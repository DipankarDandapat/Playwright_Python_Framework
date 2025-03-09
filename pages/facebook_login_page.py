from playwright.sync_api import Page
from .base_page import BasePage


class FacebookLoginPage(BasePage):
    def __init__(self, page: Page,app_config):
        super().__init__(page)
        self.app_config = app_config

    def navigate_to_facebook(self):
        """Navigate to the login page."""
        self.page.goto(f"{self.app_config.facebook_base_url}")

    def enter_credentials(self, emailid: str, password: str):
        """Enter email id and password."""
        self.enter_text("email", emailid)
        self.enter_text("password", password)

    def click_loginbutto(self):
        """Click the login button."""
        self.click("loginButton")

