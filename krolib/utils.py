import datetime
import typing as t

import pytz

from dateutil.parser import parse as date_parse
from tzlocal import get_localzone


epoch = datetime.datetime.utcfromtimestamp(0)


def is_weekday(dt: datetime.datetime):
    return dt.weekday() < 5


def is_weekend(dt: datetime.datetime):
    return dt.weekday() >= 5


def just_now(tz: str = 'UTC'):
    if not tz:
        now = datetime.datetime.utcnow()
    else:
        now = datetime.datetime.now(tz=pytz.timezone(tz))

    return now.replace(microsecond=0)


def normalize_datetime(dt: datetime.datetime, tz: str = 'UTC'):
    local_tz = pytz.timezone(tz)
    if not dt.tzinfo:
        dt = local_tz.localize(dt)
    else:
        dt = dt.astimezone(local_tz)

    return dt.replace(microsecond=0)


def normalize_isoformat(dt: str, tz: str = 'UTC'):
    dt = date_parse(dt)
    return normalize_datetime(dt, tz)


def unix_time_millis(dt: datetime.datetime = None):
    dt = dt or datetime.datetime.utcnow()
    return int((dt - epoch).total_seconds() * 1000.0)


def unix_time_to_human(uxtime: int):
    return datetime.datetime.fromtimestamp(uxtime / 1000).strftime('%Y-%m-%d %H:%M:%S')
