import time
import psycopg2
import logging

from config import Config
from common import (
    CoinManager,
    PoolManager,
    HardwareManager
)


class PostgreSQL:

    def __init__(self, config: Config) -> None:
        self.host = config.db.host
        self.database = config.db.database
        self.username = config.db.username
        self.password = config.db.password
        self.port = config.db.port
        self.cursor = None
        self.connection = None

    def connect(self) -> bool:
        try:
            logging.info(f'🔄 Connection database {self.database} with user {self.username}...')
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.username,
                password=self.password,
                port=self.port
            )
            self.cursor = self.connection.cursor()
        except Exception as err:
            logging.error(err)
            self.connection = None
            return False

        logging.info(f'✅ Connection with success')
        return True

    def request_one(self, query: str):
        if not self.cursor:
            logging.error(f'❌ Cursor is invalid')

        logging.debug(f'📝 {query}')

        self.cursor.execute(query)
        return self.cursor.fetchone()

    def request_all(self, query: str):
        if not self.cursor:
            logging.error(f'❌ Cursor is invalid')

        logging.debug(f'📝 {query}')

        self.cursor.execute(query)
        results = self.cursor.fetchall()
        for row in results:
            yield row

    def execute(self, query: str) -> None:
        if not self.cursor:
            logging.error(f'❌ Cursor is invalid')
            return
        if not self.connection:
            logging.error(f'❌ Connection is invalid')
            return

        logging.debug(f'📝 {query}')

        self.cursor.execute(query)
        self.connection.commit()

    def disconnect(self) -> bool:
        if not self.cursor:
            logging.error(f'❌ Cursor is invalid')
            return False
        if not self.connection:
            logging.error(f'❌ Connection is invalid')
            return False

        self.cursor.close()
        self.connection.close()
        return True

    def is_connected(self) -> bool:
        if not self.cursor:
            logging.error(f'❌ Cursor is invalid')
            return False
        if not self.connection:
            logging.error(f'❌ Connection is invalid')
            return False

        return True

    def _update_coin(self, coin_manager: CoinManager):
        for coin in coin_manager._coins.values():
            query = 'CALL insert_coin('\
                f'\'{coin.name}\','\
                f' \'{coin.tag}\','\
                f' \'{coin.algorithm}\','\
                f' {coin.reward.usd if coin.reward.usd else 0},'\
                f' {coin.reward.usd_sec if coin.reward.usd_sec else 0},'\
                f' {coin.reward.difficulty if coin.reward.difficulty else 0},'\
                f' {coin.reward.network_hashrate if coin.reward.network_hashrate else 0},'\
                f' {coin.reward.hash_usd if coin.reward.hash_usd else 0},'\
                f' {coin.reward.emission_coin if coin.reward.emission_coin else 0},'\
                f' {coin.reward.emission_usd if coin.reward.emission_usd else 0},'\
                f' {coin.reward.market_cap if coin.reward.market_cap else 0}'\
                f');'
            self.execute(query)

    def _update_pool(self, pool_manager: PoolManager) -> None:
        for pool_name, pool in pool_manager._pools.items():
            pool_name = pool_name.replace('\'', '')
            for coin in pool.coins.values():
                query = 'CALL insert_pool('\
                    f'\'{pool_name}\','\
                    f'\'{coin.tag}\''\
                    ');'
                self.execute(query)

            for blocks in pool.blocks.values():
                for block in blocks:
                    query = 'CALL insert_pool_stats('\
                        f'\'{pool_name}\','\
                        f'\'{block.tag}\','\
                        f'{block.height if block.height else 0},'\
                        f'{block.timestamp if block.timestamp else 0},'\
                        f'{block.difficulty if block.difficulty else 0},'\
                        f'{block.luck if block.luck else 0},'\
                        f'\'{block.status if block.status else str()}\''\
                        ');'
                    self.execute(query)

    def _update_hardware(self, hardware_manager: HardwareManager) -> None:
        for hardware in hardware_manager._hardwares:
            name = hardware['name']
            algo = hardware['algo']
            speed = hardware['speed']
            power = hardware['power']

            query = f'CALL insert_hardware(\'{name}\');'
            self.execute(query)

            query = f'SELECT id FROM hardware WHERE name=\'{name}\';'
            hardware_id = self.request_one(query)[0]
            query = 'CALL insert_hardware_mining('\
                    f'{hardware_id},'\
                    f'\'{algo}\','\
                    f'{speed},'\
                    f'{power}'\
                    ');'
            self.execute(query)

    def update(self, coin_manager: CoinManager, pool_manager: PoolManager, hardware_manager: HardwareManager) -> None:
        ###########################################################################
        logging.info('===== POSTGRESQL =====')

        #######################################################################
        start_time = time.time()

        #######################################################################
        if not self.cursor:
            logging.error(f'❌ Cursor is invalid')
            return
        if not self.connection:
            logging.error(f'❌ Connection is invalid')
            return

        #######################################################################
        # self._update_coin(coin_manager)
        self._update_pool(pool_manager)
        # self._update_hardware(hardware_manager)

        ###########################################################################
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
