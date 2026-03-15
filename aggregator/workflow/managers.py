import logging

from config import Config
from common import (
    CoinManager,
    PoolManager,
    PostgreSQL
)


def workflow_pool_manager(config: Config, pool_manager: PoolManager) -> None:
    logging.info('===== WORKFLOW POOL MANAGER =====')

    ###########################################################################
    if not config.db.update:
        logging.info('🚮 Skipped!')
        return

    pool_manager.update()


def workflow_coin_manager(config: Config, coin_manager: CoinManager) -> None:
    logging.info('===== WORKFLOW COIN MANAGER =====')

    ###########################################################################
    if not config.db.update:
        logging.info('🚮 Skipped!')
        return

    coin_manager.update()


def workflow_database_manager(config: Config, pg: PostgreSQL, coin_manager: CoinManager, pool_manager: PoolManager) -> None:
    logging.info('===== WORKFLOW COIN MANAGER =====')

    ###########################################################################
    if not config.db.update:
        logging.info('🚮 Skipped!')
        return

    pg.update(coin_manager, pool_manager)
