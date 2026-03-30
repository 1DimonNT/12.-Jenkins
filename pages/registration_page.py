import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RegistrationPage:
    URL = "https://demoqa.com/automation-practice-form"

    FIRST_NAME = (By.ID, "firstName")
    LAST_NAME = (By.ID, "lastName")
    EMAIL = (By.ID, "userEmail")
    GENDER_MALE = (By.CSS_SELECTOR, "label[for='gender-radio-1']")
    MOBILE = (By.ID, "userNumber")
    ADDRESS = (By.ID, "currentAddress")
    STATE = (By.ID, "state")
    CITY = (By.ID, "city")
    SUBMIT = (By.ID, "submit")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    @allure.step("Open registration form")
    def open(self):
        self.driver.get(self.URL)
        wrapper = self.driver.find_element(By.CSS_SELECTOR, ".practice-form-wrapper")
        assert "Student Registration Form" in wrapper.text
        self.driver.execute_script("document.querySelector('footer')?.remove()")
        self.driver.execute_script("document.getElementById('fixedban')?.remove()")
        return self

    @allure.step("Fill first name: {first_name}")
    def fill_first_name(self, first_name):
        element = self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME))
        element.clear()
        element.send_keys(first_name)
        return self

    @allure.step("Fill last name: {last_name}")
    def fill_last_name(self, last_name):
        element = self.driver.find_element(*self.LAST_NAME)
        element.clear()
        element.send_keys(last_name)
        return self

    @allure.step("Fill email: {email}")
    def fill_email(self, email):
        element = self.driver.find_element(*self.EMAIL)
        element.clear()
        element.send_keys(email)
        return self

    @allure.step("Select gender: Male")
    def select_male_gender(self):
        self.driver.find_element(*self.GENDER_MALE).click()
        return self

    @allure.step("Fill mobile: {mobile}")
    def fill_mobile(self, mobile):
        self.driver.find_element(*self.MOBILE).send_keys(mobile)
        return self

    @allure.step("Fill address: {address}")
    def fill_address(self, address):
        self.driver.execute_script("arguments[0].scrollIntoView(true);",
                                   self.driver.find_element(*self.ADDRESS))
        self.driver.find_element(*self.ADDRESS).send_keys(address)
        return self

    @allure.step("Select state: {state}")
    def select_state(self, state):
        element = self.driver.find_element(*self.STATE)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{state}']"))).click()
        return self

    @allure.step("Select city: {city}")
    def select_city(self, city):
        element = self.driver.find_element(*self.CITY)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{city}']"))).click()
        return self

    @allure.step("Submit form")
    def submit(self):
        submit_btn = self.driver.find_element(*self.SUBMIT)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        submit_btn.click()
        return self

    @allure.step("Verify registration success")
    def should_have_success(self):
        self.wait.until(EC.visibility_of_element_located((By.ID, "example-modal-sizes-title-lg")))
        return self