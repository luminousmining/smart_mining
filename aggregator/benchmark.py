import os
import time
import random
import logging
import argparse
import matplotlib.pyplot as plt

from pathlib import Path
from config import Config, ConfigBenchmark
from common import (
    Coin,
    Reward,
    CoinManager,
    PostgreSQL
)


class BenchRaw:

    def __init__(self):
        self.coin_name = ''
        self.coin_tag = ''
        self.coin_value = 0.0


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


def __draw_bench(bench: list, folder: str) -> None:
    # Create folder if it doesn't exist
    Path(folder).mkdir(parents=True, exist_ok=True)

    # Check if there is data to display
    if not bench or len(bench) == 0:
        logging.warning("No benchmark data to display")
        return

    # Get all bench_names (e.g., 'emission_usd', 'hash_usd')
    bench_names = list(bench[0].keys())

    # Create a chart for each bench_name
    for bench_name in bench_names:
        # Dictionary to store data for each coin
        # coin_tag -> {x: [loop_indices], y: [ranking positions]}
        coin_data = {}

        # Collect data for each loop iteration
        for loop_index, loop_data in enumerate(bench):
            if bench_name not in loop_data:
                continue

            # Iterate through coins with their ranking position (1-indexed)
            for rank_position, raw in enumerate(loop_data[bench_name], start=1):
                if raw.coin_tag not in coin_data:
                    coin_data[raw.coin_tag] = {'x': [], 'y': [], 'name': raw.coin_name}

                coin_data[raw.coin_tag]['x'].append(loop_index)
                coin_data[raw.coin_tag]['y'].append(rank_position)

        # Create the figure
        plt.figure(figsize=(12, 8))

        # Plot a line for each coin
        for coin_tag, data in coin_data.items():
            plt.plot(data['x'], data['y'], marker='o', label=f"{data['name']} ({coin_tag})", linewidth=2)

        # Configure the chart
        plt.xlabel('Loop Index', fontsize=12, fontweight='bold')
        plt.ylabel('Ranking Position', fontsize=12, fontweight='bold')
        plt.title(f'Benchmark: {bench_name}', fontsize=14, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        
        # Invert Y axis so rank 1 is at the top
        plt.gca().invert_yaxis()
        
        # Set Y axis to show integer values only
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        plt.tight_layout()

        # Save the chart
        filename = os.path.join(folder, f'bench_{bench_name}.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        logging.info(f'Chart saved: {filename}')


def get_base_data(pg: PostgreSQL) -> CoinManager:
    manager = CoinManager()

    raw = pg.request_all('SELECT * FROM coins')

    logging.debug(f'🔍 Listing of coins:')
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

        logging.debug(f'🔍 {coin.tag.upper()}')

    return manager


def __append_result(data: dict, filter: list, pg: PostgreSQL, bench_name: str, function_name: str) -> None:
    data[bench_name] = []

    rows = pg.request_all(f'select * FROM {function_name}()')
    for name, tag, value in rows:
        if tag.lower() in filter:
            raw = BenchRaw()
            raw.coin_name = name
            raw.coin_tag = tag
            raw.coin_value = value
            data[bench_name].append(raw)


def benchmark(config: ConfigBenchmark, pg: PostgreSQL, coin_manager: CoinManager) -> None:

    bench_ffps = []
    for loop_index in range(0, config.loop):
        # Print benchmark number iteration
        logging.info(f'Benchmark[{loop_index + 1}/{config.loop}]:')

        # Apply random factor on all coins
        for name, coin in coin_manager._coins.items():
            # Skip coin not follow
            if coin.tag.lower() not in config.filter_coins:
                continue

            current_coin = Coin()
            current_coin.merge(coin)

            # Get random factor
            factor_emission = random.uniform(config.factor_network_min, config.factor_emission_max) / 100
            factor_network = random.uniform(config.factor_network_min, config.factor_emission_max) / 100

            if coin.tag in config.factor_emission_custom:
                factor_custom = config.factor_emission_custom[coin.tag.lower()]
                factor_custom_min = factor_custom['min']
                factor_custom_max = factor_custom['max']
                factor_emission = random.uniform(factor_custom_min, factor_custom_max)

            if coin.tag in config.factor_network_custom:
                factor_custom = config.factor_network_custom[coin.tag.lower()]
                factor_custom_min = factor_custom['min']
                factor_custom_max = factor_custom['max']
                factor_network = random.uniform(factor_custom_min, factor_custom_max)

            # Update coin value
            current_coin.reward.emission_usd = max(0.0, ((100.0 + factor_emission) * current_coin.reward.emission_usd) / 100)
            current_coin.reward.network_hashrate = max(0.0, ((100.0 + factor_network) * current_coin.reward.network_hashrate) / 100)
            logging.info(f'[{coin.tag}] | USD({coin.reward.emission_usd}) -> USD({current_coin.reward.emission_usd}) | NetHash({coin.reward.network_hashrate}) -> NetHash({current_coin.reward.network_hashrate})')

            coin_manager.insert(current_coin, new_assign=True)

        # Update Database
        logging.info('🔄 Updating Database!')
        pg._update_coin(coin_manager)

        # Get Profiles result
        bench_ffps.append({})
        __append_result(bench_ffps[loop_index], config.filter_coins, pg, 'emission_usd', 'profile_emission_usd')
        __append_result(bench_ffps[loop_index], config.filter_coins, pg, 'hash_ud', 'profile_hash_usd')

    __draw_bench(bench_ffps, os.path.join('benchmark', 'ffps'))


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
