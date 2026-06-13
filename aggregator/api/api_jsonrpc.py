import logging
import requests
import requests.auth

from api.api_http import ApiHTTP


class ApiJSONRPC(ApiHTTP):

    def __init__(self, host: str, rpc_user: str, rpc_password: str) -> None:
        super().__init__(host, api_key='')
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password

    def rpc(self, method: str, params: list) -> dict:
        body = {
            'jsonrpc': '1.0',
            'id': 'aggregator',
            'method': method,
            'params': params
        }
        try:
            auth = requests.auth.HTTPBasicAuth(self.rpc_user, self.rpc_password)
            response = requests.post(
                self.host,
                json=body,
                auth=auth,
                headers={'Content-Type': 'application/json'}
            )
            logging.debug(f'🌐 rpc [{method}] -> [{response.status_code}]')
            if response.status_code != 200:
                return {}
            data = response.json()
            if data.get('error'):
                logging.error(f'RPC error [{method}]: {data["error"]}')
                return {}
            return data.get('result', {})
        except Exception as err:
            logging.error(f'{self.host} rpc [{method}]: {err}')
        return {}
