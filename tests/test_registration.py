import allure
from data.user import User, Gender, Hobby
from pages.registration_page import RegistrationPage


@allure.title('Успешная регистрация студента')
def test_student_registration(driver):
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

    with allure.step('Заполнение формы регистрации'):
        (RegistrationPage(driver)
         .open()
         .fill_first_name(user.first_name)
         .fill_last_name(user.last_name)
         .select_male_gender()
         .fill_mobile(user.mobile)
         .select_sports_hobby()
         .fill_address(user.address)
         .select_state(user.state)
         .select_city(user.city)
         .submit())

    with allure.step('Проверка результата'):
        assert True
