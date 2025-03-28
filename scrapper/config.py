import json
import logging


class ConfigAPI:

    def __init__(self, data) -> None:
        self.use_api = data['use_api']
        self.dump_file = data['dump_file']
        self.host = data['host']
        self.api_key = data['api_key']

    def __str__(self) -> str:
        return  f'use_api[{self.use_api}] - '\
                f'dump_file[{self.dump_file}] - '\
                f'host[{self.host}]'


class ConfigAPIS:

    def __init__(self) -> None:
        self.hashrate_no = None
        self.what_to_mine = None
        self.binance = None
        self.minerstat = None


class ConfigDB:

    def __init__(self, data) -> None:
        self.host = data['host']
        self.database = data['database']
        self.username = data['username']
        self.password = data['password']
        self.port = data['port']


class Config:

    def __init__(self, filename):
        with open(filename) as fd:
            data = json.load(fd)

            self.log = data['log']
            self.db = ConfigDB(data['db'])
            self.folder_output = data['folder_output']
            self.proxy_api_host = data['proxy_api_host']

            self.apis = ConfigAPIS()
            if 'api' in data:
                api_obj = data['api']
                self.apis.hashrate_no = ConfigAPI(api_obj['hashrate_no']) if 'hashrate_no' in api_obj else None
                self.apis.what_to_mine = ConfigAPI(api_obj['whattomine']) if 'whattomine' in api_obj else None
                self.apis.binance = ConfigAPI(api_obj['binance']) if 'binance' in api_obj else None
                self.apis.minerstat = ConfigAPI(api_obj['minerstat']) if 'minerstat' in api_obj else None
