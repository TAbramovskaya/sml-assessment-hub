import os
import random
import string
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from logger import get_general_logger
from secret.client_settings import EXPORT_SPREADSHEET_ID, REPORT_SPREADSHEET_ID
from attempts_metrics import *
from statistics import median, mean

log = get_general_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(CUR_DIR, "..", "secret", "service_account.json")


def upload_attempts_to_sheet(attempts):
    """
    Upload a batch of attempts to Google Sheets.
    A new sheet is created per fetch, named 'YYYY-MM-DD hh:mm fetch'.
    """
    if not attempts:
        return

    try:
        sheet_service = get_sheet_service()

        # Sheet name: YYYY-MM-DD hh:mm fetch
        sheet_name = datetime.now().strftime("%Y-%m-%d %H:%M fetch")

        # Create the sheet for the current report
        sheet_service.batchUpdate(
            spreadsheetId=EXPORT_SPREADSHEET_ID,
            body={
                "requests": [{
                    "addSheet": {
                        "properties": {"title": sheet_name, "index": 0}
                    }
                }]
            }
        ).execute()

        # Prepare data (header + rows)
        rows = [["created_at", "user_id", "course_name", "target_id",
                 "attempt_type", "is_correct", "raw_oauth_consumer_key",
                 "raw_lis_result_sourcedid", "raw_lis_outcome_service_url"]]
        for att in attempts:
            rows.append([
                att.created_at.isoformat() if hasattr(att.created_at, "isoformat") else str(att.created_at),
                att.user_id,
                att.course_name,
                att.target_id,
                att.attempt_type,
                att.is_correct,
                att.raw_oauth_consumer_key,
                att.raw_lis_result_sourcedid,
                att.raw_lis_outcome_service_url,
            ])

        # Write data in one batch
        sheet_service.values().update(
            spreadsheetId=EXPORT_SPREADSHEET_ID,
            range=f"{sheet_name}!A1",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()
        log.info(f"Working spreadsheetId '{EXPORT_SPREADSHEET_ID}'")
        log.info(f"Attempts uploaded to sheet '{sheet_name}'")

    except HttpError as e:
        log.error(f"Google Sheets API error: {e}")


def export_report(attempts, sheet_title):
    """
    Export aggregated attempt statistics to a Google Sheets report.
    """
    if not attempts:
        return

    try:
        sheet_service = get_sheet_service()

        # Create the sheet for the current report
        response = sheet_service.batchUpdate(
            spreadsheetId=REPORT_SPREADSHEET_ID,
            body={
                "requests": [{
                    "addSheet": {
                        "properties": {"title": sheet_title, "index": 0}
                    }
                }]
            }
        ).execute()
        sheet_id = response["replies"][0]["addSheet"]["properties"]["sheetId"]

        # Header
        rows = [["course name", "total attempts count", "unique users", "avg attempts per user",
                 "median attempts per user", "total runs", "total submits", "successful submits"]]
        attempts_per_course = get_attempts_per_course(attempts)

        # Prepare metrics for each course
        for course in attempts_per_course:
            course_attempts = attempts_per_course[course]
            attempts_per_user = count_attempts_per_user(course_attempts)
            attempt_types = count_attempt_types(course_attempts)
            correctness = count_correctness(course_attempts)

            rows.append([
                course,                                     # course name
                len(course_attempts),                       # total attempts count
                len(attempts_per_user),                     # unique users
                round(mean(attempts_per_user.values()), 2), # avg attempts per user
                median(attempts_per_user.values()),         # median attempts per user
                attempt_types.get("run", 0),                # total runs
                attempt_types.get("submit", 0),             # total submits
                correctness.get(1, 0)                       # proportion of successful submits
            ])

        # Add totals
        total_attempts_per_user = count_attempts_per_user(attempts)
        total_attempt_types = count_attempt_types(attempts)
        correctness = count_correctness(attempts)

        rows.append([
            "total",
            len(attempts),
            len(total_attempts_per_user),
            round(mean(total_attempts_per_user.values()), 2),
            median(total_attempts_per_user.values()),
            total_attempt_types.get("run", 0),
            total_attempt_types.get("submit", 0),
            correctness.get(1, 0)
        ])

        # Write data in one batch
        sheet_service.values().update(
            spreadsheetId=REPORT_SPREADSHEET_ID,
            range=f"{sheet_title}!A1",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()

        # Make header and totals bold
        row_count = len(attempts_per_course) + 2    # total number of rows with header and totals
        requests = [
            # Bold header
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True}
                        }
                    },
                    "fields": "userEnteredFormat.textFormat.bold"
                }
            },

            # Bold totals
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row_count - 1,
                        "endRowIndex": row_count
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True}
                        }
                    },
                    "fields": "userEnteredFormat.textFormat.bold"
                }
            }
        ]

        sheet_service.batchUpdate(
            spreadsheetId=REPORT_SPREADSHEET_ID,
            body={"requests": requests}
        ).execute()

        log.info(f"Working spreadsheetId '{REPORT_SPREADSHEET_ID}'")
        log.info(f"Report uploaded to sheet '{sheet_title}'")

    except HttpError as e:
        log.error(f"Google Sheets API error: {e}")


def get_sheet_service():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()