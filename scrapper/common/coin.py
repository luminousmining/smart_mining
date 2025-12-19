from common import Reward


class Coin:

    def __init__(self):
        self.name = None
        self.tag = None
        self.algorithm = None
        self.reward = Reward()

    def merge(self, other, new_assign: bool = False):
        if not new_assign:
            self.name = self.name if self.name else other.name
            self.tag = self.tag if self.tag else other.tag
            self.algorithm = self.algorithm if self.algorithm else other.algorithm
        else:
            self.name = other.name if other.name else self.name
            self.tag = other.tag if other.tag else self.tag
            self.algorithm = other.algorithm if other.algorithm else self.algorithm

        self.reward.merge(other.reward, new_assign=new_assign)

    def to_dict(self) -> dict:
        data = dict()

        data['name'] = self.name
        data['tag'] = self.tag
        data['algorithm'] = self.algorithm
        data['reward'] = self.reward.to_dict()

        return data


def create_coin_by_hashrate_no(data: dict) -> Coin:
    coin = Coin()

    coin.name = data['name'].lower()
    coin.tag = data['ticker'].lower()
    coin.algorithm = data['algorithm'].lower().replace('-', '')

    if coin.tag.lower() == "nicehash":
        return None
    if 'nicehash' in coin.name.lower():
        return None

    price = data['price']['USD']
    hashrate =  data['network']['hashrate']
    difficulty =  data['network']['difficulty']
    emission =  data['network']['emission']
    emissionUSD =  data['network']['emissionUSD']

    reward = Reward()
    reward.usd = float(price) if hashrate else 0
    reward.network_hashrate = float(hashrate) if hashrate else 0
    reward.difficulty = float(difficulty) if difficulty else 0
    reward.emission_coin = float(emission) if emission else 0
    reward.emission_usd = float(emissionUSD) if emissionUSD else 0

    coin.reward = reward

    return coin


def create_coin_by_what_to_mine(name: str, data: dict) -> Coin:
    coin = Coin()

    coin.name = name
    coin.tag = data['tag'].lower()
    coin.algorithm = data['algorithm'].lower().replace('-', '')

    if coin.tag.lower() == "nicehash":
        return None
    if 'nicehash' in coin.name.lower():
        return None

    reward = Reward()
    reward.difficulty = float(data['difficulty'])
    reward.network_hashrate = float(data['nethash'])
    m = data['market_cap']
    reward.market_cap = float(data['market_cap'].replace('$', '').replace(',', ''))

    coin.reward = reward

    return coin


def update_coin_by_minerstat(coin: Coin, data: dict) -> None:
    coin.reward.usd = float(data['price']) if data['price'] != -1 else coin.reward.usd
    coin.reward.network_hashrate = float(data['network_hashrate']) if data['network_hashrate'] != -1 else coin.reward.network_hashrate
    coin.reward.difficulty = float(data['difficulty']) if data['difficulty'] != -1 else coin.reward.difficulty
    coin.reward.market_cap = float(data['volume']) if data['volume'] != -1 else coin.reward.market_cap
