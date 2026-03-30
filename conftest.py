import os
import pytest
import allure
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions

load_dotenv()


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default="https://demoqa.com")
    parser.addoption("--selenoid-url", action="store", default="https://ru.selenoid.autotests.cloud/wd/hub")
    parser.addoption("--browser", action="store", default="chrome", choices=["chrome", "firefox"])
    parser.addoption("--browser-version", action="store", default="128.0")
    parser.addoption("--headless", action="store_true", default=False)
    parser.addoption("--window-size", action="store", default="1920,1080")


@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url")


@pytest.fixture(scope="session")
def selenoid_url(request):
    raw_url = request.config.getoption("--selenoid-url")
    user = os.getenv("SELENOID_USER", "")
    password = os.getenv("SELENOID_PASSWORD", "")

    if user and password and "ru.selenoid.autotests.cloud" in raw_url:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(raw_url)
        netloc = f"{user}:{password}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
        return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
    return raw_url


@pytest.fixture(scope="session")
def browser_name(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def browser_version(request):
    return request.config.getoption("--browser-version")


@pytest.fixture(scope="session")
def headless_mode(request):
    return request.config.getoption("--headless")


@pytest.fixture(scope="session")
def window_size(request):
    return request.config.getoption("--window-size")


@pytest.fixture(scope="function")
def driver(request, selenoid_url, browser_name, browser_version, headless_mode, window_size):
    is_jenkins = 'JENKINS_URL' in os.environ or 'JENKINS_HOME' in os.environ
    use_remote = is_jenkins or "selenoid" in selenoid_url

    if browser_name == "chrome":
        chrome_options = Options()
        if headless_mode or is_jenkins:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={window_size}")

        if use_remote:
            selenoid_capabilities = {
                "browserName": "chrome",
                "browserVersion": browser_version,
                "selenoid:options": {
                    "enableVNC": True,
                    "enableVideo": True,
                    "videoName": f"{request.node.name}.mp4"
                }
            }
            chrome_options.capabilities.update(selenoid_capabilities)
            driver = webdriver.Remote(command_executor=selenoid_url, options=chrome_options)
        else:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

    elif browser_name == "firefox":
        firefox_options = FirefoxOptions()
        if headless_mode or is_jenkins:
            firefox_options.add_argument("--headless")
        firefox_options.add_argument(f"--window-size={window_size}")

        if use_remote:
            selenoid_capabilities = {
                "browserName": "firefox",
                "browserVersion": browser_version,
                "selenoid:options": {
                    "enableVNC": True,
                    "enableVideo": True,
                    "videoName": f"{request.node.name}.mp4"
                }
            }
            firefox_options.capabilities.update(selenoid_capabilities)
            driver = webdriver.Remote(command_executor=selenoid_url, options=firefox_options)
        else:
            from selenium.webdriver.firefox.service import Service
            from webdriver_manager.firefox import GeckoDriverManager
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)
    else:
        raise ValueError(f"Browser {browser_name} not supported")

    driver.implicitly_wait(10)
    driver.test_name = request.node.name
    driver.session_id = driver.session_id

    yield driver

    # ========== ВЛОЖЕНИЯ ДЛЯ ALLURE ==========

    # 1. Скриншот
    allure.attach(
        driver.get_screenshot_as_png(),
        name=f"{driver.test_name}_screenshot",
        attachment_type=allure.attachment_type.PNG
    )

    # 2. URL страницы
    allure.attach(
        driver.current_url,
        name=f"{driver.test_name}_current_url",
        attachment_type=allure.attachment_type.TEXT
    )

    # 3. Заголовок страницы
    allure.attach(
        driver.title,
        name=f"{driver.test_name}_page_title",
        attachment_type=allure.attachment_type.TEXT
    )

    # 4. Логи браузера
    try:
        browser_logs = driver.get_log('browser')
        if browser_logs:
            logs_text = '\n'.join(
                f"[{log['level']}] {log['message']}"
                for log in browser_logs
            )
            allure.attach(
                logs_text,
                name=f"{driver.test_name}_browser_logs",
                attachment_type=allure.attachment_type.TEXT
            )
        else:
            allure.attach(
                "No browser logs",
                name=f"{driver.test_name}_browser_logs",
                attachment_type=allure.attachment_type.TEXT
            )
    except Exception as e:
        allure.attach(
            f"Could not retrieve logs: {e}",
            name=f"{driver.test_name}_browser_logs_error",
            attachment_type=allure.attachment_type.TEXT
        )

    # 5. ВИДЕО — скачиваем и прикрепляем как файл
    if use_remote:
        session_id = driver.session_id
        video_url = f"https://ru.selenoid.autotests.cloud/video/{session_id}.mp4"

        try:
            response = requests.get(video_url, timeout=10)
            if response.status_code == 200:
                allure.attach(
                    response.content,
                    name=f"{driver.test_name}_video.mp4",
                    attachment_type=allure.attachment_type.MP4
                )
            else:
                allure.attach(
                    f"Video not available (HTTP {response.status_code})\nURL: {video_url}",
                    name=f"{driver.test_name}_video_error",
                    attachment_type=allure.attachment_type.TEXT
                )
        except Exception as e:
            allure.attach(
                f"Video download error: {e}\nURL: {video_url}",
                name=f"{driver.test_name}_video_error",
                attachment_type=allure.attachment_type.TEXT
            )

    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        if "driver" in item.fixturenames:
            driver = item.funcargs["driver"]
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"{item.name}_failure_screenshot",
                attachment_type=allure.attachment_type.PNG
            )