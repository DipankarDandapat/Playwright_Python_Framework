import os
import time

from playwright.sync_api import Page
from .base_page import BasePage


class FacebookCreateUserPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)


    def navigate_to_facebook(self):
        """Navigate to the login page."""
        self.page.goto(os.getenv("FACEBOOK_BASE_URL"))

    def click_createUserButton(self):
        """Click the createUser Button"""

        self.click("createUserbutton")
        # time.sleep(5)
        # self.click("firstname")
        # time.sleep(4)
        # self.click("female")
        # time.sleep(4)
        # self.enter_text("Newpassword","fdggffgfg")
        # time.sleep(4)
        # self.select_dropdown("day","30")

    def click_firstname(self):
        self.click("firstname")

    def enter_firstname(self,first_name):
        self.enter_text("firstname",first_name)

    def click_lastname(self):
        self.click("lastname")

    def enter_lastname(self, last_name):
        self.enter_text("lastname", last_name)

    def selectDay(self,day):
        self.select_dropdown("day", day)

    def selectmonth(self,month):
        self.select_dropdown("month", month)

    def selectyest(self, year):
        self.select_dropdown("year", year)

    def selectgender(self):
        self.click("female")

    def click_mobile(self):
        self.click("mobile")

    def enter_mobile(self, mobile_number):
        self.enter_text("mobile", mobile_number)

    def click_password(self):
        self.click("Newpassword")

    def enter_password(self, new_password):
        self.enter_text("Newpassword", new_password)

    def clickSignupButton(self):
        self.click("signUpButton")


    def registerNewuser(self,first_name,last_name,day,month,year,mobile_number,new_password):
        self.click_firstname()
        self.enter_firstname(first_name)
        self.click_lastname()
        self.enter_lastname(last_name)
        self.selectDay(day)
        self.selectmonth(month)
        self.selectyest(year)
        self.selectgender()
        self.click_mobile()
        self.enter_mobile(mobile_number)
        self.click_password()
        self.enter_password(new_password)