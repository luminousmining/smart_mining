import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class ConfluxExplorerAPI(ExplorerBaseAPI):
    """
    Conflux blockchain explorer (ConfluxScan).
    Docs: https://api.confluxscan.io/doc
    """

    def get_stats(self) -> dict:
        output_file = os.path.join(self.path_dump, 'stats.json')

        if self.use_api:
            data = self.get('/statistics/mining')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
