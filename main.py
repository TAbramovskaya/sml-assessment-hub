import datetime as dt
import settings
from fetcher import get_data
from logger import get_general_logger

log = get_general_logger(__name__)


def main():
    start = dt.datetime.strptime('2026-02-20 09:00:00', '%Y-%m-%d %H:%M:%S')

    attempts = get_data(settings.API_URL, start)

    for attempt in attempts:
        print(attempt)


if __name__ == "__main__":
    main()
