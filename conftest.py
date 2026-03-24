import os
import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver(request):
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

        # Правильный URL Selenoid из вашего окружения
        selenoid_url = "https://ru.selenoid.autotests.cloud/wd/hub"

        driver = webdriver.Remote(
            command_executor=selenoid_url,
            options=chrome_options
        )
    else:
        # Локальный запуск (для разработки)
        chrome_options.add_argument("--start-maximized")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.implicitly_wait(10)

    # Сохраняем имя теста
    driver.test_name = request.node.name

    yield driver

    # Добавляем скриншот после теста (всегда)
    allure.attach(
        driver.get_screenshot_as_png(),
        name=f"{driver.test_name}_screenshot",
        attachment_type=allure.attachment_type.PNG
    )

    # Добавляем URL страницы
    allure.attach(
        driver.current_url,
        name=f"{driver.test_name}_current_url",
        attachment_type=allure.attachment_type.TEXT
    )

    # Добавляем заголовок страницы
    allure.attach(
        driver.title,
        name=f"{driver.test_name}_page_title",
        attachment_type=allure.attachment_type.TEXT
    )

    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для добавления скриншота при падении теста"""
    outcome = yield
    rep = outcome.get_result()

    # Если тест упал, добавляем скриншот
    if rep.when == "call" and rep.failed:
        if "driver" in item.fixturenames:
            driver = item.funcargs["driver"]
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"{item.name}_failure_screenshot",
                attachment_type=allure.attachment_type.PNG
            )
