import time
import pytest
from faker import Faker
from utils.file_reader import read_file

testcasedata = read_file("facebook",'facebook_createuser_data.json')
fake = Faker()

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize("case", testcasedata["positive"])
def test_valid_createUser(facebook_createUser_page,case):
    facebook_createUser_page.navigate_to_facebook()
    facebook_createUser_page.click_createUserButton()
    facebook_createUser_page.registerNewuser(first_name=case["firstname"],last_name=case["lastname"],day=case["day"],month=case["month"],year=case["year"],mobile_number=case["mobileNumber"],new_password=case["newPassword"])
    time.sleep(5)
    facebook_createUser_page.clickSignupButton()


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize("case", testcasedata["negative"])
def test_invalid_createUser(facebook_createUser_page,case):
    facebook_createUser_page.navigate_to_facebook()
    facebook_createUser_page.click_createUserButton()

    case["firstname"]=fake.first_name()
    case["lastname"]=fake.last_name()
    case["mobileNumber"]=fake.phone_number()

    facebook_createUser_page.registerNewuser(first_name=case["firstname"],last_name=case["lastname"],day=case["day"],month=case["month"],year=case["year"],mobile_number=case["mobileNumber"],new_password=case["newPassword"])
    time.sleep(5)
    facebook_createUser_page.clickSignupButton()
