import logging
import requests


class ApiHTTP:

    def __init__(self, host: str, api_key: str):
        self.host = host
        self.api_key = api_key
        self.headers = { "Accept": "application/json" }

    def update_header(self, key: str, value: any) -> None:
        self.headers[key] = value

    def get(self, target: str, header: dict = {}) -> dict:
        try:
            if target[0] != '/' and self.host[-1] != '/':
                target = f'/{target}'
            endpoint = f'{self.host}{target}'
            response = requests.get(endpoint, headers=self.headers)
            logging.debug(f'🌐 endpoint: [{endpoint}] - [{response.status_code}]')
            body = response.json()
            return body
        except Exception as err:
            logging.error(f'{self.host}{target}: {err}')
        return {}
