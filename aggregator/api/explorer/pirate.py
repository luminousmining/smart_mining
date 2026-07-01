import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class PirateExplorerAPI(ExplorerBaseAPI):
    """
    Pirate Chain explorer (Komodo Insight API).
    Host: https://explorer.pirate.black
    Response: { "difficulty": <number> } — no hashrate exposed (Equihash Sol/s),
    so network_hashrate stays on the hashrate.no fallback.
    A browser User-Agent is required (Cloudflare challenges datacenter IPs otherwise).
    """

    def __init__(self, host: str, use_api: bool, folder_output: str, coin_tag: str) -> None:
        super().__init__(host, use_api, folder_output, coin_tag)
        self.update_header('User-Agent', 'Mozilla/5.0')

    def get_difficulty(self) -> dict:
        output_file = os.path.join(self.path_dump, 'difficulty.json')

        if self.use_api:
            data = self.get('/insight-api-komodo/status?q=getDifficulty')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
