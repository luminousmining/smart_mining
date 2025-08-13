import psycopg2
import logging

from config import Config
from common import (
    CoinManager,
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

    def update(self, coin_manager: CoinManager, hardware_manager: HardwareManager) -> None:
        if not self.cursor:
            logging.error(f'❌ Cursor is invalid')
            return
        if not self.connection:
            logging.error(f'❌ Connection is invalid')
            return

        for _, coin in coin_manager._coins.items():
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

        for hardware in hardware_manager._hardwares:
            name = hardware['name']
            speed = hardware['speed']
            power = hardware['power']

            query = f'CALL insert_hardware(\'{name}\');'
            self.execute(query)

            query = f'SELECT id FROM hardware WHERE name=\'{name}\';'
            hardware_id = self.request_one(query)[0]

            query = 'CALL insert_hardware_mining('\
                    f'{hardware_id},'\
                    f'{speed},'\
                    f'{power}'\
                    ');'
            self.execute(query)

