import json
import pathlib
import base64
import uuid
import pytest
import os
from playwright.sync_api import Playwright, Browser
from pytest_metadata.plugin import metadata_key
from dotenv import load_dotenv
from pathlib import Path
from utils.logger import customLogger
from config.browser_capabilities import get_browser_capabilities
from utils.db.db_factory import DBFactory
from datetime import datetime

log = customLogger()

# Import fixtures from the fixtures module
pytest_plugins = ["fixtures.pages"]

# Add a dictionary to track test retries
test_retries = {}


# Define command-line options
def pytest_addoption(parser):
    parser.addoption(
        "--cloud",
        action="store",
        choices=["local", "browserstack", "lambdatest"],
        default="local",
        help="Cloud provider: local|browserstack|lambdatest"
    )
    parser.addoption(
        "--browser-engine",
        action="store",
        default="chromium",
        choices=["chromium", "firefox", "webkit"],
        help="Browser engine: chromium|firefox|webkit"
    )
    parser.addoption(
        "--headless",
        action="store",
        type=lambda x: str(x).lower() == 'true',
        default=True,
        help="Run in headless mode: true|false"
    )
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        choices=["dev", "qa", "prod"],
        help="Environment: dev|qa|prod"
    )
    parser.addoption(
        "--retries",
        action="store",
        default=0,
        type=int,
        help="Number of times to retry failed tests after session"
    )


@pytest.fixture(scope="session", autouse=True)
def load_env(request):
    env = request.config.getoption("--env").lower()
    project_root = Path(__file__).parent.parent
    env_file = project_root / "config" / "environments" / f".env.{env}"

    if not env_file.exists():
        pytest.exit(f"Environment file not found: {env_file}")

    load_dotenv(env_file, override=True)  # override=True to be safe
    os.environ["ENV"] = env
    print(os.environ["ENV"])


# Browser fixture
@pytest.fixture(scope="session")
def browser(request, playwright: Playwright):
    global ws_endpoint
    cloud = request.config.getoption("--cloud")
    browser_name = request.config.getoption("--browser-engine")
    headless = request.config.getoption("--headless")

    if cloud == "local":
        test_name = request.node.name
        caps = get_browser_capabilities(cloud, test_name)
        browser = playwright[browser_name].launch(headless=headless)
        yield browser
        browser.close()
    else:
        test_name = request.node.name
        caps = get_browser_capabilities(cloud, test_name)

        if cloud == "browserstack":
            ws_endpoint = f"wss://cdp.browserstack.com/playwright?caps={json.dumps(caps)}"
        elif cloud == "lambdatest":
            ws_endpoint = f"wss://cdp.lambdatest.com/playwright?capabilities={caps}"

        print(f"WebSocket Endpoint: {ws_endpoint}")
        browser = playwright.chromium.connect(ws_endpoint)
        yield browser
        browser.close()


# Page fixture
@pytest.fixture(scope="function")
def page(browser: Browser, request):
    cloud = request.config.getoption("--cloud")
    test_name = request.node.name
    caps = get_browser_capabilities(cloud, test_name)
    context = browser.new_context(viewport=caps["viewport"])
    page = context.new_page()
    yield page
    context.close()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):

    log.info(f"Testcase.....{item.name}.....Start now ..........................................................")


def pytest_runtest_teardown(item):
    log.info(f"Testcase.....{item.name}.....End now ............................................................")


@pytest.hookimpl(optionalhook=True)
def pytest_metadata(metadata):
    metadata.pop("Platform", None)
    metadata.pop("Packages", None)
    metadata.pop("Plugins", None)
    metadata.pop("JAVA_HOME", None)
    metadata.pop("Base URL", None)


