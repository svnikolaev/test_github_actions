import logging
from typing import Optional

from connectors.zeal_request import request_with_retries as request
from requests.models import Response

logger = logging.getLogger(__name__)


def send_message(bot_token: str, chat_id: str, data: str,
                 parse_mode: Optional[str] = 'markdown') -> Response:
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {'chat_id': chat_id,
              'text': data,
              'parse_mode': parse_mode}
    r = request('GET', url, params=params)
    if r.status_code != 200:
        logger.error("Problem with connection to Telegram")
    r.raise_for_status()
    return r
