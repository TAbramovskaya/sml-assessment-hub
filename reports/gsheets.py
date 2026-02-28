import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from logger import get_general_logger
from secret.client_settings import EXPORT_SPREADSHEET_ID, REPORT_SPREADSHEET_ID

log = get_general_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(CUR_DIR, "..", "secret", "service_account.json")


def upload_attempts_to_sheet(attempts):
    """
    Upload a batch of attempts to Google Sheets using a service account.
    A new sheet is created per fetch, named 'YYYY-MM-DD hh:mm fetch'.
    """
    if not attempts:
        return

    try:
        sheet_service = get_sheet_service()

        # Sheet name: YYYY-MM-DD fetch
        sheet_name = datetime.now().strftime("%Y-%m-%d %H:%M fetch")

        # Create the sheet for the current report
        sheet_service.batchUpdate(
            spreadsheetId=EXPORT_SPREADSHEET_ID,
            body={
                "requests": [
                    {"addSheet": {"properties": {"title": sheet_name}}}
                ]
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

        log.info(f"{len(attempts)} attempts uploaded to sheet '{sheet_name}'")

    except HttpError as e:
        log.error(f"Google Sheets API error: {e}")


def export_report(attempts):
    unique_users = {att.user_id for att in attempts}
    unique_targets = {att.target_id for att in attempts}
    

def get_sheet_service():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()