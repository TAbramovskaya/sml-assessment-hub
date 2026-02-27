import datetime as dt
from secret import client_settings
from fetcher import get_data
from db.admin import *
from db.migrate import apply_schema
from db.loader import insert_data
from logger import get_general_logger


log = get_general_logger(__name__)


def main():
    start = dt.datetime.strptime('2026-02-25 06:00:00', '%Y-%m-%d %H:%M:%S')
    attempts = get_data(client_settings.API_URL, start)
    for attempt in attempts:
        print(attempt)

    db_create_if_not_exist()
    user_create_if_not_exist()
    schema_create_if_not_exists()
    apply_schema()
    insert_data(attempts)


if __name__ == "__main__":
    main()
