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
        'algorithm': 'Autolykos',
        'price': {
            'USD': 1.5,
        },
        'network': {
            'emission': 72.0,
            'emissionUSD': 88.56,
            'hashrate': '4000000.0',
            'difficulty': '999999.0',
        },
    }


def _make_what_to_mine_data():
    return {
        'algorithm': 'KawPow',
        'difficulty': '999999.0',
        'nethash': '4000000.0',
        'market_cap': '$200,000,000',
        'block_reward': '15.0',
        'block_time': '120.0',
    }


class TestUpdateCoinByHashrateNo(unittest.TestCase):

    def test_updates_algorithm(self):
        coin = _make_coin(algorithm=None)
        update_coin_by_hashrate_no(coin, _make_hashrate_no_data())
        self.assertEqual(coin.algorithm, 'autolykos')

    def test_updates_emission_coin(self):
        coin = _make_coin()
        update_coin_by_hashrate_no(coin, _make_hashrate_no_data())
        self.assertAlmostEqual(coin.reward.emission_coin, 72.0)

    def test_updates_emission_usd(self):
        coin = _make_coin()
        update_coin_by_hashrate_no(coin, _make_hashrate_no_data())
        self.assertAlmostEqual(coin.reward.emission_usd, 88.56)

    def test_does_not_update_price(self):
        coin = _make_coin()
        coin.reward.usd = 5.0
        update_coin_by_hashrate_no(coin, _make_hashrate_no_data())
        self.assertEqual(coin.reward.usd, 5.0)

    def test_sets_difficulty_and_hashrate_as_fallback(self):
        coin = _make_coin()
        update_coin_by_hashrate_no(coin, _make_hashrate_no_data())
        self.assertEqual(coin.reward.difficulty, 999999.0)
        self.assertEqual(coin.reward.network_hashrate, 4_000_000.0)

    def test_does_not_override_existing_difficulty_and_hashrate(self):
        coin = _make_coin()
        coin.reward.difficulty = 111.0
        coin.reward.network_hashrate = 222.0
        update_coin_by_hashrate_no(coin, _make_hashrate_no_data())
        self.assertEqual(coin.reward.difficulty, 111.0)
        self.assertEqual(coin.reward.network_hashrate, 222.0)


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