def pytest_configure(config):
    pytest_html = config.pluginmanager.getplugin("html")
    config.stash[metadata_key]["Report ID"] = str(uuid.uuid4())[:8]
    config.stash[metadata_key]["Project Name"] = "Playwright Python Automation"
    config.stash[metadata_key]["Version"] = "1.0.0"
    config.stash[metadata_key]["Execution Time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    config.stash[metadata_key]["Author"] = "Dipankar"


def pytest_html_report_title(report):
    report.title = "Playwright Python Automation HTML Report"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    # Initialize retry count for the test if not exists
    if item.nodeid not in test_retries:
        test_retries[item.nodeid] = {
            'retries': 0,
            'status': []
        }

    # Only track status for 'call' phase (actual test execution)
    if report.when == 'call':
        # Track the status of each attempt
        test_retries[item.nodeid]['status'].append(report.outcome)

        # 🔹 Attach retry count to the report so it shows in HTML
        report.retry_count = test_retries[item.nodeid]['retries']

        print(f"Test {item.nodeid} - Attempt {test_retries[item.nodeid]['retries'] + 1}: {report.outcome}")

    if report.when in ('call', 'setup'):
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            page = item.funcargs.get("page", None)
            if page:
                try:
                    project_root = pathlib.Path().resolve()
                    screenshots_dir = project_root / "screenshots"
                    screenshots_dir.mkdir(parents=True, exist_ok=True)

                    file_name = f"{report.nodeid.replace('::', '_').replace('/', '_')}_attempt_{test_retries[item.nodeid]['retries'] + 1}.png"
                    screenshot_path = screenshots_dir / file_name

                    page.screenshot(path=str(screenshot_path), full_page=True)

                    with open(screenshot_path, "rb") as f:
                        encoded_image = base64.b64encode(f.read()).decode("utf-8")
                        html = (
                            f'<div><img src="data:image/png;base64,{encoded_image}" '
                            f'style="width:400px;height:auto;" '
                            f'onclick="window.open(this.src)" align="right"/></div>'
                        )
                        extra.append(pytest_html.extras.html(html))
                except Exception as e:
                    print(f"Screenshot capture failed: {e}")

        report.extras = extra


def pytest_sessionfinish(session, exitstatus):
    retry_count = session.config.getoption("--retries")
    if retry_count < 1:
        return

    # Collect failed tests
    failed_tests = []
    for item in session.items:
        if item.nodeid in test_retries:
            # Check if the test has any failed attempts and the last status is failed
            if 'failed' in test_retries[item.nodeid]['status'] and test_retries[item.nodeid]['status'][-1] == 'failed':
                failed_tests.append(item)

    if not failed_tests:
        return

    print(f"Retrying {len(failed_tests)} failed test(s) up to {retry_count} time(s)...")

    for item in failed_tests:
        # keep retrying until pass or hit retry_count
        while test_retries[item.nodeid]['retries'] < retry_count:
            test_retries[item.nodeid]['retries'] += 1
            attempt = test_retries[item.nodeid]['retries']
            print(f"\nRetry #{attempt} for {item.nodeid}")

            # Store the status count before retry to check for new results
            status_count_before = len(test_retries[item.nodeid]['status'])

            # Execute the test again
            item.config.hook.pytest_runtest_protocol(item=item, nextitem=None)

            # Wait for the status to be updated and check if we have a new result
            status_count_after = len(test_retries[item.nodeid]['status'])

            # If we have a new status entry and it's passed, stop retrying
            if status_count_after > status_count_before:
                latest_status = test_retries[item.nodeid]['status'][-1]
                print(f"Latest status for {item.nodeid}: {latest_status}")

                if latest_status == "passed":
                    print(f"{item.nodeid} passed on retry #{attempt}")
                    break
                else:
                    print(f" {item.nodeid} failed on retry #{attempt}")
            else:
                print(f" No status update detected for {item.nodeid} on retry #{attempt}")

        # Final status check after all retries
        if test_retries[item.nodeid]['retries'] >= retry_count:
            final_status = test_retries[item.nodeid]['status'][-1] if test_retries[item.nodeid]['status'] else 'unknown'
            if final_status != "passed":
                print(f" {item.nodeid} failed after {retry_count} retries. Final status: {final_status}")


@pytest.hookimpl(trylast=True)
def pytest_html_results_table_row(report, cells):
    retry_count = getattr(report, "retry_count", 0)

    if hasattr(report, "retry_count"):
        cells.insert(2, f'<td class="col-retries">{retry_count}</td>')
    else:
        cells.insert(2, '<td class="col-retries">0</td>')


@pytest.hookimpl(trylast=True)
def pytest_html_results_table_header(cells):
    cells.insert(2, '<th class="sortable col-retries" data-column-type="retries">Retries</th>')


def pytest_sessionfinish(session, exitstatus):
    retry_count = session.config.getoption("--retries")
    if retry_count < 1:
        return

    # Collect failed tests
    failed_tests = []
    for item in session.items:
        if item.nodeid in test_retries:
            if 'failed' in test_retries[item.nodeid]['status']:
                failed_tests.append(item)

    if not failed_tests:
        return

    print(f"\nRetrying {len(failed_tests)} failed test(s) up to {retry_count} time(s)...")

    for item in failed_tests:
        # keep retrying until pass or hit retry_count
        while test_retries[item.nodeid]['retries'] < retry_count:
            attempt = test_retries[item.nodeid]['retries'] + 1
            print(f"\nRetry #{attempt} for {item.nodeid}")

            # Execute the test again
            item.config.hook.pytest_runtest_protocol(item=item, nextitem=None)

            # Update retry counter
            test_retries[item.nodeid]['retries'] += 1

            # If test passed, stop retrying this one
            if test_retries[item.nodeid]['status'][-1] == "passed":
                print(f" {item.nodeid} passed on retry #{attempt}")
                break




_test_data_store = []

@pytest.fixture(autouse=True)
def track_and_clean_test_data(request):
    """Tracks test data and cleans it up after each test."""

    yield  # Run the test first

    # Skip DB connection if no test data registered
    if not _test_data_store:
        return

    dbuse = os.getenv("DBUSE")
    if not dbuse:
        print("Skipping DB cleanup: no DBUSE configured")
        return

    try:
        cosmos_db = DBFactory.get_db(dbuse)
        for container_name, condition in _test_data_store:
            existing_data = cosmos_db.execute_query(
                f"SELECT * FROM c WHERE {condition}",
                container_name=container_name
            )

            if existing_data:
                cosmos_db.clean_test_data(container_name, condition)
                print(f"Deleted {len(existing_data)} records from {container_name}")
            else:
                print(f"No data matching '{condition}' in {container_name}")
    except Exception as e:
        print(f" DB cleanup skipped due to error: {e}")

    _test_data_store.clear()



# Helper function to register data for cleanup
def add_for_cleanup(table_name: str, condition: str):
    _test_data_store.append((table_name, condition))