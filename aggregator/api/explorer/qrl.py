import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class QRLExplorerAPI(ExplorerBaseAPI):
    """
    Quantum Resistant Ledger official explorer.
    Host: https://explorer.theqrl.org
    Response: { "difficulty": <string>, "hashrate": <int, H/s>, ... }
    A browser User-Agent is required (the CDN 403s the default UA).
    """

    def __init__(self, host: str, use_api: bool, folder_output: str, coin_tag: str) -> None:
        super().__init__(host, use_api, folder_output, coin_tag)
        self.update_header('User-Agent', 'Mozilla/5.0')

    def get_mining_stats(self) -> dict:
        output_file = os.path.join(self.path_dump, 'miningstats.json')

        if self.use_api:
            data = self.get('/api/miningstats')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
