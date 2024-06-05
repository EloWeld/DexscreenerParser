# –––––––––––– Seleniumwire + undetected ––––––––––––

# from seleniumwire.undetected_chromedriver.webdriver import Chrome
# from seleniumwire.undetected_chromedriver import webdriver

# –––––––––––– Undetected ––––––––––––
import os
import shutil
from undetected_chromedriver import Chrome
import undetected_chromedriver as uc
from undetected_chromedriver.options import ChromeOptions as Options

# –––––––––––– Selenium ––––––––––––
# from selenium.webdriver import Chrome
# from selenium.webdriver.chrome.options import Options
# uc.TARGET_VERSION = 123


def create_driver(headless=True, profile_replacer=True):
    if profile_replacer:
        # Удаление папки chrome_profile, если она существует
        if os.path.exists("chrome_profile"):
            shutil.rmtree("chrome_profile")
        # Переименование папки chrome_profile copy в chrome_profile, если она существует
        if os.path.exists("chrome_profile copy"):
            os.rename("chrome_profile copy", "chrome_profile")
            # Создание копии папки chrome_profile
            shutil.copytree("chrome_profile", "chrome_profile copy")
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    geolocation = {
        "latitude": 47.123,
        "longitude": 49.123
    }

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-application-cache")
    # options.add_argument("--disable-gpu")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument('--allow-profiles-outside-user-dir')
    seleniumwire_options = {
        "disable_encoding": True,
        "verify_ssl": True
    }
    options.add_argument('--profile-directory=Default')
    options.add_argument('--user-data-dir=chrome_profile')
    # options.add_argument('--enable-profile-shortcut-manager')
    options.add_argument(f"--user-agent={user_agent}")

    # Установка геолокации (Пример: Москва)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.geolocation": 1,  # Разрешить geolocation
        "profile.default_content_setting_values.notifications": 1,  # Разрешить notification
        "geolocation": True,
    })

    # Добавляем опции для безголового режима
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")

    driver = Chrome(options=options)

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", geolocation)

    return driver
