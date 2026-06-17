import json
import os.path
import logging

from api import ApiHTTP
from config import ConfigAPI


# https://pro-api.coinmarketcap.com/v1 (free tier, requires API key)
class CoinMarketCapAPI(ApiHTTP):

    def __init__(self, config: ConfigAPI, folder_output: str):
        super().__init__(config.host, config.api_key)
        self.use_api = config.use_api
        self.path_dump_file = os.path.join(folder_output, 'coinmarketcap')
        self.dump_file_listings = os.path.join(self.path_dump_file, 'listings.json')

        if self.use_api and config.api_key:
            self.update_header('X-CMC_PRO_API_KEY', self.api_key)

        if not os.path.exists(self.path_dump_file):
            os.makedirs(self.path_dump_file)

    def get_listings(self) -> dict:
        output_file = self.dump_file_listings

        if self.use_api and self.api_key:
            listings = self.get('cryptocurrency/listings/latest?limit=5000&convert=USD')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(listings, fd, indent=4)
            return listings
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
