
def check_is_scam(driver: Chrome, token):
    el = driver.find_element(By.XPATH, f"//a[contains(.,'{token['tokenName']}')]")
    ActionChains(driver).scroll_to_element(el)
    el.click()
    sellers = driver.find_elements(By.CSS_SELECTOR, "div.chakra-stack.custom-1vsnzom > span.chakra-text.custom-0")
    buyers = driver.find_elements(By.CSS_SELECTOR, "div.chakra-stack.custom-gh4bym > span.chakra-text.custom-0")
    sells, sell_vol, sellers_count = [int(convert_to_num(x.text)) for x in sellers]
    buys, buys_vol, buyers_count = [int(convert_to_num(x.text)) for x in buyers]
    try:
        driver.find_element(By.CSS_SELECTOR, "svg.custom-19rsff")
        locked_liq = True
    except Exception as e:
        locked_liq = False
    try:
        driver.find_element(By.CSS_SELECTOR, "div.custom-125ye0j")
        has_header = True
    except Exception as e:
        has_header = False

    if not locked_liq:
        return True
    # if not has_header:
        # return True
    if sellers_count / buyers_count < TRADE_SETTINGS["min_sellers_buys_ratio"]:
        return True
    if sellers_count < TRADE_SETTINGS['min_sellers']:
        return True
    return False

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