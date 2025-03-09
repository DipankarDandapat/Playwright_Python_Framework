import pytest
from pages.facebook_login_page import FacebookLoginPage
from pages.facebook_createuser_page import FacebookCreateUserPage

@pytest.fixture
def facebook_login_page(page, app_config):
    """Fixture to initialize the LoginPage."""
    return FacebookLoginPage(page, app_config)

@pytest.fixture
def facebook_createUser_page(page,app_config):
    """Fixture to initialize the createUser."""
    return FacebookCreateUserPage(page,app_config)