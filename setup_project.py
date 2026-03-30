#!/usr/bin/env python3
"""
Установочный скрипт для создания проекта qa-guru-demoqa
Запуск: python setup_project.py
"""

import os

def create_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ {path}")

def create_folder(path):
    os.makedirs(path, exist_ok=True)
    print(f"✅ {path}/")

def main():
    print("=" * 60)
    print("🚀 Создание проекта qa-guru-demoqa")
    print("=" * 60)

    # Создаем папки
    folders = ["pages", "tests", "utils"]
    for folder in folders:
        create_folder(folder)
        create_file(f"{folder}/__init__.py", "")

    # .gitignore
    create_file(".gitignore", """.venv/
__pycache__/
*.pyc
.pytest_cache/
allure-results/
allure-report/
.idea/
.vscode/
""")

    # requirements.txt
    create_file("requirements.txt", """pytest>=8.0
allure-pytest>=2.15.0
selenium>=4.39.0
webdriver-manager>=4.0.0
""")

    # pytest.ini
    create_file("pytest.ini", """[pytest]
addopts =
    --alluredir=allure-results
""")

    # utils/attach.py
    create_file("utils/attach.py", """import allure
from allure_commons.types import AttachmentType


def add_screenshot(driver):
    png = driver.get_screenshot_as_png()
    allure.attach(body=png, name='screenshot', attachment_type=AttachmentType.PNG, extension='.png')


def add_console_logs(driver):
    log = "".join(f'{text}\\n' for text in driver.execute("getLog", {'type': 'browser'})['value'])
    allure.attach(log, 'browser_logs', AttachmentType.TEXT, '.log')


def add_page_source(driver):
    html = driver.page_source
    allure.attach(html, 'page_source', AttachmentType.HTML, '.html')


def add_video(driver):
    video_url = "https://selenoid.autotests.cloud/video/" + driver.session_id + ".mp4"
    html = "<html><body><video width='100%' height='100%' controls autoplay><source src='" \\
           + video_url \\
           + "' type='video/mp4'></video></body></html>"
    allure.attach(html, 'video_' + driver.session_id, AttachmentType.HTML, '.html')
""")

    # conftest.py
    create_file("conftest.py", """import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils import attach


@pytest.fixture(scope='function')
def driver():
    options = Options()

    selenoid_capabilities = {
        "browserName": "chrome",
        "browserVersion": '128.0',
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": True
        }
    }
    options.capabilities.update(selenoid_capabilities)

    driver = webdriver.Remote(
        command_executor="https://user1:1234@selenoid.autotests.cloud/wd/hub",
        options=options
    )

    yield driver

    attach.add_screenshot(driver)
    attach.add_page_source(driver)
    attach.add_console_logs(driver)
    attach.add_video(driver)

    driver.quit()
""")

    # pages/registration_page.py
    create_file("pages/registration_page.py", """import allure
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
""")

    # tests/test_registration.py
    create_file("tests/test_registration.py", """import allure
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
""")

    print("\n" + "=" * 60)
    print("✅ Проект qa-guru-demoqa успешно создан!")
    print("=" * 60)
    print("\n📌 Следующие шаги:")
    print("1. Создайте виртуальное окружение: python -m venv .venv")
    print("2. Активируйте его: .venv\\Scripts\\activate (Windows) или source .venv/bin/activate (Linux/Mac)")
    print("3. Установите зависимости: pip install -r requirements.txt")
    print("4. Запустите тест: pytest tests/ -v")
    print("5. Сгенерируйте Allure отчет: allure generate allure-results -o allure-report --clean")
    print("6. Откройте отчет: allure open allure-report")
    print("\n🔧 Запуск с параметрами (если нужно):")
    print("pytest tests/ -v --browser=firefox --headless=True")
    print("=" * 60)

if __name__ == "__main__":
    main()