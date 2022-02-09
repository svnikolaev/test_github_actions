import json
import logging.config
from pathlib import Path

DEPARTMENT_NAME = 'osa'
SERVER_LOGS_PATH = Path('/var/log').joinpath(DEPARTMENT_NAME)
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'logfmt': {
            'format': 'ts=%(asctime)s level=%(levelname)s msg="%(message)s"',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
        'logfmt_debug': {
            'format': 'ts=%(asctime)s level=%(levelname)s module="%(name)s" '
                      'msg="%(message)s"',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
        'json': {
            'format': json.dumps({
                'ts': '%(asctime)s',
                'level': '%(levelname)s',
                'module': '%(name)s',
                'msg': '%(message)s',
            }),
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    'handlers': {
        'stdout_info': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'logfmt',
            'stream': 'ext://sys.stdout',
        },
        'stdout_debug': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'logfmt_debug',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'root': {'level': 'INFO', 'handlers': ['stdout_info']},
    },
}


def get_logfile_path(name: str) -> Path:
    service_name = file_name = name
    local_logs_dir = Path(__file__).parent.joinpath('logs')
    path = SERVER_LOGS_PATH if SERVER_LOGS_PATH.exists() else local_logs_dir
    path = path.joinpath(service_name)
    path.mkdir(parents=True, exist_ok=True)
    return path.joinpath(file_name)


def init_logger(name, verbose=False, json=False, nologfile=False):
    file_ext = 'json.log' if json else 'log'
    root_handlers = LOGGING_CONFIG['loggers']['root']['handlers']
    logfile = not nologfile
    if logfile:
        logfile_conf = {'class': 'logging.handlers.RotatingFileHandler',
                        'level': 'DEBUG',
                        'formatter': 'logfmt',
                        'backupCount': 2,
                        'encoding': 'UTF-8',
                        'filename': f'{get_logfile_path(name)}.{file_ext}'}
        LOGGING_CONFIG['handlers'].update(logfile=logfile_conf)
        root_handlers.append('logfile')
    if verbose:
        LOGGING_CONFIG['loggers']['root'].update(level='DEBUG')
        root_handlers[root_handlers.index('stdout_info')] = 'stdout_debug'
    if json:
        for handler in LOGGING_CONFIG['handlers'].values():
            handler.update(formatter='json')
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(name)
    return logger
