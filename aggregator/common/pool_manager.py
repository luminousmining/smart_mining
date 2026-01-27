import os
import json
import time
import logging


from common import Pool


class PoolManager:

    def __init__(self):
        self._pools = {}

    def dump(self, folder_output: str) -> None:
        ###########################################################################
        logging.info('===== POOL MANAGER DUMP =====')

        #######################################################################
        path_folder = os.path.join(folder_output, 'pool_manager')
        if os.path.exists(path_folder) is False:
            os.makedirs(path_folder)
        output_file = os.path.join(path_folder, 'data.json')

        #######################################################################
        start_time = time.time()

        #######################################################################
        logging.info(f'📥 Dumping coins in {output_file}')
        data = {}
        for pool_name, pool_value in self._pools.items():
            data[pool_name] = {
                'name': pool_value.name,
                'coins': {},
                'blocks': {}
            }
            for coin_value in pool_value.coins.values():
                data[pool_name]['coins'][coin_value.tag] = coin_value.to_dict()
            for tag, blocks in pool_value.blocks.items():
                data[pool_name]['blocks'][tag] = []
                for block in blocks:
                    data[pool_name]['blocks'][block.tag].append(block.to_dict())

        #######################################################################
        with open(output_file, 'w') as fd:
            json.dump(data, fd, indent=4)

        #######################################################################
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')

    def update_pool(self, pool: Pool) -> None:
        #######################################################################
        if pool.name in self._pools:
            self._pools[pool.name].merge(pool)
        else:
            self._pools[pool.name] = pool

    def get_pool(self, name: str) -> Pool:
        return self._pools.get(name, None)

    def update(self):
        ###########################################################################
        logging.info('===== POOL MANAGER UPDATE =====')

        #######################################################################
        start_time = time.time()

        #######################################################################
        duration = time.time() - start_time
        logging.info(f'🕐 synchro in {duration:.2f} seconds')
