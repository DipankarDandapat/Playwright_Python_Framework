import os


def get_browser_capabilities(provider: str, test_name: str) -> dict:
    """Get browser capabilities for both cloud and local browsers."""
    base_caps = {
        "name": test_name,
        "build": "Playwright Build",
        "project": "Playwright Automation",
    }

    if provider == "browserstack":
        return {
            **base_caps,
            "browserName": "chrome",
            "os": "Windows",
            "osVersion": "11",
            "browserVersion": "latest",
            "client.playwrightVersion": "1.42.0",
            "browserstack.username": os.getenv("BROWSERSTACK_USERNAME"),
            "browserstack.accessKey": os.getenv("BROWSERSTACK_ACCESS_KEY"),
            "viewport": {"width": 1920, "height": 1080}

        }
    elif provider == "lambdatest":
        return {
            **base_caps,
            "platform": "Windows 11",
            "browserName": "Chrome",
            "version": "latest",
            "selenium_version": "4.8.0",
            "pw:version": "1.42.0",
            "LT_USERNAME":os.getenv("LT_USERNAME"),
            "LT_ACCESS_KEY":os.getenv("LT_ACCESS_KEY"),
            "viewport": {"width": 1920, "height": 1080}
        }
    elif provider == "local":
        return {
            **base_caps,
            "viewport": {"width": 1920, "height": 1080}  # Default resolution for local browsers
        }
    return {}