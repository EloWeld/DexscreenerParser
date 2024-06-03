from logging import getLogger


DICT = {
    "all_platforms": [],
    "all_filters": ["minLiq","minFdv","minAge","min24HTxns","min6HTxns","min1HTxns","min5MTxns","min24HBuys","min6HBuys","min1HBuys","min5MBuys","min24HSells","min6HSells","min1HSells","min5MSells","min24HVol","min6HVol","min1HVol","min5MVol","min24HChg","min6HChg","min1HChg","min5MChg",
                    "maxLiq","maxFdv","maxAge","max24HTxns","max6HTxns","max1HTxns","max5MTxns","max24HBuys","max6HBuys","max1HBuys","max5MBuys","max24HSells","max6HSells","max1HSells","max5MSells","max24HVol","max6HVol","max1HVol","max5MVol","max24HChg","max6HChg","max1HChg","max5MChg",
                    "order", "rankBy"],
    "all_rank_by": ["trendingScoreM5", "trendingScoreH1","trendingScoreH6","trendingScoreH24","txns", "buys", "sells", "volume", "priceChangeH24", "priceChangeH6", "priceChangeH1", "priceChangeM5", "liquidity", "marketCap", "pairAge"]
}

FILTERS = {
    "minLiq": 2000,
    "min24HChg": 1,
    "minAge": 0,
    "maxAge": 2,
    "chains": ["ethereum"], #"solana", "bsc",  "optimism", "arbitrum", "aptos", "polygon", "avalanche"
    "rankBy": "pairAge",
    "order": "asc",
    "additional": [
        "uniswap_v2",
        #"uniswap_v3"
    ]
}

TRADE_SETTINGS = {
    "buy_pair_age_range": [1, 15],
    "sell_age": 4,
    "my_max_tokens_buys": 77,
    "my_max_tokens_sells": 77,

    "min_sellers": 7,
    "min_sellers_buys_ratio": 0.1
}

SCAM = []

# ———————————————— LOGGER ————————————
logger = getLogger(__name__)
import coloredlogs

coloredlogs.install(level=coloredlogs.DEFAULT_LOG_LEVEL)
