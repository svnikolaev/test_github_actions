import argparse
import configparser
import importlib
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

from app_logger import init_logger

logger = logging.getLogger(__name__)
BASEDIR = Path().resolve()


def service_runner(service: str, testing: Optional[bool] = False):
    logger.debug(f'testing: {testing}')
    config = get_config(service, testing)
    try:
        module = importlib.import_module(f'services.{service}.service')
    except ImportError:
        logger.error(f'No module \'{service}\' found')
        logger.debug(
            f'ImportError:\n{traceback.format_exc()}'.replace('"', '\'')
        )
    else:
        module.main(config)


def read_cli_arguments():
    parser = argparse.ArgumentParser(description='Choose service to start')
    parser.add_argument('service', help='choose service to start',
                        metavar='Service', type=str, nargs='?')
    parser.add_argument('-v', '--verbose', help='be verbose',
                        action='store_true', dest='verbose')
    parser.add_argument('-j', '--json', help='use json format for logging',
                        action='store_true', dest='json')
    parser.add_argument('-n', '--nologfile', help='do not create a logfile',
                        action='store_true', dest='nologfile')
    parser.add_argument('-t', '--test', help='use testing config',
                        action='store_true', dest='testing')
    return parser.parse_args(), parser


def get_config(service: str, testing: Optional[bool] = False) -> dict:
    config_parser, config = configparser.ConfigParser(), {}
    if testing:
        config_path = Path(f'services/{service}/config.test.ini')
    else:
        config_path = Path(f'services/{service}/config.ini')
    config_parser.read(config_path)
    for item in config_parser:
        if item == 'DEFAULT': continue  # noqa E701 skip empty DEFAULT block
        config[item] = dict(config_parser[item])
    # logger.debug(f'config dict: {config}')
    return config


def main():
    args, args_parser = read_cli_arguments()
    if not args.service:
        args_parser.print_help()
        modules = [  # get list of available services
            Path(module).name for module  # module is a name of folder
            in BASEDIR.joinpath('services').iterdir()  # in "services" dir
            if module.joinpath('service.py').exists()  # which has "service.py"
        ]
        print('\n' + 'available services:' + '\n  '
              + '\n  '.join(sorted(modules)) + '\n')
        return

    init_logger(args.service,
                verbose=args.verbose,
                json=args.json,
                nologfile=args.nologfile)
    dt_start = datetime.now()
    logger.debug(f'START at {dt_start}')
    logger.debug(f'comandline arguments: {args}')

    try:
        service_runner(args.service, args.testing or False)
    except Exception:
        logger.error(
            f'uncaught exception:\n{traceback.format_exc()}'.replace('"', '\'')
            .replace('\n', '\\n')  # for oneline log format
        )

    logger.debug(f'END at {datetime.now()}, '
                 f'elapsed {datetime.now() - dt_start}')


if __name__ == '__main__':
    main()
