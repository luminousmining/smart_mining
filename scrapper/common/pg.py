import psycopg2
import logging

from config import Config
from common import CoinManager


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

        return True

    def request(self, query: str):
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        for row in results:
            yield row

    def execute(self, query: str) -> None:
        self.cursor.execute(query)
        self.connection.commit()

    def disconnect(self) -> bool:
        self.cursor.close()
        self.connection.close()
        return True

    def is_connected(self) -> bool:
        if not self.cursor:
            return False
        if not self.connection:
            return False
        return True

    def update(self, coin_manager: CoinManager) -> None:
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
            self.cursor.execute(query)
        self.connection.commit()
