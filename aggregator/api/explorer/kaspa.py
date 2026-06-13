import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class KaspaExplorerAPI(ExplorerBaseAPI):
    """
    Kaspa blockchain explorer.
    Docs: https://api.kaspa.org/docs
    """

    def get_hashrate(self) -> dict:
        output_file = os.path.join(self.path_dump, 'hashrate.json')

        if self.use_api:
            data = self.get('/info/hashrate')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_blockdag(self) -> dict:
        output_file = os.path.join(self.path_dump, 'blockdag.json')

        if self.use_api:
            data = self.get('/info/blockdag')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
