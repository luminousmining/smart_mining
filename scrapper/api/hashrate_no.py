import json
import os.path
import logging

from api import ApiHTTP
from config import ConfigAPI


class HashrateNoAPI(ApiHTTP):

    def __init__(self, config: ConfigAPI, folder_output: str):
        super().__init__(config.host, config.api_key)
        self.use_api = config.use_api
        self.dump_file = config.dump_file
        self.path_dump_file = os.path.join(folder_output, 'hashrate_no')

        if not os.path.exists(self.path_dump_file):
            os.makedirs(self.path_dump_file)

    def get_coins(self) -> dict:
        output_file = os.path.join(self.path_dump_file, self.dump_file)

        if self.use_api and self.api_key:
            coins = self.get(f'v1/coins?apiKey={self.api_key}')
            logging.debug(f'Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(coins, fd, indent=4)
            return coins
        else:
            logging.debug(f'Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
