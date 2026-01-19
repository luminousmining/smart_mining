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
        self.coingecko = None


class ConfigDB:

    def __init__(self, data) -> None:
        self.host = data['host']
        self.database = data['database']
        self.username = data['username']
        self.password = data['password']
        self.port = data['port']
        self.update = False if 'update' not in data else data['update']


class ConfigBenchmark:

    def __init__(self, data) -> None:
        self.loop = data['loop']
        self.filter_coins = data['filters']['coins']
        self.factor_emission_min = data['factor']['emission']['min']
        self.factor_emission_max = data['factor']['emission']['max']
        self.factor_network_min = data['factor']['network']['min']
        self.factor_network_max = data['factor']['network']['max']

        self.factor_emission_custom = data['factor']['emission']['custom']

class Config:

    def __init__(self, filename):
        with open(filename) as fd:
            data = json.load(fd)

            self.log = data['log']
            self.db = ConfigDB(data['db'])
            self.folder_output = data['folder_output']

            self.apis = ConfigAPIS()
            if 'api' in data:
                api_obj = data['api']
                self.apis.hashrate_no = ConfigAPI(api_obj['hashrate_no']) if 'hashrate_no' in api_obj else None
                self.apis.what_to_mine = ConfigAPI(api_obj['whattomine']) if 'whattomine' in api_obj else None
                self.apis.binance = ConfigAPI(api_obj['binance']) if 'binance' in api_obj else None
                self.apis.minerstat = ConfigAPI(api_obj['minerstat']) if 'minerstat' in api_obj else None
                self.apis.coingecko = ConfigAPI(api_obj['coingecko']) if 'coingecko' in api_obj else None

            self.benchmark = ConfigBenchmark(data['benchmark']) if 'benchmark' in data else None
