import unittest


class TestKaspaHashrateNormalization(unittest.TestCase):

    def test_ghs_to_hs_conversion(self):
        hashrate_ghs = 413083.1423084014
        network_hashrate = float(hashrate_ghs) * 1e9
        # 413 083 GH/s → ~413 TH/s → 4.13e14 H/s
        self.assertAlmostEqual(network_hashrate, 4.130831423084014e14, places=0)
        self.assertGreater(network_hashrate, 1e12)   # > 1 TH/s : réseau réaliste

    def test_none_hashrate_stays_none(self):
        _hashrate_ghs = None
        network_hashrate = float(_hashrate_ghs) * 1e9 if _hashrate_ghs is not None else None
        self.assertIsNone(network_hashrate)


if __name__ == '__main__':
    unittest.main()
