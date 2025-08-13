import os
import json
import logging


class HardwareManager:

    def __init__(self):
        self._hardwares = []

    def insert(self, name: str, brand: str, speed: float, power: float):
        self._hardwares.append(
            {
                'name': name,
                'brand': brand,
                'speed': speed,
                'power': power
            }
        )

    def dump(self, folder_output: str) -> None:
        path_folder = os.path.join(folder_output, 'hardware_manager')
        if os.path.exists(path_folder) is False:
            os.makedirs(path_folder)
        output_file = os.path.join(path_folder, 'data.json')

        logging.debug(f'Dumping hardware in {output_file}')

        with open(output_file, 'w') as fd:
            json.dump(self._hardwares, fd, indent=4)
