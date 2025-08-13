import logging
import argparse

from config import Config
from api import (
    BinanceAPI,
    HashrateNoAPI,
    MinerStatAPI,
    WhatToMineAPI
)
from common import (
    CoinManager,
    HardwareManager,
    PostgreSQL,
    create_coin_by_what_to_mine,
    create_coin_by_hashrate_no,
    update_coin_by_minerstat
)


def initialize_logger(level: str) -> None:
    log_level = logging.DEBUG

    if level == 'debug':
        log_level = logging.DEBUG
    elif level == 'warn':
        log_level = logging.WARNING
    elif level == 'error':
        log_level = logging.ERROR
    elif level == 'info':
        log_level = logging.INFO

    logging.basicConfig(
        format='[%(levelname)s][%(asctime)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=log_level)


def __hashrate_no(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== HASHRATE NO =====')

    if not config.apis.hashrate_no:
        return

    logging.info('🔄 get coins informations....')
    api = HashrateNoAPI(config.apis.hashrate_no, config.folder_output)
    coins = api.get_coins()
    for value in coins:
        coin = create_coin_by_hashrate_no(value)
        if coin:
            coin_manager.insert(coin)


def __what_to_mine(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== WHAT TO MINE =====')

    if not config.apis.what_to_mine:
        return

    logging.info('🔄 get coins informations....')
    api = WhatToMineAPI(config.apis.what_to_mine, config.folder_output)
    coins = api.get_coins()
    for name, value in coins.items():
        coin = create_coin_by_what_to_mine(name.lower(), value)
        if coin:
            coin_manager.insert(coin)


def __miner_stat(config: Config, coin_manager: CoinManager, hardware_manager: HardwareManager) -> None:
    logging.info('===== MINERSTAT =====')

    if not config.apis.minerstat:
        return

    logging.info('🔄 get coins informations....')
    api = MinerStatAPI(config.apis.minerstat, config.folder_output)
    coins = api.get_coins()
    for value in coins:
        if value['type'] != 'coin':
            continue
        tag = value['coin'].lower()
        coin = coin_manager.get_from_tag(tag)
        if coin:
            update_coin_by_minerstat(coin, value)

    logging.info('🔄 get hardware informations....')
    hardwares = api.get_hardware()
    for hardware in hardwares:
        hardware_type = hardware['type']
        if hardware_type != 'gpu':
            continue
        algorithms = hardware['algorithms']
        if not algorithms:
            continue
        hardware_name = hardware['name'].lower()
        hardware_brand = hardware['brand'].lower()
        for algo_name, data in algorithms.items():
            algo_name = algo_name.lower().replace('-', '')
            speed = data['speed']
            power = data['power']
            hardware_manager.insert(
                name=hardware_name,
                brand=hardware_brand,
                speed=speed,
                power=power)


def __binance(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== BINANCE =====')

    if not config.apis.binance:
        return

    logging.info('🔄 get coins informations....')
    api = BinanceAPI(config.apis.binance, config.folder_output)
    symbols = api.get_symbols()
    for data in symbols:
        symbol = data['symbol']
        symbol_lower = symbol.lower()
        if 'nicehash-' in symbol_lower:
            continue
        if 'ausdt' in symbol_lower:
            continue
        if 'usdt' in symbol_lower:
            continue
        if symbol_lower[-3:] == 'usd':
            tag = data['baseAsset'].lower().replace('usd', '')
            price = float(api.get_price(symbol)['price'])
            coin = coin_manager.get_from_tag(tag)
            if coin and coin.reward:
                if coin.name == 'zcash':
                    logging.info(symbol)
                    logging.info(coin.to_dict())
                coin.reward.usd = price


def run(config: Config):
    logging.info('🚀 Start scrapper!')

    # Managers
    coin_manager = CoinManager()
    hadrware_manager = HardwareManager()

    # Database
    pg = PostgreSQL(config)
    if not pg.connect():
        return

    # APIs
    __hashrate_no(config, coin_manager)
    __what_to_mine(config, coin_manager)
    __miner_stat(config, coin_manager, hadrware_manager)
    # __binance(config, coin_manager)

    # Coin Manager update
    coin_manager.update()

    # Save data
    coin_manager.dump(config.folder_output)
    hadrware_manager.dump(config.folder_output)
    pg.update(coin_manager, hadrware_manager)

    # PostgreSQL disconnect
    if pg.is_connected() is True:
        pg.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default='config.json')
    args = parser.parse_args()

    project_config = Config(args.config)
    initialize_logger(project_config.log)
    run(project_config)
else:
    print('USAGE python3 main.py')
