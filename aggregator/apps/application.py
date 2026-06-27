import time
import logging

from config import Config
from common import (
    CoinManager,
    HardwareManager,
    PostgreSQL,
    PoolManager,
    ApiHistoryManager,
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
    workflow_pool_manager,
    workflow_coin_manager,
    workflow_database_manager
)
from workflow import (
    workflow_explorer_ergo,
    workflow_explorer_kaspa,
    workflow_explorer_rvn,
    workflow_explorer_xmr,
    workflow_explorer_cfx,
    workflow_explorer_etc
)


def get_seconds(seconds: int) -> int:
    return seconds


def get_minutes(minutes: int) -> int:
    return get_seconds(60) * minutes


def get_hours(hours: int) -> int:
    return get_minutes(60) * hours


def get_days(days: int) -> int:
    return get_hours(24) * days


class HandlerNamespace:

    API = 'coin'
    EXPLORER = 'explorer'
    POOL = 'pool'
    MANAGER = 'manager'


class TimerHandler:
    def __init__(self, p_tick: int, p_callback: callable, *args, **kwargs):
        self.tick = p_tick
        self.callback = p_callback
        self.args = args
        self.kwargs = kwargs
        self.last_time_update = time.time()

    def is_time(self) -> bool:
        now = time.time()
        elapsed = now - self.last_time_update
        return elapsed >= self.tick

    def run(self) -> None:
        self.callback(*self.args, **self.kwargs)
        self.last_time_update = time.time()


class TimerHandlerManager:
    def __init__(self):
        self._handlers: dict[str, TimerHandler] = {}
        self._namespaces: dict[str, dict[str, TimerHandler]] = {}

    def add_handler(self, namespace: str, name: str, p_tick: int, p_callback: callable, *args, **kwargs) -> None:
        logging.info(f'Initialize Handler: Namespace[{namespace}] - Name[{name}] - Tick[{p_tick}s]')
        if namespace not in self._namespaces:
            self._namespaces[namespace] = {}
        self._namespaces[namespace][name] = TimerHandler(p_tick, p_callback, *args, **kwargs)

    def process(self, namespace: str, name: str) -> None:
        __namespace =self._namespaces.get(namespace)
        if not __namespace:
            return

        __handler = __namespace.get(name)
        if not __handler:
            return

        if __handler.is_time():
            logging.debug(f'Running: [{namespace}] - {name}')
            __handler.run()


def app_is_running() -> bool:
    return True


