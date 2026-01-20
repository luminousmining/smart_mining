import json
import os.path
import logging

from api import ApiHTTP
from config import ConfigAPI


# https://apidoc.2miners.com/
class TwoMinersAPI(ApiHTTP):

    def __init__(self, config: ConfigAPI, folder_output: str):
        super().__init__(config.host, config.api_key)
        self.use_api = config.use_api
        self.dump_file = config.dump_file
        self.path_dump_file = os.path.join(folder_output, '2miners')
        self.dump_file_blocks = os.path.join(self.path_dump_file, 'blocks.json')
        self.dump_file_miners = os.path.join(self.path_dump_file, 'miners.json')
        self.dump_file_stats = os.path.join(self.path_dump_file, 'stats.json')

        self.supported_tags = (
            "ethw",
            "solo-ethw",
            "etc",
            "solo-etc",
            "erg",
            "solo-erg",
            # STOP SUPPORT "clo",
            # STOP SUPPORT "solo-clo",
            "zec",
            "solo-zec",
            # STOP SUPPORT "zen",
            # STOP SUPPORT "solo-zen",
            # STOP SUPPORT "flux",
            # STOP SUPPORT"solo-flux",
            "btg",
            "solo-btg",
            # STOP SUPPORT "xmr",
            # STOP SUPPORT "solo-xmr",
            # STOP SUPPORT "firo",
            # STOP SUPPORT "solo-firo",
            "rvn",
            "solo-rvn",
            "neox",
            "solo-neox",
            "grin",
            "solo-grin",
            "ctxc",
            "solo-ctxc",
            "ae",
            "solo-ae",
            "beam",
            "solo-beam",
            "ckb",
            "solo-ckb"
        )

        if not os.path.exists(self.path_dump_file):
            os.makedirs(self.path_dump_file)

    def get_blocks(self) -> dict:
        output_file = self.dump_file_blocks

        if self.use_api:
            all_blocks = {}
            for tag in self.supported_tags:
                host_override = self.host.replace('<TAG>', tag)
                blocks = self.get('blocks', {}, host_override)
                all_blocks[tag] = blocks
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(all_blocks, fd, indent=4)
            return all_blocks
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_miners(self) -> dict:
        output_file = self.dump_file_miners

        if self.use_api:
            all_miners = {}
            for tag in self.supported_tags:
                host_override = self.host.replace('<TAG>', tag)
                miners = self.get('miners', {}, host_override)
                all_miners[tag] = miners
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(all_miners, fd, indent=4)
            return all_miners
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)

    def get_stats(self) -> dict:
        output_file = self.dump_file_stats

        if self.use_api:
            all_stats = {}
            for tag in self.supported_tags:
                host_override = self.host.replace('<TAG>', tag)
                stats = self.get('stats', {}, host_override)
                all_stats[tag] = stats
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(all_stats, fd, indent=4)
            return all_stats
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
