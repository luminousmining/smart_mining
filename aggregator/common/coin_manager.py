import os
import json
import time
import logging

from common import Coin


class CoinManager:

    def __init__(self) -> None:
        self._coins = dict()
        self._algorithms = list()

    def show(self) -> None:
        for _, coin in self._coins.items():
            logging.info(f'{coin.name}: {coin.tag},{coin.algorithm}')

    def dump(self, folder_output: str) -> None:
        ###########################################################################
        logging.info('===== COIN MANAGER =====')

        #######################################################################
        start_time = time.time()

        ###########################################################################
        path_folder = os.path.join(folder_output, 'coin_manager')
        if os.path.exists(path_folder) is False:
            os.makedirs(path_folder)
        output_file = os.path.join(path_folder, 'data.json')

        ###########################################################################
        logging.info(f'📥 Dumping coins in {output_file}')
        coins = dict()
        for coin in self._coins.values():
            coins[coin.name] = coin.to_dict()

        ###########################################################################
        data = {
            'algorithms': self._algorithms,
            'coins': coins
        }

        ###########################################################################
        with open(output_file, 'w') as fd:
            json.dump(data, fd, indent=4)

        ###########################################################################
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')

    def insert(self, coin: Coin, new_assign: bool = False) -> None:
        if coin.name in self._coins:
            self._coins[coin.name].merge(coin, new_assign)
        else:
            for _, data in self._coins.items():
                if data.tag == coin.tag:
                    data.merge(coin)
                    return
            self._coins[coin.name] = coin

    def get(self, coin_name: str) -> Coin:
        if coin_name in self._coins:
            return self._coins[coin_name]
        return None

    def get_from_tag(self, tag: str) -> Coin:
        for _, coin in self._coins.items():
            if coin.tag.lower() == tag.lower():
                return coin
        return None

    def update(self) -> None:
        keys_to_remove  = list()

        for key, coin in self._coins.items():
            reward = coin.reward
            reward.update()

            if not reward.emission_usd or reward.emission_usd <= float(0.0):
                keys_to_remove.append(key)
            elif not reward.market_cap:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            logging.debug(f'🔥 Need fix coin {key} -> {self._coins[key].to_dict()}')

        for _, coin in self._coins.items():
            if coin.algorithm not in self._algorithms:
                self._algorithms.append(coin.algorithm)

