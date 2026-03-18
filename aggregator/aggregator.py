import logging
import argparse

from config import Config
from common import AGGREGATOR_MODE
from apps import (
    run_application,
    run_standalone
)


def initialize_logger(level: str) -> None:
    log_level = logging.DEBUG

    if level == 'debug':
        log_level = logging.DEBUG
    elif level == 'warn':
        log_level = logging.WARNING
    elif level == 'error':
        log_level = logging.ERROR
    elif level == 'info':
        log_level = logging.INFO

    formatter = logging.Formatter(
        fmt='[%(levelname)s][%(asctime)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('aggregator.log')
    file_handler.setFormatter(formatter)

    logging.basicConfig(level=log_level, handlers=[console_handler, file_handler])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config', '-c',
        default='config.json'
    )
    parser.add_argument(
        '--mode', '-m',
        default=AGGREGATOR_MODE.STANDALONE,
        choices=[AGGREGATOR_MODE.STANDALONE , AGGREGATOR_MODE.APPLICATION]
    )
    args = parser.parse_args()

    project_config = Config(args.config)
    project_mode = args.mode

    initialize_logger(project_config.log)

    logging.info('🚀 Start aggregator!')
    try:
        if project_mode == AGGREGATOR_MODE.STANDALONE:
            run_standalone(project_config)
        elif project_mode == AGGREGATOR_MODE.APPLICATION:
            run_application(project_config)
        else:
            logging.error(f'Project mode unknow: {project_mode}!')
    except Exception as err:
        logging.exception(f'💥 Unhandled exception: {err}')
else:
    print('USAGE\npython3 aggregator.py')
