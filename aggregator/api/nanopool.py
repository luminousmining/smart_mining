import json
import os.path
import logging

from api import ApiHTTP
from config import ConfigAPI


# https://apidoc.2miners.com/
class NanopoolAPI(ApiHTTP):

    def __init__(self, config: ConfigAPI, folder_output: str):
        super().__init__(config.host, config.api_key)
        self.use_api = config.use_api
        self.path_dump_file = os.path.join(folder_output, 'nanopool')
        self.dump_file_blocks = os.path.join(self.path_dump_file, 'avg_blocks_time.json')
        self.dump_file_last_block_number = os.path.join(self.path_dump_file, 'last_block_number.json')
        self.dump_file_block_stats = os.path.join(self.path_dump_file, 'block_stats.json')
        self.dump_file_time_next_epoch = os.path.join(self.path_dump_file, 'time_next_epoch.json')
        self.dump_file_approximated_earnings = os.path.join(self.path_dump_file, 'approximated_earnings.json')
        self.dump_file_prices = os.path.join(self.path_dump_file, 'prices.json')

        self.supported_tags = (
            "xmr",
            "rvn",
            "cfx",
            "ergo"
        )

        if not os.path.exists(self.path_dump_file):
            os.makedirs(self.path_dump_file)

    def get_avg_blocks(self) -> dict:
        output_file = self.dump_file_blocks

        if self.use_api:
            rows = {}
            for tag in self.supported_tags:
                raw = self.get(f'{tag}/network/avgblocktime')
                rows[tag] = raw
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(rows, fd, indent=4)
            return rows
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_last_block_number(self) -> dict:
        output_file = self.dump_file_last_block_number

        if self.use_api:
            rows = {}
            for tag in self.supported_tags:
                raw = self.get(f'{tag}/network/lastblocknumber')
                rows[tag] = raw
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(rows, fd, indent=4)
            return rows
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_block_stats(self, offset: int = 0, count: int = 100) -> dict:
        output_file = self.dump_file_block_stats

        if self.use_api:
            rows = {}
            for tag in self.supported_tags:
                raw = self.get(f'{tag}/block_stats/{offset}/{count}')
                rows[tag] = raw
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(rows, fd, indent=4)
            return rows
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_time_next_epoch(self) -> dict:
        output_file = self.dump_file_time_next_epoch

        if self.use_api:
            rows = {}
            for tag in self.supported_tags:
                raw = self.get(f'{tag}/network/timetonextepoch')
                rows[tag] = raw
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(rows, fd, indent=4)
            return rows
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_approximated_earnings(self, hashrate: int = 10000000) -> dict:
        output_file = self.dump_file_approximated_earnings

        if self.use_api:
            rows = {}
            for tag in self.supported_tags:
                raw = self.get(f'{tag}/approximated_earnings/{hashrate}')
                rows[tag] = raw
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(rows, fd, indent=4)
            return rows
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_prices(self) -> dict:
        output_file = self.dump_file_prices

        if self.use_api:
            rows = {}
            for tag in self.supported_tags:
                raw = self.get(f'{tag}/prices')
                rows[tag] = raw
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(rows, fd, indent=4)
            return rows
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
