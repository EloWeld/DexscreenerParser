
import setuptools  # Не забываем что это нужно и не просто так
import json
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging import getLogger

from config import *
from driver import create_driver
from filters import *
import loguru
# Initialize a logger for this module.
from trade import trade
from utils import *

driver: WebDriver = None


def open_dexscreener():
    driver.get("https://dexscreener.com/new-pairs")

    # Открытие новой вкладки
    driver.execute_script("window.open('https://dexscreener.com/new-pairs');")
    time.sleep(2)
    success = False
    while not success:
        try:
            # Переключение на новую вкладку
            driver.switch_to.window(driver.window_handles[1])
            success = True
        except Exception:
            logger.info("Включите всплывающие окна в браузере")


def main():
    global driver

    while True:
        try:
            driver = create_driver()

            open_dexscreener()
        except Exception as e:
            loguru.logger.error("Cant open chrome, wait...")
            time.sleep(10)
            continue

        # Wait for table is visible
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ds-dex-table.ds-dex-table-new")))

        # Add filters
        driver.implicitly_wait(30)

        # Go to filtered table page
        go_filter(driver)

        # Get all rows of tokens
        rows = driver.find_elements(By.CSS_SELECTOR, "a.ds-dex-table-row.ds-dex-table-row-new")[:]

        # Make info-dict
        unfiltered_tokens = {}
        for row in rows:
            token_data = row_to_dict(row)
            token_data["row_element"] = row
            unfiltered_tokens[f"{token_data['tokenName']}"] = token_data

        # Filted it!
        tokens = {key: value for key, value in unfiltered_tokens.items() if value['badge'] == 'V2'}
        print(f"Filtered tokens, now {len(tokens)}/{len(unfiltered_tokens)}")

        for i, (token_name, token_data) in enumerate(tokens.items()):
            t_scam_check_result, t_scam_check_msg = check_is_scam(driver, token_data)
            go_filter(driver)
            if t_scam_check_result:
                loguru.logger.error(f"{token_name} is scam, cause of: {t_scam_check_msg}")
            else:
                loguru.logger.success(f"{token_name} is not scam, data: {t_scam_check_msg}")
                with open("good_tokens.txt", 'a', encoding='utf-8') as f:
                    f.write(t_scam_check_msg+"\n")
            loguru.logger.info(f"Scanned {i}/{len(tokens)}")

        # trade(driver, rows)

        driver.close()
        driver.quit()


if __name__ == "__main__":
    main()
