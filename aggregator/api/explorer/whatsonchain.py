import json
import logging
import os

from api.explorer.base import ExplorerBaseAPI


class WhatsOnChainAPI(ExplorerBaseAPI):
    """
    Bitcoin SV explorer (WhatsOnChain).
    Host: https://api.whatsonchain.com/v1/bsv/main
    Response: chain info with `difficulty`. No hashrate field is exposed, so the caller
    derives it via hashrate = difficulty * 2**32 / block_time (600s).
    Docs: https://docs.taal.com/core-products/whatsonchain
    """

    def get_chain_info(self) -> dict:
        output_file = os.path.join(self.path_dump, 'chain_info.json')

        if self.use_api:
            data = self.get('/chain/info')
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
