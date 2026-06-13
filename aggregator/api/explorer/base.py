import os

from api.api_http import ApiHTTP


class ExplorerBaseAPI(ApiHTTP):

    def __init__(self, host: str, use_api: bool, folder_output: str, coin_tag: str) -> None:
        super().__init__(host, api_key='')
        self.use_api = use_api
        self.path_dump = os.path.join(folder_output, 'explorer', coin_tag)
        os.makedirs(self.path_dump, exist_ok=True)
