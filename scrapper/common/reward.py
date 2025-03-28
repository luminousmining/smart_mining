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

    def merge(self, other) -> None:
        self.usd = self.usd if self.usd else other.usd
        self.usd_sec = self.usd_sec if self.usd_sec else other.usd_sec
        self.difficulty = self.difficulty if self.difficulty else other.difficulty
        self.network_hashrate = self.network_hashrate if self.network_hashrate else other.network_hashrate
        self.hash_usd = self.hash_usd if self.hash_usd else other.hash_usd
        self.emission_coin = self.emission_coin if self.emission_coin else other.emission_coin
        self.emission_usd = self.emission_usd if self.emission_usd else other.emission_usd
        self.market_cap = self.market_cap if self.market_cap else other.market_cap

    def update(self) -> None:
        self.__calc_usd_sec()
        self.__calc_hash_sec()

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
