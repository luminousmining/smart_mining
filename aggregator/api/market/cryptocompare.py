import json
import os.path
import logging

from api import ApiHTTP
from config import ConfigAPI


# https://min-api.cryptocompare.com (free tier requires API key)
class CryptoCompareAPI(ApiHTTP):

    def __init__(self, config: ConfigAPI, folder_output: str):
        super().__init__(config.host, config.api_key)
        self.use_api = config.use_api
        self.path_dump_file = os.path.join(folder_output, 'cryptocompare')
        self.dump_file_prices = os.path.join(self.path_dump_file, 'prices.json')

        if self.use_api and config.api_key:
            self.update_header('Authorization', f'Apikey {self.api_key}')

        if not os.path.exists(self.path_dump_file):
            os.makedirs(self.path_dump_file)

    def get_prices(self, symbols: str) -> dict:
        output_file = self.dump_file_prices

        if self.use_api and self.api_key:
            prices = self.get(f'data/pricemultifull?fsyms={symbols}&tsyms=USD')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(prices, fd, indent=4)
            return prices
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
