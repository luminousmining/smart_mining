import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class ErgoExplorerAPI(ExplorerBaseAPI):
    """
    Ergo blockchain explorer.
    Docs: https://api.ergoplatform.com/api/v1/docs/
    """

    def get_info(self) -> dict:
        output_file = os.path.join(self.path_dump, 'info.json')

        if self.use_api:
            data = self.get('/api/v1/info')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
