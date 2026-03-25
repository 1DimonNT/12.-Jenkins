import os
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="function")
def driver(request):
    """Фикстура для создания и закрытия драйвера через Selenoid с видео"""
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

        # Настройки Selenoid с видео
        selenoid_capabilities = {
            "browserName": "chrome",
            "browserVersion": "128.0",  # Используем доступную версию
            "selenoid:options": {
                "enableVNC": True,  # Включает удаленный доступ для отладки
                "enableVideo": True,  # Включает запись видео
                "videoName": f"{request.node.name}.mp4"
            }
        }
        chrome_options.capabilities.update(selenoid_capabilities)

        # Правильный URL Selenoid из вашего окружения
        selenoid_url = "https://ru.selenoid.autotests.cloud/wd/hub"

        driver = webdriver.Remote(
            command_executor=selenoid_url,
            options=chrome_options
        )
    else:
        # Локальный запуск (для разработки)
        chrome_options.add_argument("--start-maximized")
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.implicitly_wait(10)

    # Сохраняем имя теста и сессию
    driver.test_name = request.node.name
    driver.session_id = driver.session_id

    yield driver

    # Добавляем скриншот
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

    # Добавляем ссылку на видео из Selenoid
    if is_jenkins:
        video_url = f"https://ru.selenoid.autotests.cloud/video/{driver.session_id}.mp4"
        allure.attach(
            video_url,
            name=f"{driver.test_name}_video_link",
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