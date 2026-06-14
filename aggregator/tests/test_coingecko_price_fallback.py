import unittest

from common.coin import Coin, update_coin_by_coingecko


class TestUpdateCoinByCoingecko(unittest.TestCase):

    def test_coin_without_price_receives_coingecko_price(self):
        coin = Coin()
        coin.name = 'kaspa'
        coin.reward.usd = None
        update_coin_by_coingecko(coin, 0.15)
        self.assertAlmostEqual(coin.reward.usd, 0.15)

    def test_coin_with_existing_price_is_overwritten(self):
        coin = Coin()
        coin.name = 'firo'
        coin.reward.usd = 45.0
        update_coin_by_coingecko(coin, 1.44)
        self.assertAlmostEqual(coin.reward.usd, 1.44)


if __name__ == '__main__':
    unittest.main()
