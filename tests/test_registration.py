import allure
from pages.registration_page import RegistrationPage


@allure.title("Successful fill form")
def test_successful(driver):
    registration_page = RegistrationPage(driver)

    with allure.step("Open registration form"):
        registration_page.open()

    with allure.step("Fill form"):
        (registration_page
         .fill_first_name("Alex")
         .fill_last_name("Egorov")
         .fill_email("alex@egorov.com")
         .select_male_gender()
         .fill_mobile("1234567890")
         .fill_address("Some street 1")
         .select_state("NCR")
         .select_city("Delhi")
         .submit())

    with allure.step("Check form results"):
        registration_page.should_have_success()