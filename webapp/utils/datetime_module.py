from zoneinfo import ZoneInfo
from datetime import datetime

timezone = ZoneInfo(key='Asia/Kolkata')


def get_current_time_tz(timezone='Asia/Kolkata'):
    timezone = ZoneInfo(key=timezone)
    return datetime.now(tz=timezone)
