from playwright.sync_api import Page, expect, Locator
import logging
from typing import Dict, Any, List, Union, Optional
import json
from pathlib import Path
import re

from utils.logger import customLogger

log = customLogger()

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.elements: Dict[str, Any] = {}
        self._load_elements()


    def _load_elements(self):
        """Load elements from JSON file based on the page name."""
        page_name = self.__class__.__name__.lower().replace("page", "")
        element_file = Path(__file__).parent.parent / "elements" / f"{page_name}_page.json"

        if not element_file.exists():
            error_msg = f"Element file not found: {element_file}"
            log.error(error_msg)
            raise FileNotFoundError(error_msg)

        with open(element_file) as f:
            self.elements = json.load(f)
        log.info(f"Loaded elements from: {element_file}")

    def _get_locator(self, element_key: str) -> Any:
        """Get the locator based on the element key and its type."""
        if element_key not in self.elements:
            error_msg = f"Element '{element_key}' not found in page elements"
            log.error(error_msg)
            raise KeyError(error_msg)

        locator_info = self.elements[element_key]

        if isinstance(locator_info, dict):
            # Handle locator with type and value
            locator_type = locator_info.get("type", "css")

            if locator_type == "testid":
                return self.page.get_by_test_id(locator_info["value"])
            elif locator_type == "role":
                role = locator_info.get("role")
                name = locator_info.get("value")
                if not role or not name:
                    error_msg = f"Both 'role' and 'name' must be provided for locator type 'role'"
                    log.error(error_msg)
                    raise ValueError(error_msg)
                return self.page.get_by_role(role, name=name)
            elif locator_type == "text":
                return self.page.get_by_text(locator_info["value"])
            elif locator_type == "label":
                return self.page.get_by_label(locator_info["value"])
            elif locator_type == "title":
                return self.page.get_by_title(locator_info["value"])
            elif locator_type == "alt":
                return self.page.get_by_alt_text(locator_info["value"])
            elif locator_type == "placeholder":
                return self.page.get_by_placeholder(locator_info["value"])
            else:
                # Default to CSS/xpath selector
                return self.page.locator(locator_info["value"])
        else:
            # Default to CSS selector for backward compatibility
            return self.page.locator(locator_info)

    def wait_for_element_visible(self, element_key: str, timeout: int = 10000):
        """Wait for an element to be visible."""
        locator = self._get_locator(element_key)
        log.info(f"Waiting for element '{element_key}' to be visible")
        expect(locator).to_be_visible(timeout=timeout)

    def wait_for_element_clickable(self, element_key: str, timeout: int = 10000):
        """Wait for an element to be clickable."""
        locator = self._get_locator(element_key)
        log.info(f"Waiting for element '{element_key}' to be clickable")
        expect(locator).to_be_enabled(timeout=timeout)

    def click(self, element_key: str):
        """Click an element with built-in waits."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        self.wait_for_element_clickable(element_key)
        log.info(f"Clicking on '{element_key}'")
        locator.click()

    def enter_text(self, element_key: str, text: str):
        """Enter text into a field with validation."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Entering text '{text}' in '{element_key}'")
        locator.fill(text)

    def select_dropdown(self, element_key: str, value: str):
        """Select an option from a dropdown."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Selecting '{value}' from '{element_key}'")
        locator.select_option(value)

    def wait_for_network_idle(self, timeout: int = 30000):
        """Wait for the network to be idle."""
        log.info("Waiting for network to be idle")
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    def take_screenshot(self, name: str):
        """Take a screenshot and save it to the reports folder."""
        screenshot_path = Path(__file__).parent.parent / "reports" / f"{name}.png"
        self.page.screenshot(path=screenshot_path)
        log.info(f"Screenshot saved: {screenshot_path}")

    def verify_text(self, element_key: str, expected_text: str):
        """Verify that an element contains the expected text."""
        locator = self._get_locator(element_key)
        log.info(f"Verifying text in '{element_key}'")
        expect(locator).to_have_text(expected_text)

    def verify_element_count(self, element_key: str, expected_count: int):
        """Verify that the number of elements matches the expected count."""
        locator = self._get_locator(element_key)
        log.info(f"Verifying count of '{element_key}'")
        expect(locator).to_have_count(expected_count)

    def check_checkbox(self, element_key: str):
        """Check a checkbox or radio button."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Checking checkbox/radio: '{element_key}'")
        locator.check()

    def uncheck_checkbox(self, element_key: str):
        """Uncheck a checkbox."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Unchecking checkbox: '{element_key}'")
        locator.uncheck()

    def select_option(self, element_key: str, values: Union[str, List[str]]):
        """Select option(s) in a dropdown."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Selecting option(s) '{values}' in '{element_key}'")
        locator.select_option(values)

    def double_click(self, element_key: str):
        """Double click an element."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Double clicking: '{element_key}'")
        locator.dblclick()

    def right_click(self, element_key: str):
        """Right click an element."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Right clicking: '{element_key}'")
        locator.click(button="right")

    def press_key(self, element_key: str, key: str):
        """Press specific keyboard key on element."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Pressing key '{key}' on: '{element_key}'")
        locator.press(key)

    def upload_file(self, element_key: str, files: Union[str, List[str]]):
        """Upload file(s) to file input."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Uploading files '{files}' to: '{element_key}'")
        locator.set_input_files(files)

    def focus_element(self, element_key: str):
        """Focus on specified element."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Focusing on: '{element_key}'")
        locator.focus()

    def hover_element(self, element_key: str):
        """Hover mouse over element."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Hovering over: '{element_key}'")
        locator.hover()

    def drag_and_drop(self, source_key: str, target_key: str):
        """Drag element to target location."""
        source_locator = self._get_locator(source_key)
        target_locator = self._get_locator(target_key)
        self.wait_for_element_visible(source_key)
        self.wait_for_element_visible(target_key)
        log.info(f"Dragging '{source_key}' to '{target_key}'")
        source_locator.drag_to(target_locator)

    def scroll_to_element(self, element_key: str):
        """Scroll element into view."""
        locator = self._get_locator(element_key)
        log.info(f"Scrolling to: '{element_key}'")
        locator.scroll_into_view_if_needed()

    def clear_input(self, element_key: str):
        """Clear input field content."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Clearing input: '{element_key}'")
        locator.clear()

    def get_text_content(self, element_key: str) -> str:
        """Get text content of element."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Getting text from: '{element_key}'")
        return locator.text_content()

    def force_click(self, element_key: str):
        """Force click element bypassing actionability checks."""
        locator = self._get_locator(element_key)
        log.warning(f"Force clicking: '{element_key}'")
        locator.click(force=True)

    def type_text(self, element_key: str, text: str, delay: int = None):
        """Type text character by character with optional delay."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Typing text '{text}' in: '{element_key}'")
        locator.press_sequentially(text, delay=delay)

    def is_checked(self, element_key: str) -> bool:
        """Check if checkbox/radio is checked."""
        locator = self._get_locator(element_key)
        self.wait_for_element_visible(element_key)
        log.info(f"Checking if '{element_key}' is checked")
        return locator.is_checked()

    def is_visible(self, element_key: str) -> bool:
        """Check if element is visible."""
        locator = self._get_locator(element_key)
        log.info(f"Checking if '{element_key}' is visible")
        return locator.is_visible()

    def is_enabled(self, element_key: str) -> bool:
        """Check if element is enabled."""
        locator = self._get_locator(element_key)
        log.info(f"Checking if '{element_key}' is enabled")
        return locator.is_enabled()

    def filter_by_text(self, element_key: str, text: Union[str, re.Pattern], strict: bool = True) -> Locator:
        """Filter elements by text content."""
        locator = self._get_locator(element_key)
        filtered = locator.filter(has_text=text)
        self._handle_strictness(filtered, f"Elements filtered by text '{text}'", strict)
        return filtered

    def filter_by_child(self, parent_key: str, child_locator: Union[str, Locator], strict: bool = True) -> Locator:
        """Filter parent elements containing specific child."""
        parent_locator = self._get_locator(parent_key)
        if isinstance(child_locator, str):
            child_locator = self._get_locator(child_locator)
        filtered = parent_locator.filter(has=child_locator)
        self._handle_strictness(filtered, f"Elements filtered by child", strict)
        return filtered

    def get_list_items(self, list_key: str) -> List[Locator]:
        """Get all elements in a list."""
        locator = self._get_locator(list_key)
        log.info(f"Getting all items in list: '{list_key}'")
        return locator.all()

    def click_list_item_by_text(self, list_key: str, text: str, button_key: Optional[str] = None):
        """Click specific item in a list based on text."""
        locator = self._get_locator(list_key)
        target_item = locator.filter(has_text=text)
        if button_key:
            button_locator = self._get_locator(button_key)
            log.info(f"Clicking button '{button_key}' in list item with text '{text}'")
            target_item.locator(button_locator).click()
        else:
            log.info(f"Clicking list item with text '{text}'")
            target_item.click()

    def click_nth_element(self, element_key: str, index: int, strict: bool = True):
        """Click nth element in a list."""
        locator = self._get_locator(element_key).nth(index)
        self._handle_strictness(locator, f"{index}th element", strict)
        log.info(f"Clicking {index}th element: '{element_key}'")
        locator.click()

    def click_first_element(self, element_key: str):
        """Click first matching element."""
        locator = self._get_locator(element_key).first
        log.info(f"Clicking first element: '{element_key}'")
        locator.click()

    def click_last_element(self, element_key: str):
        """Click last matching element."""
        locator = self._get_locator(element_key).last
        log.info(f"Clicking last element: '{element_key}'")
        locator.click()

    def get_element_count(self, element_key: str) -> int:
        """Get count of matching elements."""
        locator = self._get_locator(element_key)
        log.info(f"Getting count of elements: '{element_key}'")
        return locator.count()

    def assert_list_count(self, list_key: str, expected_count: int):
        """Assert list has exact number of items."""
        locator = self._get_locator(list_key)
        log.info(f"Asserting list '{list_key}' has {expected_count} items")
        expect(locator).to_have_count(expected_count)

    def assert_list_contains_texts(self, list_key: str, expected_texts: List[str]):
        """Assert list contains exactly the specified texts."""
        locator = self._get_locator(list_key)
        actual_texts = [item.text_content() for item in locator.all()]
        log.info(f"Asserting list '{list_key}' contains texts: {expected_texts}")
        assert sorted(actual_texts) == sorted(expected_texts), \
            f"Expected texts {expected_texts} not matching actual {actual_texts}"

    def _handle_strictness(self, locator: Locator, context: str, strict: bool = True):
        """Handle strict mode checks."""
        if strict and locator.count() > 1:
            error_msg = f"Strictness violation: Multiple elements found for {context}"
            log.error(error_msg)
            raise ValueError(error_msg)