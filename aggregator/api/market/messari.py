import json
import os.path
import logging

from api import ApiHTTP
from config import ConfigAPI


#https://docs.messari.io/api-reference/endpoints/metrics/
class MessariAPI(ApiHTTP):

    # /metrics/v2/assets/details is capped at 20 assets per request.
    PAGE_SIZE = 20
    # Bound the number of requests to stay within the free tier (30/min, 2k/day).
    # 25 pages => top 500 assets by circulating market cap.
    MAX_PAGES = 25

    def __init__(self, config: ConfigAPI, folder_output: str):
        super().__init__(config.host, config.api_key)
        self.use_api = config.use_api
        self.path_dump_file = os.path.join(folder_output, 'messari')
        self.dump_file_assets = os.path.join(self.path_dump_file, 'assets.json')

        if self.use_api and config.api_key:
            self.update_header('X-Messari-API-Key', self.api_key)

        if not os.path.exists(self.path_dump_file):
            os.makedirs(self.path_dump_file)

    def get_assets(self) -> dict:
        output_file = self.dump_file_assets

        if self.use_api and self.api_key:
            # The details endpoint returns at most PAGE_SIZE assets, so paginate
            # by descending market cap and accumulate into a single payload.
            data = []
            for page in range(1, self.MAX_PAGES + 1):
                body = self.get(
                    f'assets/details?page={page}&limit={self.PAGE_SIZE}'
                    '&sort=circulating-marketcap&order=desc'
                )
                rows = body.get('data') if body else None
                if not rows:
                    break
                data.extend(rows)
                if len(rows) < self.PAGE_SIZE:
                    break

            assets = {'data': data}
            logging.debug(f'📥 Dumping in {output_file}')
            with open(output_file, 'w') as fd:
                json.dump(assets, fd, indent=4)
            return assets
        else:
            logging.debug(f'🔍 Read dump {output_file}')
            with open(output_file) as fd:
                return json.load(fd)
