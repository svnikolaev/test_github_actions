import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from run_service import BASEDIR
except ModuleNotFoundError:
    BASEDIR = Path(__file__).parents[2]
    sys.path.insert(0, str(BASEDIR))
from connectors.somiac import Somiac
from connectors.telegram import send_message

logger = logging.getLogger(__name__)


def prepare_message_text(data: dict, mentioned_user: str) -> str:
    data_date = data['date'].strftime('%d.%m.%Y')

    message = [
        f'🦠 *Данные по звонкам Covid-19 за {data_date}:*',
        f'🔵 Количество звонков: {data["number_of_covid_calls"]} (шт.)',
    ]

    _status = '🟢' if data['number_of_no_answered_calls'] == 0 else '🔴'
    message.append(f'{_status} Неотвеченные вызовы: '
                   f'{data["number_of_no_answered_calls"]} (шт.)')

    _status = '🟢' if data['maximum_waiting_time'] < 3 else '🔴'
    message.append(f'{_status} Максимальное время ожидания: '
                   f'{data["maximum_waiting_time"]} (мин.)')

    if mentioned_user and data["maximum_waiting_time"] >= 3:
        # need to escape underscore symbol "_" if exists in username
        mentioned_user = mentioned_user.replace('\\_', '_').replace('_', '\\_')
        mentioned_user = mentioned_user.replace('@', '')
        message.append(f'@{mentioned_user} ВНИМАНИЕ! Максимальное время '
                       'ожидания больше 3х минут')

    return '\n'.join(message)


def main(config: dict) -> None:
    logger.debug(f'Config dict: {config}')

    switch_off_using_proxy = True
    if switch_off_using_proxy:
        domain = '10.6.0.160'
        os.environ['NO_PROXY'] = domain
        logger.debug(f'Switch off proxy for {domain}')

    a_somiac = Somiac(url='10.6.0.160', user_agent='OSA-RBot-2.0')
    yesterday = datetime.now() - timedelta(days=1)
    covid_calls_data = a_somiac.get_covid_calls_statistic(date=yesterday)

    mentioned_user = config['telegram'].get('mentioned_user')
    message = prepare_message_text(covid_calls_data, mentioned_user)
    r = send_message(bot_token=config['telegram'].get('bot_token'),
                     chat_id=config['telegram'].get('chat_id'),
                     data=message)
    logger.debug(f'Sending message to telegram status: {r.status_code}')
    if r.status_code == 200:
        logger.info('Information has been successfully sent to Telegram')


if __name__ == "__main__":
    from utils import via_run_service
    via_run_service(
        BASEDIR,
        service_name=Path(__file__).parent.name,
        args='nt'
    )
