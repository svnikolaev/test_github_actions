import logging
import sys
from pathlib import Path

from requests import HTTPError

try:
    from run_service import BASEDIR
except ModuleNotFoundError:
    BASEDIR = Path(__file__).parents[2]
    sys.path.insert(0, str(BASEDIR))
from connectors.geois import Geois
from connectors.telegram import send_message

logger = logging.getLogger(__name__)


def main(config: dict) -> None:
    logger.debug(f'Config dict: {config}')

    a_geois = Geois(**config['geois'],
                    user_agent=config['general'].get('user_agent'))

    try:
        service_is_healthy = a_geois.check_health()
    except HTTPError:
        logger.debug('Problem with GeoIS service: HTTPError')
        service_is_healthy = False

    if not service_is_healthy:
        _msg = 'Problem with GeoIS service'
        logger.critical(_msg)

        need_to_warn_by_telegram = False
        if need_to_warn_by_telegram:
            r = send_message(bot_token=config['telegram'].get('bot_token'),
                             chat_id=config['telegram'].get('chat_id'),
                             data=_msg)
            logger.debug(f'Sending msg to telegram status: {r.status_code}')
    else:
        _msg = 'GeoIS service is OK'
        logger.info(_msg)


if __name__ == "__main__":
    from utils import via_run_service
    via_run_service(
        BASEDIR,
        service_name=Path(__file__).parent.name,
        args='nt'
    )
