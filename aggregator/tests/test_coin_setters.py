import unittest

from common.coin import Coin


class TestCoinSetName(unittest.TestCase):

    def test_keep_mode_fills_empty_field(self):
        coin = Coin()
        coin.set_name('ergo')
        self.assertEqual(coin.name, 'ergo')

    def test_keep_mode_preserves_existing(self):
        coin = Coin()
        coin.name = 'ergo'
        coin.set_name('kaspa')
        self.assertEqual(coin.name, 'ergo')

    def test_assign_mode_overwrites_with_new_value(self):
        coin = Coin()
        coin.name = 'ergo'
        coin.set_name('kaspa', new_assign=True)
        self.assertEqual(coin.name, 'kaspa')

    def test_assign_mode_keeps_existing_when_new_value_empty(self):
        coin = Coin()
        coin.name = 'ergo'
        coin.set_name('', new_assign=True)
        self.assertEqual(coin.name, 'ergo')


class TestCoinSetTag(unittest.TestCase):

    def test_keep_mode_fills_empty_field(self):
        coin = Coin()
        coin.set_tag('erg')
        self.assertEqual(coin.tag, 'erg')

    def test_keep_mode_preserves_existing(self):
        coin = Coin()
        coin.tag = 'erg'
        coin.set_tag('kas')
        self.assertEqual(coin.tag, 'erg')

    def test_assign_mode_overwrites_with_new_value(self):
        coin = Coin()
        coin.tag = 'erg'
        coin.set_tag('kas', new_assign=True)
        self.assertEqual(coin.tag, 'kas')

    def test_assign_mode_keeps_existing_when_new_value_empty(self):
        coin = Coin()
        coin.tag = 'erg'
        coin.set_tag('', new_assign=True)
        self.assertEqual(coin.tag, 'erg')


class TestCoinSetAlgorithm(unittest.TestCase):

    def test_keep_mode_fills_empty_field(self):
        coin = Coin()
        coin.set_algorithm('autolykos')
        self.assertEqual(coin.algorithm, 'autolykos')

    def test_keep_mode_preserves_existing(self):
        coin = Coin()
        coin.algorithm = 'autolykos'
        coin.set_algorithm('kheavyhash')
        self.assertEqual(coin.algorithm, 'autolykos')

    def test_assign_mode_overwrites_with_new_value(self):
        coin = Coin()
        coin.algorithm = 'autolykos'
        coin.set_algorithm('kheavyhash', new_assign=True)
        self.assertEqual(coin.algorithm, 'kheavyhash')

    def test_assign_mode_keeps_existing_when_new_value_empty(self):
        coin = Coin()
        coin.algorithm = 'autolykos'
        coin.set_algorithm('', new_assign=True)
        self.assertEqual(coin.algorithm, 'autolykos')


if __name__ == '__main__':
    unittest.main()
