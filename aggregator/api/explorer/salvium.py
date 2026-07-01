import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class SalviumExplorerAPI(ExplorerBaseAPI):
    """
    Salvium block explorer (Monero-fork, onion-style API).
    Host: https://explorer.salvium.io
    Response: { "data": { "difficulty": <string>, "hash_rate": <int, H/s> }, "status": "success" }
    """

    def get_network_info(self) -> dict:
        output_file = os.path.join(self.path_dump, 'networkinfo.json')

        if self.use_api:
            data = self.get('/api/networkinfo')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
