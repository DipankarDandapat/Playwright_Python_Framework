from playwright.sync_api import Page
import logging

logger = logging.getLogger(__name__)

def click(page: Page, locator: str, element_name: str = "Element"):
    logger.info(f"Clicking on {element_name}")
    page.locator(locator).click()

def enter_text(page: Page, locator: str, text: str, element_name: str = "Element"):
    logger.info(f"Entering '{text}' in {element_name}")
    page.locator(locator).fill(text)

def select_dropdown(page: Page, locator: str, value: str, element_name: str = "Element"):
    logger.info(f"Selecting '{value}' from {element_name}")
    page.locator(locator).select_option(value)

def wait_for_element(page: Page, locator: str, timeout=10000):
    page.wait_for_selector(locator, timeout=timeout)