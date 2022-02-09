import logging
from datetime import datetime
from json import JSONDecodeError
from typing import Optional

from connectors.zeal_request import request_with_retries as request
from requests import ConnectTimeout

logger = logging.getLogger(__name__)


class Somiac:
    def __init__(self, url: str, user_agent: Optional[str] = None) -> None:
        logger.debug('Initialize Somiac instance')
        self.host = url
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'  # noqa E501

    def get_covid_calls_statistic(self, date: datetime) -> dict:
        """[summary]

        Args:
            date (datetime): for which getting the statistic data

        Returns:
            dict: {
                "operators_per_shift": 8,
                "day": 6,
                "night": 2,
                "number_of_covid_calls": 14,
                "average_talk_time": 2.6,
                "maximum_waiting_time": 2.5,
                "average_waiting_time": 1,
                "waiting_more_than_3_minutes": 0,
                "switch_to_doctor": 100,
                "doctors_appointments": 0,
                "registration_for_tests": 0,
                "doctor_call": 0,
                "ambulance_call": 0,
                "volunteer_call": 0,
                "other": 0,
                "number_of_no_answered_calls": 1,
                "covid_directions": 3,
                "date": datetime.datetime(2022, 1, 20, 21, 1, 49, 634746)
            }
        """
        logger.debug('Getting covid calls statistic data')
        _date = date.strftime('%Y-%m-%d')
        logger.debug(f'Getting covid calls statistic on {_date}')
        url = 'http://' + self.host \
            + f'/statistics/get-tasks-doctor-covid-by-date?createdOn={_date}'
        headers = {
            'Host': self.host,
            'User-Agent': self.user_agent,
            # 'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = request('GET', url, headers=headers)
        r.raise_for_status()
        covid_calls_statistic = r.json()
        covid_calls_statistic.update(date=date)
        return covid_calls_statistic

    def check_health(self) -> bool:
        logger.debug('Checking Somiac service health')
        try:
            data = self.get_covid_calls_statistic(datetime.now())
        except JSONDecodeError:
            logger.warning('Response can not be parsed as JSON')
            return False
        except ConnectTimeout:
            logger.warning('Connection timeout')
            return False

        if not data or not isinstance(data, dict):
            return False
        response_keys = ('operators_per_shift',
                         'day',
                         'night',
                         'number_of_covid_calls',
                         'average_talk_time',
                         'maximum_waiting_time',
                         'average_waiting_time',
                         'waiting_more_than_3_minutes',
                         'switch_to_doctor',
                         'doctors_appointments',
                         'registration_for_tests',
                         'doctor_call',
                         'ambulance_call',
                         'volunteer_call',
                         'other',
                         'number_of_no_answered_calls',
                         'covid_directions')
        for key in response_keys:
            if key not in data.keys():
                return False
        return True
