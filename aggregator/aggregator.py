import time
import logging
import argparse

from config import Config
from api import (
    BinanceAPI,
    CoinGeckoAPI,
    HashrateNoAPI,
    MinerStatAPI,
    WhatToMineAPI,
    TwoMinersAPI,
    NanopoolAPI
)
from common import (
    CoinManager,
    HardwareManager,
    PostgreSQL,
    Pool,
    Coin,
    CoinPool,
    Block,
    BLOCK_STATUS,
    PoolManager,
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


def __coingecko(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== HASHRATE NO =====')

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


def __what_to_mine(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== WHAT TO MINE =====')

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


def __miner_stat(config: Config, coin_manager: CoinManager, pool_manager: PoolManager, hardware_manager: HardwareManager) -> None:
    logging.info('===== MINERSTAT =====')

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
    logging.info('🔄 get pools informations....')
    pools = api.get_pools()
    for pool_data in pools:
        pool = Pool()
        coins = pool_data['coins']
        if not coins:
            continue
        pool.name = pool_data['name'].lower()

        for coin_name, item in coins.items():
            coin = coin_manager.get_from_tag(coin_name.lower())
            if not coin:
                logging.warning(f'⚠️ Cannot find tag [{coin_name.lower()}] from pool [{pool.name}]')
                continue
            pool.coins[coin.name] = {}

            algorithm = item['algorithm'].lower().replace('-', '')
            fee = item['fee'].replace('%', '')
            if '-' in fee:
                fee = fee.split('-')[-1]
            anonymous = item['anonymous']
            registration = item['registration']

            if not algorithm:
                continue

            pool.coins[coin.name]['algorithm'] = algorithm
            pool.coins[coin.name]['algorithm'] = algorithm
            pool.coins[coin.name]['fee'] = fee if fee else 0
            pool.coins[coin.name]['anonymous'] = anonymous
            pool.coins[coin.name]['registration'] = registration

            pool_manager.insert(pool)

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


def __binance(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== BINANCE =====')

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


def __2miners(config: Config, pool_manager: PoolManager) -> None:
    ###########################################################################
    logging.info('===== 2MINERS =====')

    ###########################################################################
    if not config.apis.two_miners:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    pool = pool_manager.get_pool('2miners')
    if not pool:
        pool = Pool()
        pool.name = '2miners'
    api = TwoMinersAPI(config.apis.two_miners, config.folder_output)

    ###########################################################################
    logging.info('🔄 Update blocks informations')
    blocks = api.get_blocks()
    for tag, data in blocks.items():
        coin = CoinPool()
        coin.tag = tag
        if tag not in pool.blocks:
            pool.blocks[tag] = []
        for status in ('candidates', 'matured', 'immature'):
            total_blocks = data[f'{status}Total']
            logging.debug(f'🔍 {tag} have {total_blocks} blocks [{status}]')
            if total_blocks == 0:
                continue
            list_blocks = data[status]
            if not list_blocks:
                logging.error(f'❌ {tag} list of block [{status}] is empty!')
                continue
            for block_data in list_blocks:
                block = Block()
                block.tag = tag
                block.height = block_data['height']
                block.timestamp = block_data['timestamp']
                block.difficulty = block_data['difficulty']
                if status == 'candidates':
                    block.status = BLOCK_STATUS.CANDIDATE
                elif  status == 'matured':
                    block.status = BLOCK_STATUS.MATURED
                elif  status == 'immature':
                    block.status = BLOCK_STATUS.IMMATURE
                if 'currentLuck' in block_data:
                    block.luck = block_data['currentLuck']
                pool.update_block(block)

    ###########################################################################
    logging.info('🔄 Update miners informations')
    miners = api.get_miners()
    for tag, data in miners.items():
        coin = CoinPool()
        coin.tag = tag
        coin.total_miner = data['minersTotal']
        logging.debug(f'🔍 {tag} have {coin.total_miner} miners')
        pool.update_coin(coin)

    ###########################################################################
    logging.info('🔄 Update state informations')
    stats = api.get_stats()
    for tag, data in stats.items():
        coin = CoinPool()
        coin.tag = tag
        coin.hashrate = data['hashrate'] if 'hashrate' in data else None
        pool.update_coin(coin)

    ###########################################################################
    pool_manager.update_pool(pool)

    ###########################################################################
    duration = time.time() - start_time
    logging.info(f'🕐 synchro in {duration:.2f} seconds')


def __nanopool(config: Config, pool_manager: PoolManager) -> None:
    logging.info('===== NANOPOOL =====')

    ###########################################################################
    if not config.apis.two_miners:
        logging.info('🚮 Skipped!')
        return

    ###########################################################################
    start_time = time.time()
    api = NanopoolAPI(config.apis.nanopool, config.folder_output)

    ###########################################################################
    logging.info('🔄 Update avg block time')
    avg_blocks = api.get_avg_blocks()

    ###########################################################################
    logging.info('🔄 Update last block number')
    last_blocks_number = api.get_last_block_number()

    ###########################################################################
    logging.info('🔄 Update block stats')
    block_stats = api.get_block_stats()

    ###########################################################################
    duration = time.time() - start_time
    logging.info(f'🕐 synchro in {duration:.2f} seconds')


def run(config: Config):
    logging.info('🚀 Start aggregator!')

    # Managers
    coin_manager = CoinManager()
    pool_manager = PoolManager()
    hadrware_manager = HardwareManager()

    # Database Connection
    pg = PostgreSQL(config)
    if not pg.connect():
        return

    # APIs Coin informations
    __hashrate_no(config, coin_manager)
    __what_to_mine(config, coin_manager)
    __miner_stat(config, coin_manager, pool_manager, hadrware_manager)
    __binance(config, coin_manager)
    __coingecko(config, coin_manager)

    # APIs Pools
    __2miners(config, pool_manager)
    __nanopool(config, pool_manager)

    # Coin Manager update
    coin_manager.update()
    pool_manager.update()

    # Save data
    coin_manager.dump(config.folder_output)
    pool_manager.dump(config.folder_output)
    hadrware_manager.dump(config.folder_output)

    # Database update
    if config.db.update:
        pg.update(coin_manager, pool_manager, hadrware_manager)

    # Database disconnect
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
    print('USAGE\npython3 aggregator.py')
