import json
import logging
import argparse

from config import Config
from common.pg import PostgreSQL


def load_gpus(filepath: str) -> list:
    with open(filepath, 'r') as fd:
        return json.load(fd)


def insert_hardwares(pg: PostgreSQL, gpus: list) -> None:
    total = len(gpus)
    for i, gpu in enumerate(gpus):
        name = gpu.get('name', '').strip()
        if not name:
            continue
        name_escaped = name.replace("'", "''")
        query = f"CALL insert_hardware('{name_escaped}');"
        pg.execute(query)
        if (i + 1) % 100 == 0 or (i + 1) == total:
            logging.info(f'Progress: {i + 1}/{total}')


def main():
    parser = argparse.ArgumentParser(description='Insert GPUs from gpus.json into the hardware table')
    parser.add_argument('--config', default='config.json', help='Path to config.json')
    parser.add_argument('--gpus', default='gpus.json', help='Path to gpus.json')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    config = Config(args.config)
    pg = PostgreSQL(config)

    if not pg.connect():
        logging.error('Failed to connect to database')
        return

    gpus = load_gpus(args.gpus)
    logging.info(f'Loaded {len(gpus)} GPUs from {args.gpus}')

    insert_hardwares(pg, gpus)
    logging.info('Done')

    pg.disconnect()


if __name__ == '__main__':
    main()
