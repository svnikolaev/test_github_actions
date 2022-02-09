import logging
import sys
from pathlib import Path

try:
    from run_service import BASEDIR
except ModuleNotFoundError:
    BASEDIR = Path(__file__).parents[2]
    sys.path.insert(0, str(BASEDIR))
from connectors.template_connector import template_sting

logger = logging.getLogger(__name__)


def main(config: dict) -> None:
    logger.debug(f'Config dict: {config}')

    try:
        _msg = template_sting
        logger.info(_msg)
    except NameError:
        logger.error('Can not get the template_string')


if __name__ == "__main__":
    from utils import via_run_service
    via_run_service(
        BASEDIR,
        service_name=Path(__file__).parent.name,
        args='nt'
    )