def run_application(config: Config) -> None:
    # Managers
    coin_manager = CoinManager()
    pool_manager = PoolManager()
    hardware_manager = HardwareManager()
    api_history_manager = ApiHistoryManager()

    # Database Connection
    pg = PostgreSQL(config)
    if not pg.connect():
        return

    # Seed managers with already persisted data
    pg.load(coin_manager, pool_manager)

    t = config.timers

    # Timer Handlers Coins
    thmCoin = TimerHandlerManager()
    if config.apis.hashrate_no:
        thmCoin.add_handler(HandlerNamespace.API, 'hashrate_no', get_seconds(t.hashrate_no), workflow_coin_hashrate_no, config, coin_manager, api_history_manager)
    if config.apis.what_to_mine:
        thmCoin.add_handler(HandlerNamespace.API, 'what_to_mine', get_seconds(t.what_to_mine), workflow_coin_what_to_mine, config, coin_manager, api_history_manager)
    if config.apis.minerstat:
        thmCoin.add_handler(HandlerNamespace.API, 'miner_stat', get_seconds(t.miner_stat_coin), workflow_coin_miner_stat, config, coin_manager, hardware_manager, api_history_manager)
    if config.apis.binance:
        thmCoin.add_handler(HandlerNamespace.API, 'binance', get_seconds(t.binance), workflow_coin_binance, config, coin_manager, api_history_manager)
    if config.apis.coingecko:
        thmCoin.add_handler(HandlerNamespace.API, 'coingecko', get_seconds(t.coingecko), workflow_coin_coingecko, config, coin_manager, api_history_manager)
    if config.apis.coinpaprika:
        thmCoin.add_handler(HandlerNamespace.API, 'coinpaprika', get_seconds(t.coinpaprika), workflow_coin_coinpaprika, config, coin_manager, api_history_manager)
    if config.apis.coinmarketcap:
        thmCoin.add_handler(HandlerNamespace.API, 'coinmarketcap', get_seconds(t.coinmarketcap), workflow_coin_coinmarketcap, config, coin_manager, api_history_manager)
    if config.apis.coincap:
        thmCoin.add_handler(HandlerNamespace.API, 'coincap', get_seconds(t.coincap), workflow_coin_coincap, config, coin_manager, api_history_manager)
    if config.apis.messari:
        thmCoin.add_handler(HandlerNamespace.API, 'messari', get_seconds(t.messari), workflow_coin_messari, config, coin_manager, api_history_manager)
    if config.apis.cryptocompare:
        thmCoin.add_handler(HandlerNamespace.API, 'cryptocompare', get_seconds(t.cryptocompare), workflow_coin_cryptocompare, config, coin_manager, api_history_manager)

    # Timer Handlers Explorers
    if 'erg' in config.apis.explorer:
        thmCoin.add_handler(HandlerNamespace.EXPLORER, 'erg', get_seconds(t.explorer_erg), workflow_explorer_ergo, config, coin_manager, api_history_manager)
    if 'kas' in config.apis.explorer:
        thmCoin.add_handler(HandlerNamespace.EXPLORER, 'kas', get_seconds(t.explorer_kas), workflow_explorer_kaspa, config, coin_manager, api_history_manager)
    if 'rvn' in config.apis.explorer:
        thmCoin.add_handler(HandlerNamespace.EXPLORER, 'rvn', get_seconds(t.explorer_rvn), workflow_explorer_rvn, config, coin_manager, api_history_manager)
    if 'xmr' in config.apis.explorer:
        thmCoin.add_handler(HandlerNamespace.EXPLORER, 'xmr', get_seconds(t.explorer_xmr), workflow_explorer_xmr, config, coin_manager, api_history_manager)
    if 'cfx' in config.apis.explorer:
        thmCoin.add_handler(HandlerNamespace.EXPLORER, 'cfx', get_seconds(t.explorer_cfx), workflow_explorer_cfx, config, coin_manager, api_history_manager)
    if 'etc' in config.apis.explorer:
        thmCoin.add_handler(HandlerNamespace.EXPLORER, 'etc', get_seconds(t.explorer_etc), workflow_explorer_etc, config, coin_manager, api_history_manager)

    # Timer Handlers Pools
    thmPool = TimerHandlerManager()
    if config.apis.two_miners:
        thmPool.add_handler(HandlerNamespace.POOL, '2miner', get_seconds(t.two_miners), workflow_pool_2miners, config, pool_manager, api_history_manager)
    if config.apis.minerstat:
        thmPool.add_handler(HandlerNamespace.POOL, 'miner_stat', get_seconds(t.miner_stat_pool), workflow_pool_miner_stat, config, coin_manager, pool_manager, api_history_manager)
    if config.apis.nanopool:
        thmPool.add_handler(HandlerNamespace.POOL, 'nanopool', get_seconds(t.nanopool), workflow_pool_nanopool, config, pool_manager, api_history_manager)


    # Timer Handlers Managers
    thmManager = TimerHandlerManager()
    thmManager.add_handler(HandlerNamespace.MANAGER, 'coin', get_seconds(t.coin_manager), workflow_coin_manager, config, coin_manager)
    thmManager.add_handler(HandlerNamespace.MANAGER, 'pool', get_seconds(t.pool_manager), workflow_pool_manager, config, pool_manager)
    thmManager.add_handler(HandlerNamespace.MANAGER, 'database', get_seconds(t.database), workflow_database_manager, config, pg, coin_manager, pool_manager, hardware_manager, api_history_manager)

    while app_is_running():
        # Timer Coins
        thmCoin.process(HandlerNamespace.API, 'hashrate_no')
        thmCoin.process(HandlerNamespace.API, 'what_to_mine')
        thmCoin.process(HandlerNamespace.API, 'miner_stat')
        thmCoin.process(HandlerNamespace.API, 'binance')
        thmCoin.process(HandlerNamespace.API, 'coingecko')
        thmCoin.process(HandlerNamespace.API, 'coinpaprika')
        thmCoin.process(HandlerNamespace.API, 'coinmarketcap')
        thmCoin.process(HandlerNamespace.API, 'coincap')
        thmCoin.process(HandlerNamespace.API, 'messari')
        thmCoin.process(HandlerNamespace.API, 'cryptocompare')

        # Timer Pools
        thmPool.process(HandlerNamespace.POOL, '2miner')
        thmPool.process(HandlerNamespace.POOL, 'miner_stat')
        thmPool.process(HandlerNamespace.POOL, 'nanopool')

        # Timer Explorer
        thmCoin.process(HandlerNamespace.EXPLORER, 'erg')
        thmCoin.process(HandlerNamespace.EXPLORER, 'kas')
        thmCoin.process(HandlerNamespace.EXPLORER, 'rvn')
        thmCoin.process(HandlerNamespace.EXPLORER, 'xmr')
        thmCoin.process(HandlerNamespace.EXPLORER, 'cfx')
        thmCoin.process(HandlerNamespace.EXPLORER, 'etc')

        # Timer Managers
        thmManager.process(HandlerNamespace.MANAGER, 'coin')
        thmManager.process(HandlerNamespace.MANAGER, 'pool')
        thmManager.process(HandlerNamespace.MANAGER, 'database')

        time.sleep(1)

    # Database disconnect
    if pg.is_connected() is True:
        pg.disconnect()
