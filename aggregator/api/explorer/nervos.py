import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class NervosExplorerAPI(ExplorerBaseAPI):
    """
    Nervos CKB official explorer.
    Host: https://mainnet-api.explorer.nervos.org
    Response: data.attributes.current_epoch_difficulty (string), data.attributes.hash_rate (H/s, string).
    Requires JSON:API headers (application/vnd.api+json) or the API returns HTTP 415.
    Docs: https://explorer.nervos.org
    """

    def __init__(self, host: str, use_api: bool, folder_output: str, coin_tag: str) -> None:
        super().__init__(host, use_api, folder_output, coin_tag)
        self.update_header('Accept', 'application/vnd.api+json')
        self.update_header('Content-Type', 'application/vnd.api+json')

    def get_statistics(self) -> dict:
        output_file = os.path.join(self.path_dump, 'statistics.json')

        if self.use_api:
            data = self.get('/api/v1/statistics')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
