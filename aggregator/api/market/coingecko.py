import json
import os.path
import logging

from api import ApiHTTP
from config import ConfigAPI


# https://www.coingecko.com/en/api
class CoinGeckoAPI(ApiHTTP):

    def __init__(self, config: ConfigAPI, folder_output: str):
        super().__init__(config.host, config.api_key)
        self.use_api = config.use_api
        self.path_dump_file = os.path.join(folder_output, 'coingecko')
        self.dump_file_coins = os.path.join(self.path_dump_file, 'coins.json')

        if self.use_api and config.api_key:
            self.update_header('x-cg-demo-api-key', self.api_key)

        if not os.path.exists(self.path_dump_file):
            os.makedirs(self.path_dump_file)

    def get_coins_list(self) -> dict:
        output_file = self.dump_file_coins

        if self.use_api and self.api_key:
            coins = self.get(f'coins/list')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(coins, fd, indent=4)
            return coins
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
