import unittest

from common.reward import Reward


class TestRewardSetUsd(unittest.TestCase):

    def test_keep_mode_fills_empty_field(self):
        reward = Reward()
        reward.set_usd(1.23)
        self.assertEqual(reward.usd, 1.23)

    def test_keep_mode_preserves_existing(self):
        reward = Reward()
        reward.usd = 1.23
        reward.set_usd(9.99)
        self.assertEqual(reward.usd, 1.23)

    def test_assign_mode_overwrites_with_new_value(self):
        reward = Reward()
        reward.usd = 1.23
        reward.set_usd(9.99, new_assign=True)
        self.assertEqual(reward.usd, 9.99)

    def test_assign_mode_keeps_existing_when_new_value_empty(self):
        reward = Reward()
        reward.usd = 1.23
        reward.set_usd(None, new_assign=True)
        self.assertEqual(reward.usd, 1.23)


class TestRewardSetMarketCap(unittest.TestCase):

    def test_keep_mode_fills_empty_field(self):
        reward = Reward()
        reward.set_market_cap(200_000_000.0)
        self.assertEqual(reward.market_cap, 200_000_000.0)

    def test_keep_mode_preserves_existing(self):
        reward = Reward()
        reward.market_cap = 200_000_000.0
        reward.set_market_cap(999.0)
        self.assertEqual(reward.market_cap, 200_000_000.0)

    def test_assign_mode_overwrites_with_new_value(self):
        reward = Reward()
        reward.market_cap = 200_000_000.0
        reward.set_market_cap(999.0, new_assign=True)
        self.assertEqual(reward.market_cap, 999.0)

    def test_assign_mode_keeps_existing_when_new_value_empty(self):
        reward = Reward()
        reward.market_cap = 200_000_000.0
        reward.set_market_cap(0, new_assign=True)
        self.assertEqual(reward.market_cap, 200_000_000.0)


def _make_full_reward():
    reward = Reward()
    reward.usd = 1.0
    reward.usd_sec = 2.0
    reward.difficulty = 3.0
    reward.network_hashrate = 4.0
    reward.hash_usd = 5.0
    reward.emission_coin = 6.0
    reward.emission_usd = 7.0
    reward.market_cap = 8.0
    return reward


class TestRewardMerge(unittest.TestCase):

    def test_keep_mode_fills_only_empty_fields(self):
        base = Reward()
        base.usd = 1.23
        other = _make_full_reward()

        base.merge(other)

        self.assertEqual(base.usd, 1.23)
        self.assertEqual(base.difficulty, 3.0)
        self.assertEqual(base.market_cap, 8.0)
        self.assertEqual(base.emission_coin, 6.0)

    def test_assign_mode_overwrites_existing_values(self):
        base = _make_full_reward()
        other = Reward()
        other.usd = 99.0
        other.market_cap = 12345.0

        base.merge(other, new_assign=True)

        self.assertEqual(base.usd, 99.0)
        self.assertEqual(base.market_cap, 12345.0)
        self.assertEqual(base.difficulty, 3.0)
        self.assertEqual(base.emission_coin, 6.0)


if __name__ == '__main__':
    unittest.main()
