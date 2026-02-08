import logging

from config import Config
from common import (
    CoinManager,
    HardwareManager,
    PostgreSQL,
    PoolManager
)
from workflow import (
    workflow_coin_binance,
    workflow_coin_coingecko,
    workflow_coin_hashrate_no,
    workflow_coin_miner_stat,
    workflow_coin_what_to_mine
)
from workflow import (
    workflow_pool_nanopool,
    workflow_pool_miner_stat,
    workflow_pool_2miners
)


def run_standalone(config: Config) -> None:
    # Managers
    coin_manager = CoinManager()
    pool_manager = PoolManager()
    hadrware_manager = HardwareManager()

    # Database Connection
    pg = PostgreSQL(config)
    if not pg.connect():
        return

    # APIs Coin informations
    workflow_coin_hashrate_no(config, coin_manager)
    workflow_coin_what_to_mine(config, coin_manager)
    workflow_coin_miner_stat(config, coin_manager, hadrware_manager)
    workflow_coin_binance(config, coin_manager)
    workflow_coin_coingecko(config, coin_manager)

    # APIs Pools
    workflow_pool_2miners(config, pool_manager)
    workflow_pool_miner_stat(config, coin_manager, pool_manager)
    workflow_pool_nanopool(config, pool_manager)

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
