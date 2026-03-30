from utils import attach

print("Import OK")

# Создаем фейк-драйвер с session_id
class FakeDriver:
    session_id = "test123"

driver = FakeDriver()
attach.add_video(driver)
print("Done")