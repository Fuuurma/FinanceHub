from datetime import datetime, time, timedelta, timezone
from typing import Optional, List, Dict, Any

import pytz
from dateutil import tz

from utils.constants.default import DEFAULT_TIMEZONE

MARKET_TIMEZONES = {
    "NYSE": "America/New_York",
    "NASDAQ": "America/New_York",
    "AMEX": "America/New_York",
    "LSE": "Europe/London",
    "Euronext": "Europe/Paris",
    "TMX": "America/Toronto",
    "TSE": "Asia/Tokyo",
    "HKEX": "Asia/Hong_Kong",
    "SSE": "Asia/Shanghai",
    "ASX": "Australia/Sydney",
    "KOSPI": "Asia/Seoul",
    "BSE": "Asia/Kolkata",
    "NSE": "Asia/Kolkata",
    "FWB": "Europe/Berlin",
    "SIX": "Europe/Zurich",
}

MARKET_OPEN_TIME = time(9, 30, 0)
MARKET_CLOSE_TIME = time(16, 0, 0)
PRE_MARKET_OPEN = time(4, 0, 0)
AFTER_HOURS_CLOSE = time(20, 0, 0)

US_HOLIDAYS = [
    "2024-01-01",
    "2024-01-15",
    "2024-02-19",
    "2024-03-29",
    "2024-05-27",
    "2024-06-19",
    "2024-07-04",
    "2024-09-02",
    "2024-11-28",
    "2024-12-25",
    "2025-01-01",
    "2025-01-20",
    "2025-02-17",
    "2025-04-18",
    "2025-05-26",
    "2025-06-19",
    "2025-07-04",
    "2025-09-01",
    "2025-11-27",
    "2025-12-25",
]


def get_timezone(tz_name: str = DEFAULT_TIMEZONE) -> pytz.timezone:
    try:
        return pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return pytz.UTC


def convert_to_timezone(
    dt: datetime,
    target_tz: str,
    source_tz: Optional[str] = None,
) -> datetime:
    source_timezone = get_timezone(source_tz) if source_tz else dt.tzinfo
    if dt.tzinfo is None:
        dt = source_timezone.localize(dt)
    else:
        dt = dt.astimezone(source_timezone)
    target_timezone = get_timezone(target_tz)
    return dt.astimezone(target_timezone)


def convert_to_utc(dt: datetime, source_tz: Optional[str] = None) -> datetime:
    if source_tz:
        source_timezone = get_timezone(source_tz)
        if dt.tzinfo is None:
            dt = source_timezone.localize(dt)
    return dt.astimezone(pytz.UTC)


def get_current_time_in_timezone(tz_name: str = DEFAULT_TIMEZONE) -> datetime:
    timezone_obj = get_timezone(tz_name)
    return datetime.now(timezone_obj)


def is_market_open(
    dt: Optional[datetime] = None,
    timezone_str: str = "America/New_York",
) -> bool:
    if dt is None:
        dt = get_current_time_in_timezone(timezone_str)
    tz = get_timezone(timezone_str)
    local_dt = dt.astimezone(tz)
    current_time = local_dt.time()
    return MARKET_OPEN_TIME <= current_time <= MARKET_CLOSE_TIME


def is_pre_market(
    dt: Optional[datetime] = None,
    timezone_str: str = "America/New_York",
) -> bool:
    if dt is None:
        dt = get_current_time_in_timezone(timezone_str)
    tz = get_timezone(timezone_str)
    local_dt = dt.astimezone(tz)
    current_time = local_dt.time()
    return PRE_MARKET_OPEN <= current_time < MARKET_OPEN_TIME


def is_after_hours(
    dt: Optional[datetime] = None,
    timezone_str: str = "America/New_York",
) -> bool:
    if dt is None:
        dt = get_current_time_in_timezone(timezone_str)
    tz = get_timezone(timezone_str)
    local_dt = dt.astimezone(tz)
    current_time = local_dt.time()
    return MARKET_CLOSE_TIME < current_time <= AFTER_HOURS_CLOSE


def get_market_session_status(
    dt: Optional[datetime] = None,
    timezone_str: str = "America/New_York",
) -> str:
    if is_pre_market(dt, timezone_str):
        return "pre_market"
    elif is_market_open(dt, timezone_str):
        return "regular"
    elif is_after_hours(dt, timezone_str):
        return "after_hours"
    else:
        return "closed"


