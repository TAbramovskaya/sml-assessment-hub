import datetime as dt
from secret import settings
from fetcher import get_data
from db.admin import *
from db.migrate import *
from logger import get_general_logger


log = get_general_logger(__name__)


def main():
    start = dt.datetime.strptime('2026-02-20 09:00:00', '%Y-%m-%d %H:%M:%S')
    attempts = get_data(settings.API_URL, start)
    for attempt in attempts:
        print(attempt)

    db_create_if_not_exist()
    user_create_if_not_exist()
    schema_create_if_not_exists()
    apply_schema()


if __name__ == "__main__":
    main()
