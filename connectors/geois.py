import json
import logging
from datetime import datetime
from typing import Optional

from connectors.zeal_request import request_with_retries as request

logger = logging.getLogger(__name__)


class Geois:
    def __init__(self,
                 url: str,
                 client_id: str,
                 client_secret: str,
                 user_agent: Optional[str] = None) -> None:
        logger.debug('Initialize Geois instance')
        self.access_token = None
        self.host = url
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'  # noqa E501

    def get_access_token(self) -> str:
        if self.access_token:
            return self.access_token
        url = 'https://' + self.host + '/connect/token'
        payload = 'grant_type=client_credentials&scope=jasperApi' \
                  f'&client_id={self.client_id}' \
                  f'&client_secret={self.client_secret}'
        # content_length = str(len(payload))
        headers = {
            'Host': self.host,
            'User-Agent': self.user_agent,
            # 'Content-Length': content_length,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        logger.debug('Getting access token')
        r = request("POST", url, headers=headers, data=payload)
        r.raise_for_status()
        return r.json().get('access_token')

    def get_rights(self) -> list:
        logger.debug('Getting rights')
        access_token = self.get_access_token()
        url = 'https://' + self.host + '/api/v1/rights'
        headers = {
            'Host': self.host,
            'User-Agent': self.user_agent,
            'Authorization': f'Bearer {access_token}'
        }
        r = request('GET', url, headers=headers)
        r.raise_for_status()
        return r.json()

    def check_health(self) -> bool:
        logger.debug('Checking health')
        url = 'https://' + self.host + '/health'
        headers = {
            'Host': self.host,
            'User-Agent': self.user_agent,
        }
        r = request('GET', url, headers=headers)
        if r.status_code == 200 and r.text == 'Healthy':
            return True
        return False

    def get_unauth_waste_disposal_sites(self,
                                        date_from: datetime,
                                        date_to: datetime) -> list:
        access_token = self.get_access_token()
        url = 'https://' + self.host + '/api/v1/entities/region' \
              '/SafeUnauthWasteDisposalSiteActing'
        payload = json.dumps({
            "operator": "and",
            "criterions": [
                {"operator": "gte",
                             "property": {"alias": "DateInsertField",
                                          "type": "field"},
                             "value": date_from.strftime('%Y-%m-%dT00:00:00')},
                {"operator": "lte",
                             "property": {"alias": "DateInsertField",
                                          "type": "field"},
                             "value": date_to.strftime('%Y-%m-%dT23:59:59')}
            ]
        })
        headers = {
            'Host': self.host,
            'User-Agent': self.user_agent,
            'Authorization': f'Bearer {access_token}',
            'content-type': 'application/json',
        }
        logger.debug(
            f'Getting unauth waste disposal sites from {date_from.date()} '
            f'to {date_to.date()}'
        )
        r = request('POST', url, headers=headers, data=payload)
        r.raise_for_status()
        return r.json()
