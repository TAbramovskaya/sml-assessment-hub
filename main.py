import datetime as dt
from zoneinfo import ZoneInfo
import settings
from fetcher import get_data


start = dt.datetime.strptime('2026-02-20 09:00:00', '%Y-%m-%d %H:%M:%S')

attempts = get_data(settings.API_URL, start)
print(attempts)