# Мини-фреймворк для задач автоматизации и логирования результатов

Разработать мини-фреймворк для запуска скриптов автоматизации, в том числе задач ETL между разными сервисами.
В процессе необходимо формировать лаконичные логи, их забирает сервис мониторинга, например, в стеке Grafana – Loki - Promtail. В результате заинтересованные лица должны увидеть, успешно сработал скрипт или возникла проблема.
Скрипты запускаются с сервера по крону, либо вручную из консоли.

## Структура проекта

```text
.
└── project_tasks/ - корень проекта
    |
    ├── run_service.py - модуль запуска задач
    ├── app_logger.py - модуль конфигурирования логгера
    ├── utils.py - модуль со вспомогательными алгоритмами
    ├── logs/ - локальная папка с логами
    │
    ├── connectors/ - коннекторы до ИС
    │   ├── ...
    │   ├── telegram.py
    │   ├── geois.py
    │   └── scmks.py
    │
    └── services/ - задачи (скрипты)
        │
        ├── hello_world/
        │   ├── service.py
        │   ├── config.ini
        │   └── config.test.ini
        │
        ├── hello_land/
        │   ├── service.py
        │   ├── config.ini
        │   └── config.test.ini
        |
        ├── ...
        │
        ├── name_of_service_A/
        │   ├── service.py
        │   ├── config.ini
        │   └── config.test.ini
        │
        └── name_of_service_B/
            ├── service.py
            ├── config.ini
            └── config.test.ini

```

## Запуск задач

Запуск без параметров

```sh
$ python .\run_service.py
usage: run_service.py [-h] [-v] [-n] [-t] [Service]

Choose service to start

positional arguments:
  Service          choose service to start

options:
  -h, --help       show this help message and exit
  -v, --verbose    be verbose
  -j, --json       use json format for logging
  -n, --nologfile  do not create a logfile
  -t, --test       use testing config

available services:
  a_check_geois_health
  a_current_unauth_waste_sites
  b_check_covid_statistic_health
  b_covid_statistic
  hello_land
  hello_world
  template_service
```

Запуск скрипта, который корректно отрабатывает

```sh
$ python .\run_service.py hello_land
ts=2022-01-21T23:32:22 level=INFO msg="basedir: D:\dev\cit.sakhalin\osa\launch_with_params"
ts=2022-01-21T23:32:22 level=INFO msg="service services.hello_land.service logger.info testing: CONNECTOR TEST STRING"
```

Запуск скрипта, в котором возникла ошибка

```sh
$ python .\run_service.py hello_world
ts=2022-01-21T23:30:47 level=INFO msg="service services.hello_world.service logger.info testing: CONNECTOR TEST STRING"
ts=2022-01-21T23:30:47 level=ERROR msg="uncaught exception:\nTraceback (most recent call last):\n  File '/usr/src/app/run_service.py', line 81, in main\n    service_runner(args.service, args.testing or False)\n  File '/usr/src/app/run_service.py', line 27, in service_runner\n    module.main(config)\n  File '/usr/src/app/services/hello_world/service.py', line 18, in main\n    a = 10 / 0  # intentional error FOR TESTING purpose\nZeroDivisionError: division by zero\n"
```

## Требования

Для запуска необходим Python 3.9 и выше, чтобы обойти этот момент возможно запускать задачи через [Docker](##Docker)

## Docker

### Подготовка образа

Необходимо подготовить образ с зависимостями из requirements.txt

```sh
docker build --build-arg userid=$(id $USER -u) --build-arg groupid=$(id $USER -g) -t pythonimp .
```

### Запуск с помощью Docker

```sh
docker run --rm -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro -v "$PWD":/usr/src/app pythonimp python run_service.py hello_land
```

## Тестирование

Запуск тестов осуществляется по команде `python -m unittest`
