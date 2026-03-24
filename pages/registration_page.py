import time

import allure
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class RegistrationPage:
    URL = "https://demoqa.com/automation-practice-form"

    # Локаторы
    FIRST_NAME = (By.ID, "firstName")
    LAST_NAME = (By.ID, "lastName")
    EMAIL = (By.ID, "userEmail")
    GENDER_MALE = (By.XPATH, "//label[text()='Male']")
    MOBILE = (By.ID, "userNumber")
    SUBJECTS_INPUT = (By.ID, "subjectsInput")
    HOBBIES_SPORTS = (By.XPATH, "//label[text()='Sports']")
    ADDRESS = (By.ID, "currentAddress")
    STATE = (By.ID, "state")
    CITY = (By.ID, "city")
    SUBMIT = (By.ID, "submit")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    @allure.step("Открыть страницу регистрации")
    def open(self):
        self.driver.get(self.URL)

        # Ждем загрузки страницы
        self.wait.until(EC.presence_of_element_located((By.ID, "firstName")))

        # Более агрессивное удаление мешающих элементов
        self.driver.execute_script("""
            // Удаляем футер
            var footer = document.querySelector('footer');
            if (footer) footer.remove();

            // Удаляем фиксированный баннер
            var fixedban = document.getElementById('fixedban');
            if (fixedban) fixedban.remove();

            // Удаляем любые модальные окна
            var modals = document.querySelectorAll('.modal, .modal.show, [role="dialog"], .ad, .ads');
            modals.forEach(function(modal) {
                modal.remove();
            });

            // Удаляем элементы с рекламными классами
            var ads = document.querySelectorAll('[class*="ad"], [id*="ad"], [class*="banner"], [id*="banner"]');
            ads.forEach(function(ad) {
                ad.remove();
            });

            // Удаляем iframe с рекламой
            var iframes = document.querySelectorAll('iframe');
            iframes.forEach(function(iframe) {
                iframe.remove();
            });

            // Убираем скроллинг для предотвращения перекрытия
            document.body.style.overflow = 'auto';
        """)

        # Небольшая пауза для применения удаления
        time.sleep(1)
        return self

    @allure.step("Заполнить имя: {first_name}")
    def fill_first_name(self, first_name):
        element = self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME))
        element.send_keys(first_name)
        return self

    @allure.step("Заполнить фамилию: {last_name}")
    def fill_last_name(self, last_name):
        self.driver.find_element(*self.LAST_NAME).send_keys(last_name)
        return self

    @allure.step("Заполнить email: {email}")
    def fill_email(self, email):
        self.driver.find_element(*self.EMAIL).send_keys(email)
        return self

    @allure.step("Выбрать пол: Мужской")
    def select_male_gender(self):
        element = self.driver.find_element(*self.GENDER_MALE)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element.click()
        return self

    @allure.step("Заполнить телефон: {mobile}")
    def fill_mobile(self, mobile):
        self.driver.find_element(*self.MOBILE).send_keys(mobile)
        return self

    @allure.step("Выбрать хобби: Спорт")
    def select_sports_hobby(self):
        element = self.driver.find_element(*self.HOBBIES_SPORTS)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)  # Небольшая пауза
        element.click()
        return self

    @allure.step("Заполнить адрес: {address}")
    def fill_address(self, address):
        element = self.driver.find_element(*self.ADDRESS)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        element.send_keys(address)
        return self

    @allure.step("Выбрать штат: {state}")
    def select_state(self, state):
        # Прокручиваем к элементу State
        element = self.driver.find_element(*self.STATE)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)

        # Пытаемся кликнуть, если перехвачено - кликаем через JS
        try:
            element.click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            # Если клик перехвачен, используем JavaScript
            self.driver.execute_script("arguments[0].click();", element)

        # Ждем появления выпадающего списка и выбираем нужный штат
        self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{state}']"))).click()
        return self

    @allure.step("Выбрать город: {city}")
    def select_city(self, city):
        # Прокручиваем к элементу City
        element = self.driver.find_element(*self.CITY)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)

        # Пытаемся кликнуть, если перехвачено - кликаем через JS
        try:
            element.click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self.driver.execute_script("arguments[0].click();", element)

        # Выбираем нужный город
        self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{city}']"))).click()
        return self

    @allure.step("Нажать кнопку Submit")
    def submit(self):
        submit_btn = self.driver.find_element(*self.SUBMIT)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        time.sleep(0.5)

        try:
            submit_btn.click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self.driver.execute_script("arguments[0].click();", submit_btn)
        return self

    @allure.step('Проверить, что регистрация успешна')
    def should_have_registered(self, user):
        modal = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'modal-content')))
        assert user.full_name in modal.text
        assert user.email in modal.text
        return self
