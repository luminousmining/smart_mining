import unittest

from common.coin import Coin
from common.reward import Reward
from common.coin_manager import CoinManager


def _make_coin(name: str, emission_usd: float, market_cap: float) -> Coin:
    coin = Coin()
    coin.name = name
    coin.tag = name.lower()
    coin.algorithm = 'ethash'
    coin.reward.emission_usd = emission_usd
    coin.reward.market_cap = market_cap
    coin.reward.network_hashrate = 1_000_000.0
    return coin


class TestCoinManagerUpdate(unittest.TestCase):

    def test_invalid_coin_zero_emission_is_removed(self):
        manager = CoinManager()
        manager.insert(_make_coin('badcoin', emission_usd=0.0, market_cap=1_000_000.0))
        manager.update()
        self.assertIsNone(manager.get('badcoin'))

    def test_invalid_coin_no_market_cap_is_removed(self):
        manager = CoinManager()
        manager.insert(_make_coin('nocap', emission_usd=100.0, market_cap=None))
        manager.update()
        self.assertIsNone(manager.get('nocap'))

    def test_valid_coin_is_kept(self):
        manager = CoinManager()
        manager.insert(_make_coin('bitcoin', emission_usd=50_000.0, market_cap=800_000_000_000.0))
        manager.update()
        self.assertIsNotNone(manager.get('bitcoin'))

    def test_mixed_coins_only_valid_remain(self):
        manager = CoinManager()
        manager.insert(_make_coin('valid', emission_usd=200.0, market_cap=5_000_000.0))
        manager.insert(_make_coin('invalid_no_emission', emission_usd=0.0, market_cap=1_000_000.0))
        manager.insert(_make_coin('invalid_no_cap', emission_usd=100.0, market_cap=None))
        manager.update()
        self.assertIsNotNone(manager.get('valid'))
        self.assertIsNone(manager.get('invalid_no_emission'))
        self.assertIsNone(manager.get('invalid_no_cap'))


if __name__ == '__main__':
    unittest.main()
