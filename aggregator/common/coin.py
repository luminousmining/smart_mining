from common import Reward


class Coin:

    def __init__(self):
        self.name = None
        self.tag = None
        self.algorithm = None
        self.reward = Reward()
        self.block_height = None

    def merge(self, other, new_assign: bool = False):
        #######################################################################
        if not new_assign:
            self.name = self.name if self.name else other.name
            self.tag = self.tag if self.tag else other.tag
            self.algorithm = self.algorithm if self.algorithm else other.algorithm
        else:
            self.name = other.name if other.name else self.name
            self.tag = other.tag if other.tag else self.tag
            self.algorithm = other.algorithm if other.algorithm else self.algorithm

        #######################################################################
        self.reward.merge(other.reward, new_assign=new_assign)

    def to_dict(self) -> dict:
        data = dict()

        data['name'] = self.name
        data['tag'] = self.tag
        data['algorithm'] = self.algorithm
        data['reward'] = self.reward.to_dict()
        data['block_height'] = self.block_height

        return data


def update_coin_by_binance(coin: Coin, data: dict) -> None:
    price = data['price']


def update_coin_by_hashrate_no(coin: Coin, data: dict) -> None:
    #######################################################################
    price = data['price']['USD']
    hashrate =  data['network']['hashrate']
    difficulty =  data['network']['difficulty']
    emission =  data['network']['emission']
    emissionUSD =  data['network']['emissionUSD']

    #######################################################################
    coin.reward.usd = float(price) if price else 0
    coin.reward.network_hashrate = float(hashrate) if hashrate else 0
    coin.reward.difficulty = float(difficulty) if difficulty else 0
    coin.reward.emission_coin = float(emission) if emission else 0
    coin.reward.emission_usd = float(emissionUSD) if emissionUSD else 0


def update_coin_by_what_to_mine(coin: Coin, data: dict) -> None:
    #######################################################################
    coin.reward.difficulty = float(data['difficulty'])
    coin.reward.network_hashrate = float(data['nethash'])
    coin.reward.market_cap = float(data['market_cap'].replace('$', '').replace(',', ''))

    #######################################################################
    seconds_by_day = float(86400)
    block_reward = float(data['block_reward'])
    block_time = float(data['block_time'])
    if block_time and block_time > 0.0:
        block_by_day = seconds_by_day / block_time
        coin.reward.emission_coin = block_by_day * block_reward


def update_coin_by_minerstat(coin: Coin, data: dict) -> None:
    #######################################################################
    coin.reward.usd = float(data['price']) if data['price'] != -1 else coin.reward.usd
    coin.reward.network_hashrate = float(data['network_hashrate']) if data['network_hashrate'] != -1 else coin.reward.network_hashrate
    coin.reward.difficulty = float(data['difficulty']) if data['difficulty'] != -1 else coin.reward.difficulty


def update_coin_by_coingecko(coin: Coin, usd: float) -> None:
    coin.reward.usd = float(usd)


def update_coin_by_explorer(coin: Coin, network_hashrate: float, difficulty: float, block_height: int) -> None:
    if network_hashrate:
        coin.reward.network_hashrate = float(network_hashrate)
    if difficulty:
        coin.reward.difficulty = float(difficulty)
    if block_height:
        coin.block_height = int(block_height)
