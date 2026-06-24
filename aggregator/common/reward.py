import logging


class Reward:

    def __init__(self) -> None:
        self.usd = None
        self.usd_sec = None
        self.difficulty = None
        self.network_hashrate = None
        self.hash_usd = None
        self.emission_coin = None
        self.emission_usd = None
        self.market_cap = None

    def merge(self, other, new_assign: bool = False) -> None:
        #######################################################################
        self.set_usd(other.usd, new_assign)
        self.set_usd_sec(other.usd_sec, new_assign)
        self.set_difficulty(other.difficulty, new_assign)
        self.set_network_hashrate(other.network_hashrate, new_assign)
        self.set_hash_usd(other.hash_usd, new_assign)
        self.set_emission_coin(other.emission_coin, new_assign)
        self.set_emission_usd(other.emission_usd, new_assign)
        self.set_market_cap(other.market_cap, new_assign)

    def set_usd(self, new_value, new_assign: bool = False) -> None:
        if not new_assign:
            self.usd = self.usd if self.usd else new_value
        else:
            self.usd = new_value if new_value else self.usd

    def set_usd_sec(self, new_value, new_assign: bool = False) -> None:
        if not new_assign:
            self.usd_sec = self.usd_sec if self.usd_sec else new_value
        else:
            self.usd_sec = new_value if new_value else self.usd_sec

    def set_difficulty(self, new_value, new_assign: bool = False) -> None:
        if not new_assign:
            self.difficulty = self.difficulty if self.difficulty else new_value
        else:
            self.difficulty = new_value if new_value else self.difficulty

    def set_network_hashrate(self, new_value, new_assign: bool = False) -> None:
        if not new_assign:
            self.network_hashrate = self.network_hashrate if self.network_hashrate else new_value
        else:
            self.network_hashrate = new_value if new_value else self.network_hashrate

    def set_hash_usd(self, new_value, new_assign: bool = False) -> None:
        if not new_assign:
            self.hash_usd = self.hash_usd if self.hash_usd else new_value
        else:
            self.hash_usd = new_value if new_value else self.hash_usd

    def set_emission_coin(self, new_value, new_assign: bool = False) -> None:
        if not new_assign:
            self.emission_coin = self.emission_coin if self.emission_coin else new_value
        else:
            self.emission_coin = new_value if new_value else self.emission_coin

    def set_emission_usd(self, new_value, new_assign: bool = False) -> None:
        if not new_assign:
            self.emission_usd = self.emission_usd if self.emission_usd else new_value
        else:
            self.emission_usd = new_value if new_value else self.emission_usd

    def set_market_cap(self, new_value, new_assign: bool = False) -> None:
        if not new_assign:
            self.market_cap = self.market_cap if self.market_cap else new_value
        else:
            self.market_cap = new_value if new_value else self.market_cap

    def update(self) -> None:
        self.__calc_emission_usd()
        self.__calc_usd_sec()
        self.__calc_hash_sec()

    def __calc_emission_usd(self) -> None:
        if not self.emission_coin or not self.usd:
            return
        self.emission_usd = self.emission_coin * self.usd

    def __calc_usd_sec(self) -> None:
        if not self.emission_usd:
            return

        seconds_by_day = float(86400)
        self.usd_sec = self.emission_usd / seconds_by_day

    def __calc_hash_sec(self) -> None:
        if not self.network_hashrate:
            return
        if not self.emission_usd:
            return
        
        self.hash_usd = self.emission_usd / self.network_hashrate

    def to_dict(self) -> dict:
        data = dict()

        data['usd'] = self.usd
        data['usd_sec'] = self.usd_sec
        data['difficulty'] = self.difficulty
        data['network_hashrate'] = self.network_hashrate
        data['hash_usd'] = self.hash_usd
        data['emission_coin'] = self.emission_coin
        data['emission_usd'] = self.emission_usd
        data['market_cap'] = self.market_cap

        return data
