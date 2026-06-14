import unittest

from common.coin import Coin, update_coin_by_minerstat


def _make_minerstat_data(volume=1_000_000.0):
    return {
        'price': 45.0,
        'network_hashrate': 500_000_000.0,
        'difficulty': 12_000_000.0,
        'volume': volume,
    }


class TestMinerStatDoesNotCorruptMarketCap(unittest.TestCase):

    def test_market_cap_from_whattomine_is_preserved(self):
        coin = Coin()
        coin.name = 'firo'
        coin.reward.market_cap = 500_000_000.0

        update_coin_by_minerstat(coin, _make_minerstat_data(volume=1_234_567.0))

        self.assertEqual(coin.reward.market_cap, 500_000_000.0)

    def test_market_cap_unchanged_when_minerstat_volume_is_sentinel(self):
        coin = Coin()
        coin.name = 'firo'
        coin.reward.market_cap = 500_000_000.0

        update_coin_by_minerstat(coin, _make_minerstat_data(volume=-1))

        self.assertEqual(coin.reward.market_cap, 500_000_000.0)


if __name__ == '__main__':
    unittest.main()