def is_trading_day(
    dt: datetime,
    timezone_str: str = "America/New_York",
    holidays: Optional[List[str]] = None,
) -> bool:
    tz = get_timezone(timezone_str)
    local_dt = dt.astimezone(tz)
    if local_dt.weekday() >= 5:
        return False
    date_str = local_dt.strftime("%Y-%m-%d")
    holiday_list = holidays or US_HOLIDAYS
    return date_str not in holiday_list


def get_next_trading_day(
    dt: datetime,
    timezone_str: str = "America/New_York",
    holidays: Optional[List[str]] = None,
) -> datetime:
    current_date = dt.date()
    next_date = current_date + timedelta(days=1)
    tz = get_timezone(timezone_str)
    while True:
        check_dt = datetime.combine(next_date, time(9, 30, 0), tz)
        if is_trading_day(check_dt, timezone_str, holidays):
            return check_dt
        next_date += timedelta(days=1)


def get_previous_trading_day(
    dt: datetime,
    timezone_str: str = "America/New_York",
    holidays: Optional[List[str]] = None,
) -> datetime:
    current_date = dt.date()
    prev_date = current_date - timedelta(days=1)
    tz = get_timezone(timezone_str)
    while True:
        check_dt = datetime.combine(prev_date, time(9, 30, 0), tz)
        if is_trading_day(check_dt, timezone_str, holidays):
            return check_dt
        prev_date -= timedelta(days=1)


def get_market_open_time(
    dt: Optional[datetime] = None,
    timezone_str: str = "America/New_York",
) -> datetime:
    if dt is None:
        dt = get_current_time_in_timezone(timezone_str)
    tz = get_timezone(timezone_str)
    local_date = dt.astimezone(tz).date()
    return datetime.combine(local_date, MARKET_OPEN_TIME, tz)


def get_market_close_time(
    dt: Optional[datetime] = None,
    timezone_str: str = "America/New_York",
) -> datetime:
    if dt is None:
        dt = get_current_time_in_timezone(timezone_str)
    tz = get_timezone(timezone_str)
    local_date = dt.astimezone(tz).date()
    return datetime.combine(local_date, MARKET_CLOSE_TIME, tz)


def get_time_until_market_open(
    dt: Optional[datetime] = None,
    timezone_str: str = "America/New_York",
) -> Optional[timedelta]:
    tz = get_timezone(timezone_str)
    now = dt.astimezone(tz) if dt else get_current_time_in_timezone(timezone_str)
    today_open = datetime.combine(now.date(), MARKET_OPEN_TIME, tz)
    if now < today_open:
        return today_open - now
    tomorrow_open = datetime.combine(
        now.date() + timedelta(days=1), MARKET_OPEN_TIME, tz
    )
    while not is_trading_day(tomorrow_open, timezone_str):
        tomorrow_open += timedelta(days=1)
    return tomorrow_open - now


def get_time_until_market_close(
    dt: Optional[datetime] = None,
    timezone_str: str = "America/New_York",
) -> Optional[timedelta]:
    tz = get_timezone(timezone_str)
    now = dt.astimezone(tz) if dt else get_current_time_in_timezone(timezone_str)
    today_close = datetime.combine(now.date(), MARKET_CLOSE_TIME, tz)
    if now < today_close and is_trading_day(now, timezone_str):
        return today_close - now
    return None


