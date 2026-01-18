class Pool:

    def __init__(self) -> None:
        self.name = None
        self.website = None
        self.founded = None
        self.coins = {}

    def merge(self, other) -> None:
        if other.name and self.name != other.name:
            self.name = other.name
        if other.website and self.website != other.website:
            self.website = other.website
        if other.founded and self.founded != other.founded:
            self.founded = other.founded

        if not self.coins and other.coins:
            self.coins = other.coins
        else:
            for coin in self.coins.keys():
                if coin in other.coins[coin]:
                    self.coins[coin] = other.coins[coin]
            for coin in other.coins.keys():
                self.coins[coin] = other.coins[coin]
