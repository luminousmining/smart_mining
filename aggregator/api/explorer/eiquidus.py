import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class EIquidusExplorerAPI(ExplorerBaseAPI):
    """
    Generic eIquidus explorer (Bitcoin-Core-family coins).
    Used for: dingo (explorer.dingocoin.com), pep (pepeblocks.com), rxd (radiantexplorer.com).
    Two endpoints, each returning a bare numeric body (H/s for hashrate):
      /api/getdifficulty     -> difficulty
      /api/getnetworkhashps  -> network hashrate (H/s)
    A browser User-Agent is set because some instances (pepeblocks) are behind Cloudflare.
    """

    def __init__(self, host: str, use_api: bool, folder_output: str, coin_tag: str) -> None:
        super().__init__(host, use_api, folder_output, coin_tag)
        self.update_header('User-Agent', 'Mozilla/5.0')

    def get_difficulty(self) -> 'float | None':
        return self.__fetch('/api/getdifficulty', 'difficulty.json')

    def get_network_hashrate(self) -> 'float | None':
        return self.__fetch('/api/getnetworkhashps', 'network_hashrate.json')

    def __fetch(self, target: str, filename: str) -> 'float | None':
        output_file = os.path.join(self.path_dump, filename)

        if self.use_api:
            data = self.get(target)
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
