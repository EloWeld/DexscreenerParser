import json
import time
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from config import *
from utils import *
from web3_connector import getBurnedBalance, getBurnedPercentage, getContract, getPairBalance, getTotalSupply


class TokenValidator:
    def __init__(self, driver: WebDriver, token_data) -> None:
        self.driver = driver
        self.token = token_data

    def openToken(self):
        try:
            el = self.driver.find_element(By.XPATH, f"//a[contains(.,'{self.token['tokenName']}')]")
            ActionChains(self.driver).scroll_to_element(el)
            self.driver.execute_script("arguments[0].click();", el)
        except Exception as e:
            logger.error(str(e)+"\n"+traceback.format_exc())
            return "CANT_OPEN_TOKEN"

    def closeToken(self):
        self.driver.back()

    def checkLockedLiquidity(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, "svg.custom-19rsff")
            return True
        except Exception as e:
            return False

    def checkIssues(self):
        issues = {}
        try:
            security_dropdown_arrow = self.driver.find_element(By.XPATH, "//div[text()[contains(.,'Go+ Security')]]/parent::div/div[last()]")
            security_dropdown_arrow.click()
            self.driver.implicitly_wait(0.5)
            issues_list = self.driver.find_elements(By.XPATH, "//div[text()[contains(.,'Go+ Security')]]/parent::div/parent::div/div[last()]/div/div")
            self.driver.implicitly_wait(2)
            if issues_list:
                self.driver.execute_script("arguments[0].scrollIntoView();", issues_list[-1])
            else:
                logger.error("No issues list found")
                return []
            for issue in issues_list:
                label = issue.find_element(By.XPATH, './div[1]')
                value = issue.find_element(By.XPATH, './div[last()]')
                issues[label.text] = value.text

            return issues
        except Exception as e:
            logger.error(str(e)+"\n"+traceback.format_exc())
            return []

    def getPaidViewLinks(self):
        try:
            container = self.driver.find_element("//div[contains(@class, 'custom-9hvd15')]/div/div[count(a)=3 and count(button)=1]")
            self.driver.implicitly_wait(0.5)
            hrefs = [x.get_attribute('href') for x in container.find_elements(By.CSS_SELECTOR, 'a[target="_blank"]')]
            self.driver.implicitly_wait(2)
            return hrefs
        except Exception as e:
            logger.error("No paid plan")
            return []

    def getSnifferLink(self):
        try:
            sniffer_link = self.driver.find_element(By.XPATH, "//div[text()[contains(.,'Token Sniffer')]]/parent::div/a[last()]")
            self.driver.execute_script("arguments[0].scrollIntoView();", sniffer_link)
            return (sniffer_link, sniffer_link.get_attribute('href'))
        except Exception as e:
            logger.error(str(e)+"\n"+traceback.format_exc())
            return (None, None)

    def getSnifferScores(self, link_el):
        try:
            signatures = []
            link_el.click()
            self.driver.switch_to.window(self.driver.window_handles[2])
            
            self.driver.implicitly_wait(20)

            scores_span = self.driver.find_element(By.XPATH, '//h2[text()[contains(.,"Score:")]]/span')
            scores = int(scores_span.text.strip().split('/')[0]) / 100
            self.driver.implicitly_wait(0.5)
            signatures_els: list[WebElement] = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'Home_alertSection')]/ul/li")
            signatures = [x.text for x in signatures_els]
            self.driver.implicitly_wait(2)
            
            
            if "tokensniffer" in self.driver.current_url:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[1])
            
            return dict(
                scores=scores,
                signatures=signatures
            )
        except Exception as e:
            if "Score" in str(e):
                logger.error("Cant found scores")
            if "tokensniffer" in self.driver.current_url:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[1])
            if "Score" not in str(e):
                logger.error(str(e)+"\n"+traceback.format_exc())
            return dict(
                scores=0,
                signatures=[]
            )
        
    def getTokenAddress(self):
        try:
            trade_uniswap_title_el = self.driver.find_element(By.XPATH, '//button[text()="Trade on Uniswap"]/parent::div/a')
            token_address = trade_uniswap_title_el.get_attribute('href').split('/')[-1].split('&')[0].split('=')[1]

            return token_address
        except Exception as e:
            logger.error(str(e)+"\n"+traceback.format_exc())
            return None
        
        
    def getPairAddress(self):
        try:
            pair_title_el = self.driver.find_element(By.XPATH, '//span[text()="Pair"]')
            pair_title = pair_title_el.get_attribute('title')

            return pair_title
        except Exception as e:
            logger.error(str(e)+"\n"+traceback.format_exc())
            return None

