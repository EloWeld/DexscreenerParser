# –––––––––––– Seleniumwire + undetected ––––––––––––

# from seleniumwire.undetected_chromedriver.webdriver import Chrome
# from seleniumwire.undetected_chromedriver import webdriver

# –––––––––––– Undetected ––––––––––––
from undetected_chromedriver import Chrome
import undetected_chromedriver as uc
from undetected_chromedriver.options import ChromeOptions as Options

# –––––––––––– Selenium ––––––––––––
# from selenium.webdriver import Chrome
# from selenium.webdriver.chrome.options import Options
# uc.TARGET_VERSION = 123


def create_driver():

    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    geolocation = {
        "latitude": 47.123,
        "longitude": 49.123
    }

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
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

    driver = Chrome(options=options)

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", geolocation)

    return driver