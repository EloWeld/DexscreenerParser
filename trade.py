from filters import check_is_scam, go_filter
from utils import *
from config import *

buys = {}
sells = {}
tokens = {}
bank = 1000
buy_dollars = 10



def trade(driver, rows):
    global bank, buys, SCAM
    for row in rows:
        r = row_to_dict(row)
        if not r:
            continue
        if r['tokenName'] in SCAM:
            continue
        if datetime.timedelta(minutes=TRADE_SETTINGS['buy_pair_age_range'][-1]) >= datetime.datetime.now() - r['createdAt'] >= datetime.timedelta(minutes=TRADE_SETTINGS['buy_pair_age_range'][0]):
            if r['tokenName'] not in buys:
                driver.implicitly_wait(3)
                if r['sells'] < 10 or r['buys'] < 10:
                    continue

                try:
                    is_scam = check_is_scam(driver, r)
                except Exception as e:
                    print(f"Scam check failed {r['tokenName']} {e} {traceback.format_exc()}")
                    SCAM.append(r['tokenName'])
                    go_filter(driver)                  
                    continue
                # go_filter(driver)
                driver.back()
                if is_scam:
                    print(f"Scam {r['tokenName']}")
                    SCAM.append(r['tokenName'])
                    continue
                if len(buys) > TRADE_SETTINGS['my_max_tokens_buys']:
                    continue

                driver.implicitly_wait(15)
                buys[r['tokenName']] = {
                    "buyPrice": r['price'],
                    "buyTime": datetime.datetime.now(),
                    "amount": buy_dollars / r['price']
                }
                bank -= buy_dollars
                logger.warning(f"New buy {r['baseToken']}/{r['quoteToken']}; {r['price']}; Bank: {bank}")
        # Проверяем покупки и продаем монеты, если прошло 15 минут
        for token_name, buy_info in buys.items():
            if datetime.timedelta(minutes=TRADE_SETTINGS['sell_age']) < datetime.datetime.now() - buy_info["buyTime"]:
                if token_name in sells:
                    continue
                if token_name not in tokens:
                    print(f"Монета {token_name} ушла из видимости!")
                    sells[token_name] = {"status": "complete", "is_win": False, "caption": "SCAM"}

                    print(f"GOT SCAMMED! {token_name}; Bank", bank)
                else:
                    sell_price = tokens[token_name]['price']  # Получаем текущую цену продажи монеты
                    bank += sell_price * buy_info["amount"]  # Обновляем баланс банка после продажи монет
                    sells[token_name] = {"status": "complete", "is_win": buy_info['buyPrice'] < sell_price, "sellTime": datetime.datetime.now(), "sellPrice": sell_price}
                    if sell_price / buy_info['buyPrice']-1 > 0:
                        wins += 1
                    else:
                        looses += 1
                    logger.warning(f"Sell {token_name}; Profit {(sell_price / buy_info['buyPrice']-1)*100:.2f}% Bank: {bank}")
                    logger.debug(f"Wins: {looses}; Looses: {looses}: {wins/looses*100:.2f}")