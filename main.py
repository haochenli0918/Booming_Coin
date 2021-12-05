import time
import tqdm

import logging
from pycoingecko import CoinGeckoAPI


logger = logging.getLogger(__name__)


def timestamp_to_date(time_stamp):
    time_array = time.localtime(time_stamp//1000)
    date = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return date


def date_to_timestamp(date):
    time_array = time.strptime(date, "%Y-%m-%d %H:%M:%S")
    time_stamp = int(time.mktime(time_array))
    return time_stamp


cg = CoinGeckoAPI()


def is_booming_coin(coin_id: int, days: str = 3, vs_currency: int = 'usd', booimg_ratio: float = 0.8,
                    min_booming_factor: int = 20):
    '''获取过去3天内每小时coin的price数据，如果price是连续拉升的状态，则判断为booming
    '''
    try:
        market_chart = cg.get_coin_market_chart_by_id(coin_id, vs_currency=vs_currency, days=days)
    except:
        time.sleep(60)
        print('HTTPError, sleep 60 sec')
        return False
    prices = market_chart['prices']
    # 把价格按照时间进行分block
    prices = sorted(prices, key=lambda p: p[0])

    blocks = []
    for idx in range(0, len(prices), 3):
        block_prices = prices[idx: idx + 3]
        max_price = max([price[1] for price in block_prices])
        min_price = min([price[1] for price in block_prices])
        blocks.append((timestamp_to_date(block_prices[0][0]), max_price, min_price))

    max_booming_factor = len(blocks) - 1
    if max_booming_factor < min_booming_factor:
        return False

    booming_factor = 0
    for idx in range(len(blocks) - 1):
        early_block = blocks[idx]
        later_block = blocks[idx + 1]
        if later_block[1] - early_block[1] > 0:
            booming_factor += 1
    if booming_factor > booimg_ratio * max_booming_factor:
        print('Booming with factor: {}, factor_ratio: {:0.2f}'.format(booming_factor,
                                                                      booming_factor / max_booming_factor))
        return True
    return False


interest_keys = {'market_cap_rank', 'categories', 'genesis_date', 'coingecko_rank', 'symbol', 'id'}


def track_booming_coins(booimg_ratio):
    coins_lst = cg.get_coins_list()
    print('Here are {} coins in the world.'.format(len(coins_lst)))

    booming_coins = []
    for coin in tqdm.tqdm(coins_lst[7800:]):
        logger.info(f'start to test {coin["name"]}')
        coin_master = {key: val for key, val in coin.items() if key in interest_keys}
        coin_id = coin_master['id']
        if is_booming_coin(coin_id, booimg_ratio=booimg_ratio):
            booming_coins.append(coin_id)
            print('Booming coin attrs: {}'.format(coin_master))
        time.sleep(1.5)

    # plot booming coin
    for coin_id in booming_coins:
        print(coin_id)


track_booming_coins(booimg_ratio=0.8)