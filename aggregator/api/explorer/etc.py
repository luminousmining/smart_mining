import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class ETCExplorerAPI(ExplorerBaseAPI):
    """
    Ethereum Classic blockchain explorer (Blockscout).
    Docs: https://etc.blockscout.com/api-docs
    """

    def get_stats(self) -> dict:
        output_file = os.path.join(self.path_dump, 'stats.json')

        if self.use_api:
            data = self.get('/api/v2/stats')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
