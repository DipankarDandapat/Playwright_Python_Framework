def get_browser_capabilities(provider: str, test_name: str, app_config) -> dict:
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
            "browserstack.username": app_config.browserstack_username,
            "browserstack.accessKey": app_config.browserstack_access_key,
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
            "LT_USERNAME":app_config.lambdatest_username,
            "LT_ACCESS_KEY":app_config.lambdatest_access_key,
            "viewport": {"width": 1920, "height": 1080}
        }
    elif provider == "local":
        return {
            **base_caps,
            "viewport": {"width": 1920, "height": 1080}  # Default resolution for local browsers
        }
    return {}