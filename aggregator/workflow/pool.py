import time
import logging

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
    CoinPool,
    Block,
    BLOCK_STATUS,
    PoolManager,
    create_coin_by_what_to_mine,
    create_coin_by_hashrate_no,
    update_coin_by_minerstat
)


def workflow_pool_miner_stat(config: Config, coin_manager: CoinManager, pool_manager: PoolManager) -> None:
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
    duration = time.time() - start_time
    logging.info(f'🕐 synchro in {duration:.2f} seconds')


def workflow_pool_nanopool(config: Config, pool_manager: PoolManager) -> None:
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


def workflow_pool_2miners(config: Config, pool_manager: PoolManager) -> None:
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