
import setuptools # Не забываем что это нужно и не просто так
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

# Initialize a logger for this module.
from trade import trade
from utils import *

driver: WebDriver = None

def open_dexscreener():
    driver.get("https://dexscreener.com/new-pairs")

    # Открытие новой вкладки
    driver.execute_script("window.open('https://dexscreener.com/new-pairs');")
    time.sleep(3)

    # # Переключение на новую вкладку
    driver.switch_to.window(driver.window_handles[1])


def main():
    global driver
    driver = create_driver()
    
    open_dexscreener()
    
    # Wait for table is visible
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ds-dex-table.ds-dex-table-new")))
    
    # Add filters
    driver.implicitly_wait(30)

    go_filter(driver)

    rows = driver.find_elements(By.CSS_SELECTOR, "a.ds-dex-table-row.ds-dex-table-row-new")[:]
    tokens = {}
        # print('iter')

    for row in rows:
        row_data_dict = row_to_dict(row)
        if not row_data_dict:
            continue
        tokens[f"{row_data_dict['tokenName']}"] = row_data_dict

    with open("tokens.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(tokens, indent=4, default=str, ensure_ascii=False))

        
    trade(driver, rows)
                    

    driver.close()
    driver.quit()
    

if __name__ == "__main__":
    main()
