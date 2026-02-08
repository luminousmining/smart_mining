import time
import logging

from config import Config
from common import (
    CoinManager,
    HardwareManager,
    PostgreSQL,
    PoolManager,
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


def get_seconds(seconds: int) -> int:
    return seconds


def get_minutes(minutes: int) -> int:
    return get_seconds(60) * minutes


def get_hours(hours: int) -> int:
    return get_minutes(60) * hours


def get_days(days: int) -> int:
    return get_hours(24) * days


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

    def add_handler(self, name: str, p_tick: int, p_callback: callable, *args, **kwargs) -> None:
        self._handlers[name] = TimerHandler(p_tick, p_callback, *args, **kwargs)

    def process(self, name: str) -> None:
        handler = self._handlers.get(name)
        if not handler:
            return

        if handler.is_time():
            handler.run()


def app_is_running() -> bool:
    return True


def run_application(config: Config) -> None:
    # Managers
    coin_manager = CoinManager()
    pool_manager = PoolManager()
    hadrware_manager = HardwareManager()

    # Database Connection
    pg = PostgreSQL(config)
    if not pg.connect():
        return

    # Timer Handlers Coins
    thmCoin = TimerHandlerManager()
    thmCoin.add_handler('hashrate_no', get_seconds(3), workflow_coin_hashrate_no, config, coin_manager)
    thmCoin.add_handler('what_to_mine', get_seconds(5), workflow_coin_what_to_mine, config, coin_manager)
    thmCoin.add_handler('miner_stat', get_seconds(12), workflow_coin_miner_stat, config, coin_manager, hadrware_manager)
    thmCoin.add_handler('binance', get_seconds(8), workflow_coin_binance, config, coin_manager)
    thmCoin.add_handler('coingecko', get_seconds(20), workflow_coin_coingecko, config, coin_manager)

    # Timer Handlers Pools
    thmPool = TimerHandlerManager()
    thmPool.add_handler('2miner', get_seconds(5), workflow_pool_2miners, config, pool_manager)
    thmPool.add_handler('miner_stat', get_seconds(10), workflow_pool_miner_stat, config, coin_manager, pool_manager)
    thmPool.add_handler('nanopool', get_seconds(1), workflow_pool_nanopool, config, pool_manager)

    while app_is_running():
        # Timer Coins
        thmCoin.process('hashrate_no')
        thmCoin.process('what_to_mine')
        thmCoin.process('miner_stat')
        thmCoin.process('binance')
        thmCoin.process('coingecko')

        # Timer Pools
        thmCoin.process('2miner')
        thmCoin.process('miner_stat')
        thmCoin.process('nanopool')

    time.sleep(0.1)  # évite le CPU à 100 %


    # Database disconnect
    if pg.is_connected() is True:
        pg.disconnect()
