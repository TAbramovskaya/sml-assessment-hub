import datetime as dt
from secret import client_settings
from fetcher import get_data
from db.admin import *
from db.migrate import apply_schema
from db.loader import insert_data
from logger import get_general_logger

log = get_general_logger(__name__)


def main():
    # Fetch data for the specified period and load to the database.

    # The start date will be treated as a date in UTC+00:00.
    # No other behavior is implied.
    start = dt.datetime.strptime('2026-02-24 02:00:00', '%Y-%m-%d %H:%M:%S')

    # By default, data is requested for 24 hours starting from the start.
    # For a different period, specify the optional duration parameter.
    attempts = get_data(client_settings.API_URL, start)

    if len(attempts) == 0:
        log.info(f"The fetched data contains no items.")
        return

    # DB routine
    db_create_if_not_exist()
    user_create_if_not_exist()
    schema_create_if_not_exists()
    apply_schema()

    insert_data(attempts)

    # See today's log file to check the results of the workflow.

if __name__ == "__main__":
    main()
