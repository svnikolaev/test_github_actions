import logging
from time import sleep
from typing import Optional
from requests import Session, RequestException
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from requests.models import Response

DEFAULT_TIMEOUT = (1, 300)  # seconds for (send, receive)
RETRIES = 3

logger = logging.getLogger(__name__)


def request_with_retries(method: str,
                         url: str,
                         retries: Optional[int] = RETRIES,
                         **kwargs: dict) -> Response:
    """Wrapper over a requests.request() function with timeout and retries

    Usage::

      >>> from zeal_request import request_with_retries as request
      >>> req = request('GET', 'https://httpbin.org/get')
      >>> req
      <Response [200]>
    """

    _error = None
    if 'timeout' not in kwargs:
        kwargs.update(timeout=(DEFAULT_TIMEOUT))
    with Session() as session:
        for i in range(1, retries+1):
            seconds = round(4 * i / retries) if i < retries else 0
            try:
                logger.debug(f'Request attempt {i} of {retries}')
                r = session.request(method=method, url=url, **kwargs)
                r.raise_for_status()
                return r
            except RequestException as e:
                _error = e
                sleep(seconds)
    raise RequestException(_error)


def request_with_retries_complicated(method: str,
                                     url: str,
                                     retries: Optional[int] = RETRIES,
                                     **kwargs: dict) -> Response:
    """Wrapper over a requests.request() function with timeout and retries

    Usage::

      >>> from zeal_request import request_with_retries as request
      >>> req = request('GET', 'https://httpbin.org/get')
      >>> req
      <Response [200]>
    """

    if 'timeout' not in kwargs:
        kwargs.update(timeout=(DEFAULT_TIMEOUT))
    with Session() as session:
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            # status_forcelist=[429, 500, 502, 503, 504],
            status_forcelist=[*range(400, 600)],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        return session.request(method=method, url=url, **kwargs)
