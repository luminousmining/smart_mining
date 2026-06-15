import unittest
from common.coin import Coin, update_coin_by_hashrate_no, update_coin_by_what_to_mine


def _make_coin(tag='erg', name='ergo', algorithm='autolykos'):
    coin = Coin()
    coin.name = name
    coin.tag = tag
    coin.algorithm = algorithm
    return coin


def _make_hashrate_no_data():
    return {
        'price': {'USD': 1.23},
        'network': {
            'hashrate': 5_000_000.0,
            'difficulty': 1_200_000.0,
            'emission': 72.0,
            'emissionUSD': 88.56,
        },
    }


def _make_what_to_mine_data():
    return {
        'difficulty': '999999.0',
        'nethash': '4000000.0',
        'market_cap': '$200,000,000',
        'block_reward': '15.0',
        'block_time': '120.0',
    }


class TestUpdateCoinByHashrateNo(unittest.TestCase):

    def test_updates_price(self):
        coin = _make_coin()
        update_coin_by_hashrate_no(coin, _make_hashrate_no_data())
        self.assertEqual(coin.reward.usd, 1.23)

    def test_updates_network_fields(self):
        coin = _make_coin()
        update_coin_by_hashrate_no(coin, _make_hashrate_no_data())
        self.assertEqual(coin.reward.network_hashrate, 5_000_000.0)
        self.assertEqual(coin.reward.difficulty, 1_200_000.0)

    def test_preserves_market_cap(self):
        coin = _make_coin()
        coin.reward.market_cap = 200_000_000.0
        update_coin_by_hashrate_no(coin, _make_hashrate_no_data())
        self.assertEqual(coin.reward.market_cap, 200_000_000.0)


class TestUpdateCoinByWhatToMine(unittest.TestCase):

    def test_updates_market_cap(self):
        coin = _make_coin()
        update_coin_by_what_to_mine(coin, _make_what_to_mine_data())
        self.assertEqual(coin.reward.market_cap, 200_000_000.0)

    def test_updates_network_fields(self):
        coin = _make_coin()
        update_coin_by_what_to_mine(coin, _make_what_to_mine_data())
        self.assertEqual(coin.reward.difficulty, 999999.0)
        self.assertEqual(coin.reward.network_hashrate, 4_000_000.0)

    def test_emission_coin_calculated_from_block_data(self):
        coin = _make_coin()
        update_coin_by_what_to_mine(coin, _make_what_to_mine_data())
        # block_time=120s -> 720 blocks/day x 15 reward = 10800
        self.assertAlmostEqual(coin.reward.emission_coin, 10800.0)

    def test_preserves_price(self):
        coin = _make_coin()
        coin.reward.usd = 1.23
        update_coin_by_what_to_mine(coin, _make_what_to_mine_data())
        self.assertEqual(coin.reward.usd, 1.23)


if __name__ == '__main__':
    unittest.main()
