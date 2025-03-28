import json
import os.path
import logging

from api import ApiHTTP
from config import ConfigAPI


class BinanceAPI(ApiHTTP):

    def __init__(self, config: ConfigAPI, folder_output: str):
        super().__init__(config.host, config.api_key)
        self.use_api = config.use_api
        self.dump_file = config.dump_file
        self.path_dump_file = os.path.join(folder_output, 'binance')
        self.path_dump_price = os.path.join(self.path_dump_file, 'price')
        self.path_dump_avg_price = os.path.join(self.path_dump_file, 'avg_price')

        if not os.path.exists(self.path_dump_file):
            os.makedirs(self.path_dump_file)

        if not os.path.exists(self.path_dump_price):
            os.makedirs(self.path_dump_price)

        if not os.path.exists(self.path_dump_avg_price):
            os.makedirs(self.path_dump_avg_price)

    def get_symbols(self) -> dict:
        output_file = os.path.join(self.path_dump_file, self.dump_file)

        if self.use_api:
            symbols = self.get('api/v3/exchangeInfo')['symbols']
            logging.debug(f'Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(symbols, fd, indent=4)
            return symbols
        else:
            logging.debug(f'Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_price(self, symbol: str) -> dict:
        output_file = os.path.join(self.path_dump_price, f'{symbol}.json')

        if self.use_api:
            price = self.get(f'api/v3/ticker/price?symbol={symbol}')
            logging.debug(f'Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(price, fd, indent=4)
            return price
        else:
            with open(output_file) as fd:
                return json.load(fd)

    def get_avg_price(self, symbol: str) -> dict:
        output_file = os.path.join(self.path_dump_avg_price, f'{symbol}.json')

        if self.use_api:
            avg_price = self.get(f'api/v3/avgPrice?symbol={symbol}')
            logging.debug(f'Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(avg_price, fd, indent=4)
            return avg_price
        else:
            with open(output_file) as fd:
                return json.load(fd)
