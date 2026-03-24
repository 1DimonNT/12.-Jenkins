import allure


def attach_logs(driver):
    logs = driver.get_log('browser')
    allure.attach('\n'.join(str(log) for log in logs),
                  name='browser_console_logs',
                  attachment_type=allure.attachment_type.TEXT)


def attach_video(driver):
    # Опционально: если есть интеграция с Selenoid
    pass
