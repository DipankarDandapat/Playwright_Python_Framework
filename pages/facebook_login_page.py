import os

from playwright.sync_api import Page
from .base_page import BasePage


class FacebookLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)


    def navigate_to_facebook(self):
        """Navigate to the login page."""
        self.page.goto(os.getenv("FACEBOOK_BASE_URL"))

    def enter_credentials(self, emailid: str, password: str):
        """Enter email id and password."""
        self.enter_text("email", emailid)
        self.enter_text("password", password)

    def click_loginbutto(self):
        """Click the login button."""
        self.click("loginButton")

