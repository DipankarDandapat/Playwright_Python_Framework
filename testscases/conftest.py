import json
import urllib

import pytest
import os
from playwright.sync_api import Playwright, Browser

import pytest
import os
from playwright.sync_api import Playwright, Browser

from utils.logger import customLogger
from config.browser_capabilities import get_browser_capabilities  # Updated import
from config.config import Config

log = customLogger()

# Import fixtures from the fixtures module
pytest_plugins = ["fixtures.pages"]


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
        action="store_true",
        default=False,
        help="Run in headless mode"
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
    context.close()  # Close the context after the test



def pytest_runtest_setup(item):
    log.info(f"Testcase.....{item.name}.....Start now ..........................................................")

def pytest_runtest_teardown(item):
    log.info(f"Testcase.....{item.name}.....End now ............................................................")
