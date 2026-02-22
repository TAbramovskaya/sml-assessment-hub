import requests
import datetime as dt
from zoneinfo import ZoneInfo
import settings
import matching_model


working_td = dt.timedelta(hours=1) - dt.timedelta(microseconds=1)


def start_as_utc(start):
    start_client = start.replace(tzinfo=settings.CLIENT_TIMEZONE)
    return start_client.astimezone(ZoneInfo('UTC'))


def get_data(api_url, start):
    start_utc = start_as_utc(start)
    end_utc = start_utc + working_td

    params = {'client': settings.CLIENT,
              'client_key': settings.CLIENT_KEY,
              'start': start_utc.strftime('%Y-%m-%d %H:%M:%S.%f'),
              'end': end_utc.strftime('%Y-%m-%d %H:%M:%S.%f')}

    response = requests.get(api_url, params=params)

    print("Status:", response.status_code, response.reason)
    print("Elapsed:", response.elapsed)

    print("\nBody:")
    print(response.text)

    try:
        data = response.json()
    except requests.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        data = None
    except Exception as e:
        print("Unexpected error:", e)
        data = None

    attempts = []
    for item in data:
        attempt = matching_model.get_attempt(item)
        if not attempt:
            print("Attempt not found or doesn't match: ", item)
            continue
        attempts.append(attempt)

    return attempts
