import json
import logging


class ConfigAPI:

    def __init__(self, data) -> None:
        self.use_api = data['use_api']
        self.host = data['host']
        self.api_key = data.get('api_key', '')
        self.rpc_user = data.get('rpc_user', '')
        self.rpc_password = data.get('rpc_password', '')

    def __str__(self) -> str:
        return  f'use_api[{self.use_api}] - '\
                f'host[{self.host}]'


class ConfigAPIS:

    def __init__(self) -> None:
        self.hashrate_no = None
        self.what_to_mine = None
        self.binance = None
        self.minerstat = None
        self.coingecko = None
        self.coinpaprika = None
        self.coinmarketcap = None
        self.coincap = None
        self.messari = None
        self.cryptocompare = None
        self.two_miners = None
        self.nanopool = None
        self.explorer: dict = {}


class ConfigDB:

    def __init__(self, data) -> None:
        self.host = data['host']
        self.database = data['database']
        self.username = data['username']
        self.password = data['password']
        self.port = data['port']
        self.update = False if 'update' not in data else data['update']


class ConfigTimers:

    def __init__(self, data) -> None:
        market = data.get('market', {})
        self.binance = market.get('binance', 8)
        self.coingecko = market.get('coingecko', 20)
        self.coinpaprika = market.get('coinpaprika', 60)
        self.coinmarketcap = market.get('coinmarketcap', 120)
        self.coincap = market.get('coincap', 60)
        self.messari = market.get('messari', 60)
        self.cryptocompare = market.get('cryptocompare', 60)

        mining = data.get('mining', {})
        self.hashrate_no = mining.get('hashrate_no', 3)
        self.what_to_mine = mining.get('what_to_mine', 5)
        self.miner_stat_coin = mining.get('miner_stat', 12)

        pool = data.get('pool', {})
        self.two_miners = pool.get('2miners', 5)
        self.miner_stat_pool = pool.get('miner_stat', 10)
        self.nanopool = pool.get('nanopool', 1)

        managers = data.get('managers', {})
        self.coin_manager = managers.get('coin_manager', 30)
        self.pool_manager = managers.get('pool_manager', 30)
        self.database = managers.get('database', 30)

        explorer = data.get('explorer', {})
        self.explorer_erg = explorer.get('erg', 60)
        self.explorer_kas = explorer.get('kas', 60)
        self.explorer_rvn = explorer.get('rvn', 60)
        self.explorer_xmr = explorer.get('xmr', 120)
        self.explorer_cfx = explorer.get('cfx', 60)
        self.explorer_etc = explorer.get('etc', 60)


class ConfigBenchmark:

    def __init__(self, data) -> None:
        self.loop = data['loop']
        self.filter_coins = data['filters']['coins']
        self.factor_emission_min = data['factor']['emission']['min']
        self.factor_emission_max = data['factor']['emission']['max']
        self.factor_network_min = data['factor']['network']['min']
        self.factor_network_max = data['factor']['network']['max']

        self.factor_emission_custom = data['factor']['emission']['custom']
        self.factor_network_custom = data['factor']['network']['custom']

class Config:

    def __init__(self, filename):
        with open(filename) as fd:
            data = json.load(fd)

            self.log = data['log']
            self.db = ConfigDB(data['db'])
            self.folder_output = data['folder_output']

            self.apis = ConfigAPIS()

            market_obj = data.get('market', {})
            self.apis.binance = ConfigAPI(market_obj['binance']) if 'binance' in market_obj else None
            self.apis.coingecko = ConfigAPI(market_obj['coingecko']) if 'coingecko' in market_obj else None
            self.apis.coinpaprika = ConfigAPI(market_obj['coinpaprika']) if 'coinpaprika' in market_obj else None
            self.apis.coinmarketcap = ConfigAPI(market_obj['coinmarketcap']) if 'coinmarketcap' in market_obj else None
            self.apis.coincap = ConfigAPI(market_obj['coincap']) if 'coincap' in market_obj else None
            self.apis.messari = ConfigAPI(market_obj['messari']) if 'messari' in market_obj else None
            self.apis.cryptocompare = ConfigAPI(market_obj['cryptocompare']) if 'cryptocompare' in market_obj else None

            mining_obj = data.get('mining', {})
            self.apis.hashrate_no = ConfigAPI(mining_obj['hashrate_no']) if 'hashrate_no' in mining_obj else None
            self.apis.what_to_mine = ConfigAPI(mining_obj['whattomine']) if 'whattomine' in mining_obj else None
            self.apis.minerstat = ConfigAPI(mining_obj['miner_stat']) if 'miner_stat' in mining_obj else None

            pool_obj = data.get('pool', {})
            self.apis.two_miners = ConfigAPI(pool_obj['2miners']) if '2miners' in pool_obj else None
            self.apis.nanopool = ConfigAPI(pool_obj['nanopool']) if 'nanopool' in pool_obj else None

            explorer_obj = data.get('explorer', {})
            for tag, cfg in explorer_obj.items():
                self.apis.explorer[tag] = ConfigAPI(cfg)

            self.timers = ConfigTimers(data['timers']) if 'timers' in data else ConfigTimers({})

            self.benchmark = ConfigBenchmark(data['benchmark']) if 'benchmark' in data else None
