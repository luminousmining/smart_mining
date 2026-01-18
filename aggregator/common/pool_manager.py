import os
import json
import logging


from common import Pool


class PoolManager:

    def __init__(self):
        self._pools = {}

    def dump(self, folder_output: str) -> None:
        path_folder = os.path.join(folder_output, 'pool_manager')
        if os.path.exists(path_folder) is False:
            os.makedirs(path_folder)
        output_file = os.path.join(path_folder, 'data.json')

        logging.info(f'📥 Dumping coins in {output_file}')

        data = {}
        for pool_name, pool_value in self._pools.items():
            data[pool_name] = {
                'website': pool_value.website,
                'founded': pool_value.founded,
                'coins': []
            }
            for coin_value in pool_value.coins.values():
                data[pool_name]['coins'].append(coin_value)

        with open(output_file, 'w') as fd:
            json.dump(data, fd, indent=4)

    def insert(self, pool: Pool) -> None:
        if pool.name in self._pools:
            self._pools[pool.name].merge(pool)
        else:
            self._pools[pool.name] = pool
