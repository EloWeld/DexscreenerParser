import json
import time
import loguru
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from config import *
from utils import *
from web3_connector import TokenWeb3Stats


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
                try:
                    ll = issue.find_element(By.XPATH, './div[1]').text
                except Exception as e:
                    loguru.logger.error(f"Error, cant identift label of issue, alllist: {issue.text}")
                    ll = "?"
                try:
                    vv = issue.find_element(By.XPATH, './div[last()]').text
                except Exception as e:
                    loguru.logger.error(f"Error, cant identift label of issue, alllist: {issue.text}")
                    vv = "?"
                issues[ll] = vv
            issues = {x: y for x, y in issues.items() if x not in ["Creator address", "Owner address", ""]}
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


class ScamValidator:
    def __init__(self, driver: WebDriver, filter_file='filters.json', message_file='filter_messages.json'):
        self.driver = driver
        self.load_filters(filter_file)
        self.load_messages(message_file)
        self.token_address = None
        self.pair_address = None

    def load_filters(self, filter_file):
        with open(filter_file) as f:
            self.filters = json.load(f)

    def load_messages(self, message_file):
        with open(message_file) as f:
            self.messages = json.load(f)

    def check_is_scam(self, token):
        self.token = token
        self.driver.implicitly_wait(2)
        validator = TokenValidator(self.driver, self.token)
        open_result = validator.openToken()
        if open_result == "CANT_OPEN_TOKEN":
            return True, self.messages["CANT_OPEN_TOKEN"]

        self.token_address = validator.getTokenAddress()
        self.pair_address = validator.getPairAddress()

        validator_status = {}
        validator_status['token_address'] = self.token_address
        validator_status['pair_address'] = self.pair_address
        validator_status['locked_liq'] = validator.checkLockedLiquidity()
        validator_status['paid_plan_links'] = validator.getPaidViewLinks()

        if self.filters['paid_plan_links'] == 1:
            if validator_status['paid_plan_links'] == []:
                return True, self.messages["NO_PAID_LINKS"]

        if self.filters['locked_liq'] == 1:
            if not validator_status['locked_liq']:
                return True, self.messages["UNLOCKED_LIQUIDITY"]

        validator_status['issues'] = validator.checkIssues()

        if validator_status['issues'] == []:
            return True, "Token's URL broken, not on Ether blockchain"
        if self.filters['open_source'] == 1 and validator_status['issues'].get('Open source') == "No":
            return True, self.messages["NOT_OPEN_SOURCE"]
        if self.filters['honeypot'] == 1 and validator_status['issues'].get('Honeypot', 'Yes') == "Yes":
            return True, self.messages["HONEYPOT"]

        selltax: str = validator_status['issues'].get('Sell tax', '0').replace('%', '')
        buytax: str = validator_status['issues'].get('Buy tax', '0').replace('%', '')
        if (selltax.isdigit() and int(selltax) > self.filters['max_sell_tax']):
            return True, self.messages["S_HIGH_TAX"].format(self.filters['max_sell_tax'], selltax)
        if (buytax.isdigit() and int(buytax) > self.filters['max_buy_tax']):
            return True, self.messages["B_HIGH_TAX"].format(self.filters['max_buy_tax'], buytax)

        if self.filters["owner_can_change_balance"] == 1 and validator_status['issues'].get('Owner can change balance') == "Yes":
            return True, self.messages["CHANGE_BALANCE"]
        if self.filters["ownership_renounced"] == 1 and validator_status['issues'].get('Ownership renounced') == "No":
            return True, self.messages["NO_OWNERSHIP_RENOUNCED"]

        if validator_status['issues'].get('Holder count', '0').replace(' ', '').isdigit() and int(validator_status['issues'].get('Holder count', '0').replace(' ', '')) < self.filters['min_holder_count']:
            return True, self.messages["LOW_HOLDERS"].format(self.filters['min_holder_count'], validator_status['issues'].get('Holder count', '0'))

        if self.filters["sniffer"] == 1:

            link_el, link_href = validator.getSnifferLink()
            validator_status['sniffer_link'] = link_href
            validator_status['sniffer_data'] = validator.getSnifferScores(link_el) if link_el else None

            if not validator_status['sniffer_data']:
                return True, self.messages["NO_SNIFFER_SCORES"]

            if validator_status['sniffer_data']['scores'] < self.filters['min_sniffer_score'] / 100:
                return True, self.messages["LOW_SNIFFER_SCORE"].format(self.filters['min_sniffer_score'] / 100, validator_status['sniffer_data']['scores'], )
            if self.filters['sniffer_signatures'] == 1 and validator_status['sniffer_data']['signatures']:
                return True, self.messages["SNIFFER_SIGNATURES"]

        if self.filters['web3'] == 1:
            token_analyzer = TokenWeb3Stats()
            token_analyzer.initToken(self.token_address, self.pair_address)
            validator_status.update(token_analyzer.getAllInfo())
            validator_status.update(self.token)

            if validator_status['pair_percent'] < self.filters['min_pool_liq_percent']:
                return True, self.messages["LOW_PAIR_PERCENT"].format(self.filters['min_pool_liq_percent'], validator_status['pair_percent'])

            if validator_status['burned_percent'] < self.filters['min_burned_percent']:
                if validator_status['burned_percent'] > 0:
                    return True, self.messages["LOW_BURNED_PERCENT"].format(self.filters['min_burned_percent'], validator_status['burned_percent'])
                logger.error("Burned balance is zero, so idk what to do")

        return False, validator_status


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
        return True, "Tokens' url broken, not ether blockchain"
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
    if validator_status['issues']['Holder count'].isdigit() and int(validator_status['issues']['Holder count']) < 3:
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

    token_analyzer = TokenWeb3Stats()
    token_analyzer.initToken(token_address, pair_address)
    validator_status.update(token_analyzer.getAllInfo())
    validator_status.update(token)

    if validator_status['pair_percent'] < 40:
        return True, f"Less then 3% of supply in pool, now: {validator_status['pair_percent']:.2f}%"
    if validator_status['burned_percent'] < 90:
        if validator_status['burned_percent'] > 0:
            return True, f"Less then 90% of pool burned, now: {validator_status['burned_percent']:.2f}"
        logger.error("Burned balance is zero, so idk what to do")

    return False, validator_status


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
