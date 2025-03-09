from playwright.sync_api import Page, expect
from typing import Optional

class WaitStrategies:
    @staticmethod
    def for_network_idle(page: Page, timeout: float = 30000):
        page.wait_for_load_state("networkidle", timeout=timeout)

    @staticmethod
    def for_element_contains_text(page: Page, locator: str, text: str, timeout: float = 30000):
        expect(page.locator(locator)).to_contain_text(text, timeout=timeout)

    @staticmethod
    def for_element_count(page: Page, locator: str, count: int, timeout: float = 30000):
        expect(page.locator(locator)).to_have_count(count, timeout=timeout)