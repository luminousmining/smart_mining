import json
import os.path
import logging

from api import ApiHTTP
from config import ConfigAPI


class MinerStatAPI(ApiHTTP):

    def __init__(self, config: ConfigAPI, folder_output: str):
        super().__init__(config.host, config.api_key)
        self.use_api = config.use_api
        self.path_dump_file = os.path.join(folder_output, 'minerstat')
        self.dump_file_coins = os.path.join(self.path_dump_file, 'coins.json')
        self.dump_file_hardware =  os.path.join(self.path_dump_file, 'hardware.json')
        self.dump_file_pool =  os.path.join(self.path_dump_file, 'pool.json')

        if self.use_api and config.api_key:
            self.update_header('X-API-Key', self.api_key)

        if not os.path.exists(self.path_dump_file):
            os.makedirs(self.path_dump_file)

    def get_coins(self) -> dict:
        output_file = self.dump_file_coins

        if self.use_api:
            coins = self.get('/v2/coins')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(coins, fd, indent=4)
            return coins['data']
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_hardware(self) -> dict:
        output_file = self.dump_file_hardware

        if self.use_api:
            hardwares = self.get('v2/hardware')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(hardwares, fd, indent=4)
            return hardwares
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_pools(self) -> dict:
        output_file = self.dump_file_pool

        if self.use_api:
            pools = self.get('/v2/pools')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(pools, fd, indent=4)
            return pools
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
