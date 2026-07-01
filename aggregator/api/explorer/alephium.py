import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class AlephiumExplorerAPI(ExplorerBaseAPI):
    """
    Alephium official backend explorer.
    Host: https://backend.mainnet.alephium.org
    The backend exposes no difficulty endpoint; hashrate comes from the hashrate chart.
    Response: list of [{ "timestamp": <ms>, "hashrate": <string, H/s> }] — take the last element.
    """

    def get_hashrates(self, from_ts: int, to_ts: int) -> list:
        output_file = os.path.join(self.path_dump, 'hashrates.json')

        if self.use_api:
            target = f'/charts/hashrates?fromTs={from_ts}&toTs={to_ts}&interval-type=hourly'
            data = self.get(target)
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
