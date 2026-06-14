import unittest

from common.reward import Reward


class TestCalcEmissionUsd(unittest.TestCase):

    def test_whattomine_only_calculates_emission_usd(self):
        reward = Reward()
        reward.emission_coin = 572.0
        reward.usd = 1.44
        reward.update()
        self.assertAlmostEqual(reward.emission_usd, 572.0 * 1.44)

    def test_emission_usd_recalculated_with_new_price(self):
        reward = Reward()
        reward.emission_coin = 572.0
        reward.usd = 1.44
        reward.emission_usd = 50_000.0  # ancienne valeur figée
        reward.update()
        self.assertAlmostEqual(reward.emission_usd, 572.0 * 1.44)  # recalculé avec prix Binance

    def test_missing_price_leaves_emission_usd_none(self):
        reward = Reward()
        reward.emission_coin = 572.0
        reward.usd = None
        reward.update()
        self.assertIsNone(reward.emission_usd)


if __name__ == '__main__':
    unittest.main()
