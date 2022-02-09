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


def main(config: dict):
    logger.info(f'service {__name__} logger.info testing: {template_sting}')
    logger.debug(f'service {__name__} logger.debug testing: {template_sting}')
    a = 10 / 0  # intentional error FOR TESTING purpose
    print(a)


if __name__ == '__main__':
    from utils import via_run_service
    via_run_service(
        BASEDIR,
        service_name=Path(__file__).parent.name,
        # args='nt'
    )
