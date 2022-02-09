import logging
import os
import sys
from pathlib import Path

from requests import HTTPError

try:
    from run_service import BASEDIR
except ModuleNotFoundError:
    BASEDIR = Path(__file__).parents[2]
    sys.path.insert(0, str(BASEDIR))
from connectors.somiac import Somiac
from connectors.telegram import send_message

logger = logging.getLogger(__name__)


def main(config: dict) -> None:
    logger.debug(f'Config dict: {config}')

    switch_off_using_proxy = True
    if switch_off_using_proxy:
        domain = '10.6.0.160'
        os.environ['NO_PROXY'] = domain
        logger.debug(f'Switch off proxy for {domain}')

    a_somiac = Somiac(url='10.6.0.160', user_agent='OSA-RBot-2.0')

    try:
        service_is_healthy = a_somiac.check_health()
    except HTTPError:
        logger.debug('Covid calls statistic not available: HTTPError')
        service_is_healthy = False

    if not service_is_healthy:
        _msg = 'Problem with SOMIAC service, covid statistics not available'
        logger.critical(_msg)

        need_to_warn_by_telegram = False
        if need_to_warn_by_telegram:
            r = send_message(bot_token=config['telegram'].get('bot_token'),
                             chat_id=config['telegram'].get('chat_id'),
                             data=_msg)
            logger.debug(f'Sending msg to telegram status: {r.status_code}')
    else:
        _msg = 'SOMIAC service is OK'
        logger.info(_msg)


if __name__ == "__main__":
    from utils import via_run_service
    via_run_service(
        BASEDIR,
        service_name=Path(__file__).parent.name,
        args='nt'
    )
