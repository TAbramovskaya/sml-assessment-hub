import datetime as dt
from secret import client_settings
from fetcher import get_data
from db.admin import *
from db.migrate import apply_schema
from db.loader import insert_data
from reports.gsheets import upload_attempts_to_sheet, export_report
from logger import get_general_logger

log = get_general_logger(__name__)


def main():

    # The start date will be treated as a date in UTC+00:00.
    # No other behavior is implied.
    start_utc = dt.datetime.strptime(
        '2026-02-20 00:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc)
    duration = dt.timedelta(hours=24) - dt.timedelta(microseconds=1)
    end_utc = start_utc + duration

    log.info(f"Started preparing data")
    attempts = get_data(client_settings.API_URL, start_utc, end_utc)

    if len(attempts) == 0:
        log.info(f"The fetched data contains no items")
        return
    log.info("Finished preparing data")

    # Database preparation
    log.info("Started preparing database")
    db_create_if_not_exist()
    user_create_if_not_exist()
    schema_create_if_not_exists()
    apply_schema()
    log.info("Finished preparing database")

    log.info("Started inserting attempts into database")
    insert_data(attempts)
    log.info("Finished inserting attempts into database")


    log.info("Started generating report")
    upload_attempts_to_sheet(attempts)

    # Specify the title of the sheet for the report
    sheet_title = f"{client_settings.CLIENT} {start_utc.strftime('%Y-%m-%d %H:%M')}-{end_utc.strftime('%Y-%m-%d %H:%M')}"
    export_report(attempts, sheet_title)
    log.info("Finished generating report")

    # See today's log file to check the results of the workflow.

if __name__ == "__main__":
    main()
