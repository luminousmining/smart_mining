import time
import random
import logging
import argparse

from config import Config, ConfigBenchmark
from api import (
    BinanceAPI,
    HashrateNoAPI,
    MinerStatAPI,
    WhatToMineAPI
)
from common import (
    Coin,
    Reward,
    CoinManager,
    PostgreSQL
)



def initialize_logger(level: str) -> None:
    log_level = logging.DEBUG

    if level == 'debug':
        log_level = logging.DEBUG
    elif level == 'warn':
        log_level = logging.WARNING
    elif level == 'error':
        log_level = logging.ERROR
    elif level == 'info':
        log_level = logging.INFO

    logging.basicConfig(
        format='[%(levelname)s][%(asctime)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=log_level)


def get_base_data(pg: PostgreSQL) -> CoinManager:
    manager = CoinManager()

    raw = pg.request_all('SELECT * FROM coins')

    logging.info(f'Listing of coins:')
    for _, name, tag, algorithm, usd, usd_sec, difficulty, network_hashrate, hash_usd, emission_coin, emission_usd, market_cap in raw:
        coin = Coin()
        coin.name = name
        coin.tag = tag
        coin.algorithm = algorithm

        reward = Reward()
        reward.usd = float(usd)
        reward.usd_sec = float(usd_sec)
        reward.difficulty = float(difficulty)
        reward.network_hashrate = float(network_hashrate)
        reward.hash_usd = float(hash_usd)
        reward.emission_coin = float(emission_coin)
        reward.emission_usd = float(emission_usd)
        reward.market_cap = float(market_cap)

        coin.reward = reward

        manager.insert(coin)

        logging.info(f'{coin.tag.upper()}')

    return manager


def benchmark(config: ConfigBenchmark, pg: PostgreSQL, coin_manager: CoinManager) -> None:

    for loop in range(0, config.loop):
        # Print benchmark number iteration
        logging.info(f'Benchmark [{loop}/{config.loop}]:')

        # Apply random factor on all coins
        for name, coin in coin_manager._coins.items():
            # Get random factor
            factor_emission = random.uniform(config.factor_network_min, config.factor_emission_max) / 100
            factor_network = random.uniform(config.factor_network_min, config.factor_emission_max) / 100
            factor_difficulty = random.uniform(config.factor_network_min, config.factor_emission_max) / 100

            # Update coin value
            coin.reward.emission_usd = coin.reward.emission_usd + (coin.reward.emission_usd * factor_emission)
            coin.reward.network_hashrate = coin.reward.network_hashrate + (coin.reward.network_hashrate * factor_network)
            coin_manager.insert(coin, new_assign=True)

        # Update Database
        logging.info('Updating Database!')
        pg._update_coin(coin_manager)

        # Wait
        seconds = config.tick_rate_ms / 1000
        logging.info(f'Waiting {seconds}s...')
        time.sleep(seconds)


def run(config: Config):
    logging.info('RUN SIMULATOR')

    # Database Connection
    pg = PostgreSQL(config)
    if not pg.connect():
        return

    # Initialize coins data
    coin_manager = get_base_data(pg)

    # Process benchmark
    benchmark(config.benchmark, pg, coin_manager)

    # Database disconnect
    if pg.is_connected() is True:
        pg.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default='config.json')
    args = parser.parse_args()

    project_config = Config(args.config)
    initialize_logger(project_config.log)
    run(project_config)
