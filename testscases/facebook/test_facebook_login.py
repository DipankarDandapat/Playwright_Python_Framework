import time
import pytest
from faker import Faker
from utils.file_reader import read_file

testcasedata = read_file("facebook",'facebook_login_data.json')
fake = Faker()

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize("case", testcasedata["positive"])
def test_valid_login(facebook_login_page,case):
    facebook_login_page.navigate_to_facebook()
    facebook_login_page.enter_credentials(case["usename"], case["password"])
    facebook_login_page.click_loginbutto()
    time.sleep(5)

@pytest.mark.flaky(reruns=3)
@pytest.mark.e2e
@pytest.mark.parametrize("case", testcasedata["negative"])
def test_Invalid_login(facebook_login_page,case):

    email = fake.email()
    password=fake.password()

    case["usename"] = email
    case["password"]=password

    facebook_login_page.navigate_to_facebook()
    facebook_login_page.enter_credentials(case["usename"], case["password"] )
    facebook_login_page.click_loginbutto()
    time.sleep(5)