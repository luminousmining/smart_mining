import logging
import requests


class ApiHTTP:

    def __init__(self, host: str, api_key: str):
        self.host = host
        self.api_key = api_key

    def get(self, target: str) -> dict:
        try:
            if target[0] != '/' and self.host[-1] != '/':
                target = f'/{target}'
            endpoint = f'{self.host}{target}'
            logging.debug(f'endpoint: {endpoint}')
            response = requests.get(endpoint)
            body = response.json()
            return body
        except Exception as err:
            logging.error(f'{self.host}{target}: {err}')
        return {}