def format_datetime_for_display(
    dt: datetime,
    timezone_str: str = DEFAULT_TIMEZONE,
    format_str: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    try:
        local_dt = convert_to_timezone(dt, timezone_str)
        return local_dt.strftime(format_str)
    except (ValueError, AttributeError):
        return dt.strftime(format_str)


def format_date_for_display(
    dt: datetime,
    timezone_str: str = DEFAULT_TIMEZONE,
    format_str: str = "%Y-%m-%d",
) -> str:
    try:
        local_dt = convert_to_timezone(dt, timezone_str)
        return local_dt.strftime(format_str)
    except (ValueError, AttributeError):
        return dt.strftime(format_str)


def format_time_for_display(
    dt: datetime,
    timezone_str: str = DEFAULT_TIMEZONE,
    format_str: str = "%H:%M:%S",
) -> str:
    try:
        local_dt = convert_to_timezone(dt, timezone_str)
        return local_dt.strftime(format_str)
    except (ValueError, AttributeError):
        return dt.strftime(format_str)


def get_market_hours(
    timezone_str: str = "America/New_York",
) -> Dict[str, Any]:
    tz = get_timezone(timezone_str)
    now = get_current_time_in_timezone(timezone_str)
    return {
        "timezone": timezone_str,
        "market_open": datetime.combine(now.date(), MARKET_OPEN_TIME, tz).isoformat(),
        "market_close": datetime.combine(now.date(), MARKET_CLOSE_TIME, tz).isoformat(),
        "pre_market_open": datetime.combine(
            now.date(), PRE_MARKET_OPEN, tz
        ).isoformat(),
        "after_hours_close": datetime.combine(
            now.date(), AFTER_HOURS_CLOSE, tz
        ).isoformat(),
        "is_open": is_market_open(now, timezone_str),
        "is_pre_market": is_pre_market(now, timezone_str),
        "is_after_hours": is_after_hours(now, timezone_str),
        "session": get_market_session_status(now, timezone_str),
    }


def get_exchange_timezone(exchange_code: str) -> str:
    return MARKET_TIMEZONES.get(exchange_code.upper(), DEFAULT_TIMEZONE)


def is_exchange_open(
    exchange_code: str,
    dt: Optional[datetime] = None,
) -> bool:
    tz_name = get_exchange_timezone(exchange_code)
    return is_market_open(dt, tz_name)


def get_trading_session(
    dt: datetime,
    timezone_str: str = "America/New_York",
) -> Dict[str, Any]:
    tz = get_timezone(timezone_str)
    local_dt = dt.astimezone(tz)
    return {
        "datetime": local_dt.isoformat(),
        "timezone": timezone_str,
        "session": get_market_session_status(local_dt, timezone_str),
        "is_trading_day": is_trading_day(local_dt, timezone_str),
        "market_open": get_market_open_time(local_dt, timezone_str).isoformat(),
        "market_close": get_market_close_time(local_dt, timezone_str).isoformat(),
    }


def parse_date_string(
    date_str: str,
    format_str: str = "%Y-%m-%d",
    timezone_str: str = DEFAULT_TIMEZONE,
) -> Optional[datetime]:
    try:
        dt = datetime.strptime(date_str, format_str)
        tz = get_timezone(timezone_str)
        return tz.localize(dt)
    except (ValueError, AttributeError):
        return None


def parse_datetime_string(
    datetime_str: str,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    timezone_str: str = DEFAULT_TIMEZONE,
) -> Optional[datetime]:
    try:
        dt = datetime.strptime(datetime_str, format_str)
        tz = get_timezone(timezone_str)
        return tz.localize(dt)
    except (ValueError, AttributeError):
        return None


def get_utc_offset(timezone_str: str) -> int:
    tz = get_timezone(timezone_str)
    now = datetime.now(tz)
    offset = now.utcoffset()
    if offset:
        return int(offset.total_seconds() / 3600)
    return 0


def get_timezone_info(timezone_str: str) -> Dict[str, Any]:
    tz = get_timezone(timezone_str)
    now = datetime.now(tz)
    offset = now.utcoffset()
    offset_hours = 0
    if offset:
        offset_hours = offset.total_seconds() / 3600
    return {
        "name": timezone_str,
        "utc_offset": offset_hours,
        "utc_offset_str": f"UTC{offset_hours:+.0f}",
        "current_time": now.isoformat(),
        "abbreviation": now.strftime("%Z"),
    }


def get_trading_days_in_range(
    start_dt: datetime,
    end_dt: datetime,
    timezone_str: str = "America/New_York",
    holidays: Optional[List[str]] = None,
) -> List[datetime]:
    trading_days = []
    current = start_dt
    tz = get_timezone(timezone_str)
    while current <= end_dt:
        check_dt = datetime.combine(current.date(), time(9, 30, 0), tz)
        if is_trading_day(check_dt, timezone_str, holidays):
            trading_days.append(check_dt)
        current += timedelta(days=1)
    return trading_days


def get_calendar_days_in_range(
    start_dt: datetime,
    end_dt: datetime,
    timezone_str: str = DEFAULT_TIMEZONE,
) -> List[datetime]:
    calendar_days = []
    current = start_dt.date()
    end = end_dt.date()
    tz = get_timezone(timezone_str)
    while current <= end:
        calendar_days.append(datetime.combine(current, time(0, 0, 0), tz))
        current += timedelta(days=1)
    return calendar_days


def get_business_days_in_range(
    start_dt: datetime,
    end_dt: datetime,
    exclude_holidays: bool = True,
    holidays: Optional[List[str]] = None,
) -> int:
    tz = get_timezone(DEFAULT_TIMEZONE)
    start_local = start_dt.astimezone(tz)
    end_local = end_dt.astimezone(tz)
    trading_days = get_trading_days_in_range(
        start_local, end_local, DEFAULT_TIMEZONE, holidays
    )
    return len(trading_days)
