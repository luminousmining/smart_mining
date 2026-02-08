from config import Config
from common import (
    CoinManager,
    HardwareManager,
    PostgreSQL,
    PoolManager,
)


def run_application(config: Config) -> None:
    # Managers
    coin_manager = CoinManager()
    pool_manager = PoolManager()
    hadrware_manager = HardwareManager()

    # Database Connection
    pg = PostgreSQL(config)
    if not pg.connect():
        return

    # Database disconnect
    if pg.is_connected() is True:
        pg.disconnect()
