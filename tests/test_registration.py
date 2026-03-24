import allure
from data.user import User, Gender, Hobby
from pages.registration_page import RegistrationPage



@allure.title('Успешная регистрация студента')
@allure.description('Тест проверяет успешное заполнение формы регистрации на demoqa.com')
@allure.severity(allure.severity_level.CRITICAL)
def test_student_registration(driver):
    # Создаем тестовые данные
    user = User(
        first_name='Alex',
        last_name='Egorov',
        email='alex@egorov.com',
        gender=Gender.MALE,
        mobile='1234567890',
        birth_day=15,
        birth_month='March',
        birth_year=1995,
        subjects=['Maths'],
        hobbies=[Hobby.SPORTS],
        picture='tests/photo.jpg',
        address='Some street 1',
        state='NCR',
        city='Delhi'
    )

    # Сохраняем тестовые данные как вложение
    allure.attach(
        f"First Name: {user.first_name}\n"
        f"Last Name: {user.last_name}\n"
        f"Email: {user.email}\n"
        f"Gender: {user.gender.value}\n"
        f"Mobile: {user.mobile}\n"
        f"Address: {user.address}\n"
        f"State: {user.state}\n"
        f"City: {user.city}\n",
        name="test_data",
        attachment_type=allure.attachment_type.TEXT
    )

    with allure.step('Открыть страницу регистрации'):
        registration_page = RegistrationPage(driver)
        registration_page.open()

        # Скриншот после открытия страницы
        allure.attach(
            driver.get_screenshot_as_png(),
            name="page_opened",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step('Заполнить персональные данные'):
        registration_page.fill_first_name(user.first_name)
        registration_page.fill_last_name(user.last_name)
        registration_page.fill_email(user.email)
        registration_page.select_male_gender()
        registration_page.fill_mobile(user.mobile)

    with allure.step('Выбрать хобби'):
        registration_page.select_sports_hobby()

    with allure.step('Заполнить адрес'):
        registration_page.fill_address(user.address)

    with allure.step('Выбрать штат и город'):
        registration_page.select_state(user.state)
        registration_page.select_city(user.city)

    with allure.step('Отправить форму'):
        registration_page.submit()

        # Скриншот после отправки формы
        allure.attach(
            driver.get_screenshot_as_png(),
            name="form_submitted",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step('Проверить результат регистрации'):
        # Проверяем, что появилось модальное окно с подтверждением
        assert "Thanks for submitting the form" in driver.page_source, \
            "Не найдено сообщение об успешной регистрации"

        # Скриншот результата
        allure.attach(
            driver.get_screenshot_as_png(),
            name="registration_success",
            attachment_type=allure.attachment_type.PNG
        )
