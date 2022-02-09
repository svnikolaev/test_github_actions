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
from connectors.geois import Geois
from connectors.telegram import send_message

logger = logging.getLogger(__name__)


def count_states(data: list) -> dict:
    data_dict = {'Обнаружено сегодня': 0,
                 'Обнаружено с начала года': len(data),
                 'Устранено': 0,
                 'Подтверждено': 0,
                 'В работе': 0,
                 'Просрочено': {'Устранено': 0,
                                'Подтверждено': 0,
                                'В работе': 0}}
    for row in data:
        if (datetime.strptime(
                row['Fields']['DateInsertField'], "%Y-%m-%dT%H:%M:%S.%f"
                        ).date() == datetime.now().date()):
            data_dict['Обнаружено сегодня'] += 1

        if row['Fields']['Status'] == 1000010003640069:
            data_dict['Устранено'] += 1
        elif (row['Fields']['Status'] == 1000010003638937
              or row['Fields']['Status'] == 1000010003638936
              or row['Fields']['Status'] == 1000010003640068):
            data_dict['В работе'] += 1

        if row['Fields']['StatusCheck'] == 1000010003645659:
            data_dict['Подтверждено'] += 1

        if row['Fields']['Wasted'] == 1:
            if row['Fields']['Status'] == 1000010003638937:
                data_dict['Просрочено']['В работе'] += 1
            if row['Fields']['Status'] == 1000010003640069:
                data_dict['Просрочено']['Устранено'] += 1
            if row['Fields']['Status'] == 1000010003682268:
                data_dict['Просрочено']['Подтверждено'] += 1

    return data_dict


def get_current_info(config: dict) -> str:
    current_year = datetime.now().year
    date_from = datetime(year=current_year, month=1, day=1)
    one_day = timedelta(days=1)

    a_geois = Geois(**config['geois'],
                    user_agent=config['general'].get('user_agent'))

    # get first pack of data from 01.01.CURRENT_YEAR to 30.06.CURRENT_YEAR
    data = a_geois.get_unauth_waste_disposal_sites(
        date_from=date_from,
        date_to=date_from.replace(month=7)-one_day
    )
    # get second pack of data from 01.07.CURRENT_YEAR to 31.12.CURRENT_YEAR
    data += a_geois.get_unauth_waste_disposal_sites(
        date_from=date_from.replace(month=7),
        date_to=date_from.replace(year=current_year+1, month=1)-one_day
    )

    counted = count_states(data)

    information = [
        '*🚮Информация о ходе (динамике) работ по внесению и устранению '
                + 'несанкционированных свалок за '  # noqa E131
                + f'{datetime.now().strftime("%d.%m.%Y")}:*',  # noqa E131
        'Обнаружено сегодня: '
                f'*{counted["Обнаружено сегодня"]}*',  # noqa E131
        'Обнаружено накопительным итогом с '
                + f'{date_from.strftime("%d.%m.%Y")}: '  # noqa E131
                + f'*{counted["Обнаружено с начала года"]}*',  # noqa E131
        'Устранено (накопительный итог): '
                + f'*{counted["Устранено"]}*',  # noqa E131
        'Подтверждено: '
                + f'*{counted["Подтверждено"]}*',  # noqa E131
        'В работе (накопительный итог): '
                + f'*{counted["В работе"]}*',  # noqa E131
        '',
        '*Из них, с нарушением сроков:*',
        '1) Устранено (накопительный итог): '
                + f'*{counted["Просрочено"]["Устранено"]}*',  # noqa E131
        '2) Подтверждено (накопительный итог): '
                + f'*{counted["Просрочено"]["Подтверждено"]}*',  # noqa E131
        '3) В работе (накопительный итог): '
                + f'*{counted["Просрочено"]["В работе"]}*'  # noqa E131
    ]

    return '\n'.join(information)


def main(config: dict) -> None:
    logger.debug(f'Config dict: {config}')

    switch_off_using_proxy = True
    if switch_off_using_proxy:
        domain = config['geois'].get('url')
        os.environ['NO_PROXY'] = domain
        logger.debug(f'Switch off proxy for {domain}')

    information = get_current_info(config)
    logger.debug(f'Information:\n{information}')

    r = send_message(bot_token=config['telegram'].get('bot_token'),
                     chat_id=config['telegram'].get('chat_id'),
                     data=information)
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
