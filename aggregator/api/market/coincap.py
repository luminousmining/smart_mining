import json
import os.path
import logging

from api import ApiHTTP
from config import ConfigAPI


# https://rest.coincap.io/v3 (v3, free tier requires API key)
class CoinCapAPI(ApiHTTP):

    def __init__(self, config: ConfigAPI, folder_output: str):
        super().__init__(config.host, config.api_key)
        self.use_api = config.use_api
        self.path_dump_file = os.path.join(folder_output, 'coincap')
        self.dump_file_assets = os.path.join(self.path_dump_file, 'assets.json')

        if self.use_api and config.api_key:
            self.update_header('Authorization', f'Bearer {self.api_key}')

        if not os.path.exists(self.path_dump_file):
            os.makedirs(self.path_dump_file)

    def get_assets(self) -> dict:
        output_file = self.dump_file_assets

        if self.use_api and self.api_key:
            assets = self.get('assets?limit=2000')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(assets, fd, indent=4)
            return assets
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
