import requests
import datetime as dt
from zoneinfo import ZoneInfo
import matching_model
from secret.settings import *
from logger import get_general_logger

log = get_general_logger(__name__)

working_td = dt.timedelta(hours=3) - dt.timedelta(microseconds=1)


def start_as_utc(start):
    start_client = start.replace(tzinfo=CLIENT_TIMEZONE)
    return start_client.astimezone(ZoneInfo('UTC'))


def get_data(api_url, start, duration=working_td):
    start_utc = start_as_utc(start)
    end_utc = start_utc + duration

    params = {'client': CLIENT,
              'client_key': CLIENT_KEY,
              'start': start_utc.strftime('%Y-%m-%d %H:%M:%S.%f'),
              'end': end_utc.strftime('%Y-%m-%d %H:%M:%S.%f')}

    data = _fetch_api(api_url, params)
    if not data:
        log.warning("No data were fetched")
        return None

    log.info(f'Fetched period is {start_utc} - {end_utc}, got {len(data)} items in response')

    attempts = []
    failed_attempts = []
    log.info(f"Parsing data items...")
    for item in data:
        attempt = matching_model.get_attempt(item)
        if not attempt:
            failed_attempts.append(item)
            print("Attempt not found or doesn't match: ", item)
            continue
        attempts.append(attempt)
    log.info(f" {len(failed_attempts)} items failed validation")
    log.info(f" {len(attempts)} attempts successfully added")

    return attempts


def _fetch_api(api_url, params):
    log.info(f"Getting data from {api_url}...")

    data = None
    try:
        response = requests.get(api_url, params=params)
        log.info(f"Status code: {response.status_code}, elapsed: {response.elapsed}")
        data = response.json()
    except requests.exceptions.RequestException as e:
        log.warning("Request failed:", e)
    except requests.JSONDecodeError as e:
        log.warning("Failed to parse JSON:", e)
    except Exception as e:
        log.warning("Unexpected error:", e)

    return data