def check_is_scam(driver: WebDriver, token):
    driver.implicitly_wait(2)

    validator = TokenValidator(driver, token)
    open_result = validator.openToken()
    if open_result == "CANT_OPEN_TOKEN":
        return True, "Cant open token"
    
    token_address = validator.getTokenAddress()
    pair_address = validator.getPairAddress()
    
    validator_status = {}
    validator_status['token_address'] = token_address
    validator_status['pair_address'] = token_address
    validator_status['locked_liq'] = validator.checkLockedLiquidity()
    validator_status['paid_plan_links'] = validator.getPaidViewLinks()
    
    if not validator_status['locked_liq']:
        return True, "Unlocked liquidity"
    
    validator_status['issues'] = validator.checkIssues()
    
    if validator_status['issues'] == []:
        return False, "Tokens' url broken, not ether blockchain"
    if validator_status['issues']['Open source'] == "Noe":
        return True, f"Not open source"
    if validator_status['issues'].get('Honeypot', 'Yes') == "Yes":
        return True, f"Honeypot"
    selltax: str = validator_status['issues']['Sell tax'].replace('%', '')
    buytax: str = validator_status['issues']['Buy tax'].replace('%', '')
    if (selltax.isdigit() and int(selltax) > 4) or (buytax.isdigit() and int(buytax) > 4):
        return True, f"Sell taxes or buy taxes too high or unknown"
    if validator_status['issues']['Owner can change balance'] == "Yes":
        return True, "Owner can change balance"
    if validator_status['issues']['Holder count'].isdigit() and  int(validator_status['issues']['Holder count']) < 3:
        return True, "Less than 3 holders"
    if validator_status['issues']['Ownership renounced'] == "No":
        return True, "No Ownership renounced"
    # if validator_status['issues']['Trading cooldown'] == "Yes":
    #     return True, "Trading cooldown"
    
    link_el, link_href = validator.getSnifferLink()
    validator_status['sniffer_link'] = link_href
    validator_status['sniffer_scores'] = validator.getSnifferScores(link_el) if link_el else None
    
    
    if not validator_status['sniffer_scores']:
        return True, "Not available sniffer scores"
    if validator_status['sniffer_scores']['scores'] < 0.2:
        return True, f"Sniffer scores lesser then 20%, it's {validator_status['sniffer_scores']['scores']}"
    if validator_status['sniffer_scores']['signatures']:
        return True, f"Sniffer signatures: {validator_status['sniffer_scores']['signatures']}"
    
    
    
    contract = getContract(token_address)
    validator_status['total_supply'] = getTotalSupply(token_address, contract)
    
    validator_status['pair_balance'] = getPairBalance(token_address, pair_address, contract)
    validator_status['pair_percent'] = (validator_status['pair_balance'] / validator_status['total_supply']) * 100
    
    validator_status['burned_balance'] = getBurnedBalance(pair_address, None)
    validator_status['burned_percent'] = getBurnedPercentage(pair_address)
    validator_status.update(token)
    
    if validator_status['pair_percent'] < 95:
        return True, f"Less then 95% of supply in pool, now: {validator_status['pair_percent']}"
    if validator_status['burned_percent'] < 90:
        if validator_status['burned_percent'] > 0:
            return True, f"Less then 90% of pool burned, now: {validator_status['burned_percent']}"
        logger.error("Burned balance is zero, so idk what to do")
    
    return False, str(json.dumps(validator_status, indent=4, ensure_ascii=False, default=str))
    

def go_filter(driver):
    base_url = "https://dexscreener.com/new-pairs?"
    url_params = []

    if "chains" in FILTERS:
        chains = ','.join(FILTERS['chains'])
        url_params += [f"chainIds={chains}"]
    else:
        url_params += [f"chainIds=all"]
    for fl_key, fl_value in FILTERS.items():
        if fl_key in DICT['all_filters']:
            url_params += [f"{fl_key}={fl_value}"]

    driver.get(base_url + '&'.join(url_params))
