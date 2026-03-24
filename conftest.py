import os
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="function")
def driver():
    """Фикстура для создания и закрытия драйвера через Selenoid"""
    chrome_options = Options()

    # Проверяем, запущены ли тесты в Jenkins
    is_jenkins = 'JENKINS_URL' in os.environ or 'JENKINS_HOME' in os.environ

    if is_jenkins:
        # Настройки для Jenkins (headless режим)
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Используем Selenoid (Selenium Grid)
        # URL Selenoid (обычно доступен внутри Docker сети)
        selenoid_url = os.environ.get('SELENOID_URL', 'http://selenoid:4444/wd/hub')

        driver = webdriver.Remote(
            command_executor=selenoid_url,
            options=chrome_options
        )
    else:
        # Локальный запуск
        chrome_options.add_argument("--start-maximized")
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

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