import time
import logging

from config import Config
from api import (
    BinanceAPI,
    CoinGeckoAPI,
    HashrateNoAPI,
    MinerStatAPI,
    WhatToMineAPI
)
from common import (
    CoinManager,
    HardwareManager,
    create_coin_by_what_to_mine,
    create_coin_by_hashrate_no,
    update_coin_by_minerstat
)


def workflow_coin_binance(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== WORKFLOW BINANCE COIN =====')

    ###########################################################################
    if not config.apis.binance:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()

    ###########################################################################
    symbol_prefix_skip = ['nicehash-', 'ausdt', 'usdt']
    api = BinanceAPI(config.apis.binance, config.folder_output)

    ###########################################################################
    logging.info('🔄 get list coins...')
    symbols = api.get_symbols()

    ###########################################################################
    logging.info('🔄 filter coins...')
    filtered = []
    for symbol_data in symbols:
        symbol = symbol_data['symbol'].lower()
        if any(item in symbol for item in symbol_prefix_skip):
            continue
        if not symbol.endswith('usd'):
            continue
        filtered.append(symbol_data)

    ###########################################################################
    logging.info('🔄 update coins price...')
    for data in filtered:
        symbol = data['symbol']
        tag = data['baseAsset'].lower().replace('usd', '')
        raw = api.get_price(symbol)
        if 'price' not in raw:
            logging.error(f'❌ missing key "price" -> {raw}')
            return
        price = float(raw['price'])
        coin = coin_manager.get_from_tag(tag)
        if coin and coin.reward:
            coin.reward.usd = price

    ###########################################################################
    duration = time.time() - start_time
    logging.info(f'🕐 synchro in {duration:.2f} seconds')


def workflow_coin_coingecko(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== WORKFLOW COINGECKO COIN =====')

    ###########################################################################
    if not config.apis.coingecko:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()

    ###########################################################################
    api = CoinGeckoAPI(config.apis.coingecko, config.folder_output)

    ###########################################################################
    logging.info('🔄 get list coins...')
    coins = api.get_coins_list()
    for coin in coins:
        symbol = coin['symbol'].lower()

    ###########################################################################
    duration = time.time() - start_time
    logging.info(f'🕐 synchro in {duration:.2f} seconds')


def workflow_coin_hashrate_no(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== WORKFLOW HASHRATE NO COIN =====')

    ###########################################################################
    if not config.apis.hashrate_no:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()

    ###########################################################################
    api = HashrateNoAPI(config.apis.hashrate_no, config.folder_output)

    ###########################################################################
    logging.info('🔄 get coins informations....')
    coins = api.get_coins()
    for _, value in coins.items():
        coin = create_coin_by_hashrate_no(value)
        if coin:
            coin_manager.insert(coin)

    ###########################################################################
    duration = time.time() - start_time
    logging.info(f'🕐 synchro in {duration:.2f} seconds')


def workflow_coin_miner_stat(config: Config, coin_manager: CoinManager, hardware_manager: HardwareManager) -> None:
    logging.info('===== WORKFLOW MINERSTAT COIN =====')

    ###########################################################################
    if not config.apis.minerstat:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()

    ###########################################################################
    api = MinerStatAPI(config.apis.minerstat, config.folder_output)

    ###########################################################################
    logging.info('🔄 get coins informations....')
    coins = api.get_coins()
    for value in coins:
        if value['type'] != 'coin':
            continue
        tag = value['coin'].lower()
        coin = coin_manager.get_from_tag(tag)
        if coin:
            update_coin_by_minerstat(coin, value)

    ###########################################################################
    logging.info('🔄 get hardware informations....')
    hardwares = api.get_hardware()
    for hardware in hardwares:
        hardware_type = hardware['type']
        if hardware_type != 'gpu':
            continue
        algorithms = hardware['algorithms']
        if not algorithms:
            continue
        hardware_name = hardware['name'].lower().replace(' ', '_')
        hardware_brand = hardware['brand'].lower()

        ###########################################################################
        for algo_name, data in algorithms.items():
            algo_name = algo_name.lower().replace('-', '')
            speed = data['speed']
            power = data['power']
            hardware_manager.insert(
                name=hardware_name,
                brand=hardware_brand,
                algo=algo_name,
                speed=speed,
                power=power)

    ###########################################################################
    duration = time.time() - start_time
    logging.info(f'🕐 synchro in {duration:.2f} seconds')


def workflow_coin_what_to_mine(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== WORKFLOW WHAT TO MINE COIN =====')

    ###########################################################################
    if not config.apis.what_to_mine:
        logging.info('Skipped!')
        return

    ###########################################################################
    start_time = time.time()

    ###########################################################################
    logging.info('🔄 get coins informations....')
    api = WhatToMineAPI(config.apis.what_to_mine, config.folder_output)
    coins = api.get_coins()
    for name, value in coins.items():
        coin = create_coin_by_what_to_mine(name.lower(), value)
        if coin:
            coin_manager.insert(coin)

    ###########################################################################
    duration = time.time() - start_time
    logging.info(f'🕐 synchro in {duration:.2f} seconds')
