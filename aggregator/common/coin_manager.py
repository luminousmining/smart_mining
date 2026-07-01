import os
import json
import time
import logging

from common import Coin
from common.numeric import _is_nan_or_negative


class CoinManager:

    def __init__(self) -> None:
        self._coins = dict()
        self._algorithms = list()

    def show(self) -> None:
        for _, coin in self._coins.items():
            logging.info(f'{coin.name}: {coin.tag},{coin.algorithm}')

    def dump(self, folder_output: str) -> None:
        ###########################################################################
        logging.info('===== COIN MANAGER DUMP =====')

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
                if coin.tag and data.tag == coin.tag:
                    data.merge(coin, new_assign)
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

    def get_or_create(self, name: str, tag: str) -> Coin:
        coin = self.get_from_tag(tag)
        if coin is None:
            coin = Coin()
            coin.set_tag(tag, True)
            coin.set_name(name, True)
            self.insert(coin)
        return coin

    def get_all(self) -> list:
        return list(self._coins.values())

    def update(self) -> None:
        ###########################################################################
        logging.info('===== COIN MANAGER UPDATE =====')

        keys_to_remove = list()

        for key, coin in self._coins.items():
            if not key or not coin:
                logging.warning(f'⚠️ Coin invalide [{coin.name if coin else "Unknown"}]')
                continue

            reward = coin.reward
            reward.update()

            for attr in ('usd', 'network_hashrate', 'difficulty'):
                val = getattr(reward, attr)
                if _is_nan_or_negative(val):
                    logging.warning(f'⚠️ {key}: {attr}={val} invalide, set to None')
                    setattr(reward, attr, None)

            # Force override name coin
            attr_override = {
                'name': {
                    'arrr': 'pirate chain',
                    'beam': 'beam',
                    'cap':  'capstash',
                    'cfx':  'conflux',
                    'dnx':  'dynex',
                    'epic': 'epic cash',
                    'geod': 'geodnet',
                    'grin': 'grin',
                    'mewc': 'meowcoin',
                    'prl':  'pearl',
                    'qrl':  'quantum resistant ledger',
                    'quai': 'quai',
                }
            }
            coin.name = attr_override['name'].get(coin.tag, coin.name)

            reason = None
            if not reward.emission_usd or reward.emission_usd <= 0.0 or _is_nan_or_negative(reward.emission_usd):
                reason = f'emission_usd invalide ({reward.emission_usd})'
            elif not reward.market_cap or _is_nan_or_negative(reward.market_cap):
                reason = f'market_cap invalide ({reward.market_cap})'

            if reason:
                keys_to_remove.append(key)
                logging.warning(f'🔥 Coin rejected [{key}] — {reason}')

        if keys_to_remove:
            logging.warning(f'⚠️ {len(keys_to_remove)} coins rejected!')
        for key in keys_to_remove:
            del self._coins[key]

        for _, coin in self._coins.items():
            if coin.algorithm not in self._algorithms:
                self._algorithms.append(coin.algorithm)

