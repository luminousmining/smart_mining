from common import (
    Block
)


class CoinPool:

    def __init__(self):
        self.name = None
        self.tag = None
        self.hashrate = None
        self.total_miner = None

    def merge(self, other, new_assign: bool = False):
        #######################################################################
        if not new_assign:
            self.tag = self.tag if self.tag else other.tag
            self.hashrate = self.hashrate if self.hashrate else other.hashrate
            self.total_miner = self.total_miner if self.total_miner else other.total_miner
        else:
            self.tag = other.tag if other.tag else self.tag
            self.hashrate = other.hashrate if other.hashrate else self.hashrate
            self.total_miner = other.total_miner if other.total_miner else self.total_miner

    def to_dict(self) -> dict:
        data = dict()

        data['tag'] = self.tag
        data['hashrate'] = self.hashrate
        data['total_miner'] = self.total_miner

        return data


class Pool:

    def __init__(self) -> None:
        self.name = None
        self.coins = {}
        self.blocks = {}

    def merge(self, other) -> None:
        if other.name and self.name != other.name:
            self.name = other.name

        for coin in other.coins.values():
            self.updade_coin(coin)

        for block in other.blocks.values():
            self.updade_block(block)

    def update_coin(self, coin: CoinPool) -> None:
        if coin.tag not in self.coins:
            self.coins[coin.tag] = coin
            return
        self.coins[coin.tag].merge(coin)

    def update_block(self, block: Block) -> None:
        if block.tag not in self.blocks:
            self.blocks[block.tag] = []
            self.blocks[block.tag].append(block)
            return

        for it_block in self.blocks[block.tag]:
            if it_block.tag == block.tag and it_block.height == block.height:
                it_block.merge(block)
                return

        self.blocks[block.tag].append(block)
