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
    ApiHistoryManager,
    update_coin_by_what_to_mine,
    update_coin_by_hashrate_no,
    update_coin_by_minerstat
)


def workflow_coin_binance(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW BINANCE COIN =====')

    ###########################################################################
    if not config.apis.binance:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = False
    message = ''

    ###########################################################################
    symbol_prefix_skip = ['nicehash-', 'ausdt', 'usdt']
    api = BinanceAPI(config.apis.binance, config.folder_output)

    ###########################################################################
    try:
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

        success = True

    ###########################################################################
    except Exception as err:
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('binance', success, int(duration * 1000), message)


def workflow_coin_coingecko(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW COINGECKO COIN =====')

    ###########################################################################
    if not config.apis.coingecko:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = False
    message = ''

    ###########################################################################
    api = CoinGeckoAPI(config.apis.coingecko, config.folder_output)

    ###########################################################################
    try:
        ###########################################################################
        logging.info('🔄 get list coins...')
        coins = api.get_coins_list()
        for coin in coins:
            symbol = coin['symbol'].lower()

        success = True

    ###########################################################################
    except Exception as err:
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('coingecko', success, int(duration * 1000), message)


def workflow_coin_hashrate_no(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW HASHRATE NO COIN =====')

    ###########################################################################
    if not config.apis.hashrate_no:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = False
    message = ''

    ###########################################################################
    api = HashrateNoAPI(config.apis.hashrate_no, config.folder_output)

    ###########################################################################
    try:
        ###########################################################################
        logging.info('🔄 get coins informations....')
        coins = api.get_coins()
        if coins:
            for _, value in coins.items():
                coin = update_coin_by_hashrate_no(value)
                if coin:
                    coin_manager.insert(coin)
            success = True
        else:
            message = 'API returned empty response'

    ###########################################################################
    except Exception as err:
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('hashrate_no', success, int(duration * 1000), message)


def workflow_coin_miner_stat(config: Config, coin_manager: CoinManager, hardware_manager: HardwareManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW MINERSTAT COIN =====')

    ###########################################################################
    if not config.apis.minerstat:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = False
    message = ''

    ###########################################################################
    api = MinerStatAPI(config.apis.minerstat, config.folder_output)

    ###########################################################################
    try:
        #######################################################################
        logging.info('🔄 get coins informations....')
        coins = api.get_coins()
        for value in coins:
            if value['type'] != 'coin':
                continue
            tag = value['coin'].lower()
            coin = coin_manager.get_from_tag(tag)
            if coin:
                update_coin_by_minerstat(coin, value)

        #######################################################################
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

            ###################################################################
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

        success = True

    ###########################################################################
    except Exception as err:
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('minerstat_coin', success, int(duration * 1000), message)


def workflow_coin_what_to_mine(config: Config, coin_manager: CoinManager, api_history_manager: ApiHistoryManager) -> None:
    logging.info('===== WORKFLOW WHAT TO MINE COIN =====')

    ###########################################################################
    if not config.apis.what_to_mine:
        logging.info('Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    success = False
    message = ''

    ###########################################################################
    logging.info('🔄 get coins informations....')
    api = WhatToMineAPI(config.apis.what_to_mine, config.folder_output)

    ###########################################################################
    try:
        coins = api.get_coins()
        for name, value in coins.items():
            coin = update_coin_by_what_to_mine(name.lower(), value)
            if coin:
                coin_manager.insert(coin)

        success = True

    ###########################################################################
    except Exception as err:
        message = str(err)
        logging.error(f'❌ {err}')

    ###########################################################################
    finally:
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
        api_history_manager.add('what_to_mine', success, int(duration * 1000), message)
