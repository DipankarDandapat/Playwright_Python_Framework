
import json
import pathlib
import base64
import uuid

import pytest
import os
from playwright.sync_api import Playwright, Browser
from pytest_metadata.plugin import metadata_key

from utils.db.db_factory import DBFactory
from utils.logger import customLogger
from config.browser_capabilities import get_browser_capabilities  # Updated import
from config.config import Config
from datetime import datetime
log = customLogger()

# Import fixtures from the fixtures module
pytest_plugins = ["fixtures.pages"]

def pytest_configure(config):
    # Register additional metadata or initialize variables here if needed
    global pytest_html
    pytest_html = config.pluginmanager.getplugin("html")

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


# Fixture to initialize Config
@pytest.fixture(scope="session", autouse=True)
def setup_env(request):
    """Set up the environment configuration."""
    env = request.config.getoption("--env")
    os.environ["ENV"] = env  # Set the environment variable
    print(f"Running tests in {env.upper()} environment")


# Fixture to provide the Config instance
@pytest.fixture(scope="session")
def app_config():
    """Provide the Config instance initialized with the correct environment."""
    env = os.getenv("ENV", "dev")
    config = Config(env)  # Initialize Config here
    return config


# Browser fixture
@pytest.fixture(scope="session")
def browser(request, playwright: Playwright,app_config):
    global ws_endpoint
    cloud = request.config.getoption("--cloud")
    browser_name = request.config.getoption("--browser-engine")
    headless = request.config.getoption("--headless")

    if cloud == "local":
        # Get capabilities for local browser
        test_name = request.node.name
        caps = get_browser_capabilities(cloud, test_name,app_config)
        browser = playwright[browser_name].launch(headless=headless)
        yield browser
        browser.close()
    else:
        # Cloud provider setup
        test_name = request.node.name
        caps = get_browser_capabilities(cloud, test_name,app_config)

        if cloud == "browserstack":
            ws_endpoint = f"wss://cdp.browserstack.com/playwright?caps={json.dumps(caps)}"

        elif cloud == "lambdatest":
            ws_endpoint = f"wss://cdp.lambdatest.com/playwright?capabilities={caps}"

        # Connect to cloud browser
        print(f"WebSocket Endpoint: {ws_endpoint}")
        browser = playwright.chromium.connect(ws_endpoint)
        yield browser
        browser.close()



# Page fixture
@pytest.fixture(scope="function")
def page(browser: Browser, request,app_config):
    # Get capabilities for the current provider
    cloud = request.config.getoption("--cloud")
    test_name = request.node.name
    caps = get_browser_capabilities(cloud, test_name,app_config)
    context = browser.new_context(viewport=caps["viewport"])
    # context = browser.new_context(no_viewport=True)
    page = context.new_page()
    yield page
    context.close()


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




enve: str = None
def pytest_configure(config):
    global enve
    enve=config.getoption('--env')
    # Add custom metadata to the report
    config.stash[metadata_key]["Report ID"] = str(uuid.uuid4())[:8]
    config.stash[metadata_key]["Project Name"] = "Playwright Python Automation"
    config.stash[metadata_key]["Version"] = "1.0.0"
    config.stash[metadata_key]["Environment"] = enve
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

    if report.when in ('call', 'setup'):
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            page = item.funcargs.get("page", None)
            if page:
                try:
                    # Project-level screenshots folder
                    project_root = pathlib.Path().resolve()
                    screenshots_dir = project_root / "screenshots"
                    screenshots_dir.mkdir(parents=True, exist_ok=True)

                    file_name = report.nodeid.replace("::", "_").replace("/", "_") + ".png"
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
    config = Config(os.getenv("ENV", "dev"))

    # # Clean up postgresql DB
    # postgresql_db = DBFactory.get_db("postgresql")
    # postgresql_db.clean_test_data("partner_consent", "user_id='56177907'")

    # Clean up postgresql DB
    cosmos_db = DBFactory.get_db(config.DBUSE)
    cosmos_db.clean_test_data(config.COSMOS_DB_CONTAINER, "email='d@gmail.com'")
