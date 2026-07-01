import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class BlockchairExplorerAPI(ExplorerBaseAPI):
    """
    Generic Blockchair explorer. The chain is embedded in the configured host,
    e.g. host = 'https://api.blockchair.com/dogecoin'.
    Used for: bch, doge, dash, zec (Sol/s), xec.
    Response: data.difficulty (number) and data.hashrate_24h (string).
    Docs: https://blockchair.com/api/docs
    Note: keyless usage is rate-limited (~30 req/min) — keep the timer >= 60s.
    """

    def get_stats(self) -> dict:
        output_file = os.path.join(self.path_dump, 'stats.json')

        if self.use_api:
            data = self.get('/stats')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
