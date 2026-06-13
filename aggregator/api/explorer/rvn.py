import json
import logging
import os

from api.api_jsonrpc import ApiJSONRPC


class RavencoinRPCAPI(ApiJSONRPC):
    """
    Ravencoin blockchain — direct JSON-RPC.
    Public node: https://rvn-rpc-mainnet.ting.finance/rpc (auth: anonymous/anonymous)
    """

    def __init__(self, host: str, use_api: bool, rpc_user: str, rpc_password: str, folder_output: str) -> None:
        super().__init__(host, rpc_user, rpc_password)
        self.use_api = use_api
        self.path_dump = os.path.join(folder_output, 'explorer', 'rvn')
        os.makedirs(self.path_dump, exist_ok=True)

    def get_blockchain_info(self) -> dict:
        output_file = os.path.join(self.path_dump, 'blockchain_info.json')

        if self.use_api:
            data = self.rpc('getblockchaininfo', [])
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_network_hashrate(self) -> 'float | None':
        output_file = os.path.join(self.path_dump, 'network_hashrate.json')

        if self.use_api:
            data = self.rpc('getnetworkhashps', [])
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(data, fd, indent=4)
            return data
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
