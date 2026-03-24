import os
import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver():
    """Фикстура для создания и закрытия драйвера"""
    chrome_options = Options()

    # Проверяем, запущены ли тесты в Jenkins
    if 'JENKINS_URL' in os.environ or 'JENKINS_HOME' in os.environ:
        # Настройки для Jenkins (headless режим)
        chrome_options.add_argument("--headless=new")  # headless режим
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--remote-debugging-port=9222")
    else:
        # Локальные настройки
        chrome_options.add_argument("--start-maximized")

    # Правильный способ: используем Service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.implicitly_wait(10)

    yield driver

    # Если тест упал — делаем скриншот для Allure
    if hasattr(driver, 'test_failed') and driver.test_failed:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="screenshot",
            attachment_type=allure.attachment_type.PNG
        )

    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для отслеживания падения теста"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        if "driver" in item.fixturenames:
            driver = item.funcargs["driver"]
            driver.test_failed = True
