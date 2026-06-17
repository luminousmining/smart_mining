"""
Standalone aggregator application for mining data collection.

This module orchestrates the collection and processing of cryptocurrency and mining pool data
from multiple external sources. It manages the lifecycle of data retrieval, processing, storage,
and database synchronization.
"""

from config import Config
from common import (
    CoinManager,
    HardwareManager,
    PostgreSQL,
    PoolManager,
    ApiHistoryManager
)
from workflow import (
    workflow_coin_binance,
    workflow_coin_coingecko,
    workflow_coin_coinpaprika,
    workflow_coin_coinmarketcap,
    workflow_coin_coincap,
    workflow_coin_messari,
    workflow_coin_cryptocompare,
    workflow_coin_hashrate_no,
    workflow_coin_miner_stat,
    workflow_coin_what_to_mine
)
from workflow import (
    workflow_pool_nanopool,
    workflow_pool_miner_stat,
    workflow_pool_2miners
)
from workflow import (
    workflow_explorer_ergo,
    workflow_explorer_kaspa,
    workflow_explorer_rvn,
    workflow_explorer_xmr,
    workflow_explorer_cfx,
    workflow_explorer_etc
)


def run_standalone(config: Config) -> None:
    """
    Execute the standalone data aggregation workflow.

    This function orchestrates the complete lifecycle of mining data collection:
    1. Initializes managers for coins, pools, and hardware
    2. Establishes database connection
    3. Fetches cryptocurrency data from multiple APIs
    4. Fetches mining pool data from multiple APIs
    5. Updates managers with collected data
    6. Exports data to configured output folder
    7. Optionally syncs data to database
    8. Closes database connection

    Args:
        config (Config): Configuration object containing API credentials, database settings,
                        and output folder path.

    Returns:
        None
    """
    # Initialize managers for managing coins, pools, and hardware data
    coin_manager = CoinManager()
    pool_manager = PoolManager()
    hadrware_manager = HardwareManager()
    api_history_manager = ApiHistoryManager()

    # Establish database connection
    pg = PostgreSQL(config)
    if config.db.update and not pg.connect():
        return

    # Fetch cryptocurrency data from multiple external APIs
    workflow_coin_hashrate_no(config, coin_manager, api_history_manager)
    workflow_coin_what_to_mine(config, coin_manager, api_history_manager)
    workflow_coin_miner_stat(config, coin_manager, hadrware_manager, api_history_manager)
    workflow_coin_binance(config, coin_manager, api_history_manager)
    workflow_coin_coingecko(config, coin_manager, api_history_manager)
    workflow_coin_coinpaprika(config, coin_manager, api_history_manager)
    workflow_coin_coinmarketcap(config, coin_manager, api_history_manager)
    workflow_coin_coincap(config, coin_manager, api_history_manager)
    workflow_coin_messari(config, coin_manager, api_history_manager)
    workflow_coin_cryptocompare(config, coin_manager, api_history_manager)

    # Fetch mining pool data from multiple external APIs
    workflow_pool_2miners(config, pool_manager, api_history_manager)
    workflow_pool_miner_stat(config, coin_manager, pool_manager, api_history_manager)
    workflow_pool_nanopool(config, pool_manager, api_history_manager)

    # Fetch on-chain data directly from blockchain explorers (runs last to overwrite secondary sources)
    workflow_explorer_ergo(config, coin_manager, api_history_manager)
    workflow_explorer_kaspa(config, coin_manager, api_history_manager)
    workflow_explorer_rvn(config, coin_manager, api_history_manager)
    workflow_explorer_xmr(config, coin_manager, api_history_manager)
    workflow_explorer_cfx(config, coin_manager, api_history_manager)
    workflow_explorer_etc(config, coin_manager, api_history_manager)

    # Process and finalize collected data
    coin_manager.update()
    pool_manager.update()

    # Export collected data to configured output folder
    coin_manager.dump(config.folder_output)
    pool_manager.dump(config.folder_output)
    hadrware_manager.dump(config.folder_output)

    # Synchronize data to database if enabled in configuration
    if config.db.update:
        pg.update(coin_manager, pool_manager, hadrware_manager, api_history_manager)

    # Close database connection
    if config.db.update and pg.is_connected() is True:
            pg.disconnect()
