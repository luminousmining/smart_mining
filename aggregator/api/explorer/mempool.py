import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class MempoolExplorerAPI(ExplorerBaseAPI):
    """
    Generic mempool.space-family explorer (self-hosted instances share the same API).
    Used for: btc (mempool.space), ltc (litecoinspace.org), fb (mempool.fractalbitcoin.io).
    Docs: https://mempool.space/docs/api/rest
    """

    def get_hashrate(self) -> dict:
        output_file = os.path.join(self.path_dump, 'hashrate.json')

        if self.use_api:
            data = self.get('/api/v1/mining/hashrate/3d')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_price(self) -> dict:
        output_file = os.path.join(self.path_dump, 'price.json')

        if self.use_api:
            data = self.get('/api/v1/prices')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
