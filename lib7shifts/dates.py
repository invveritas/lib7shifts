"""
Utilities for handling dates from the 7Shifts API
"""
import datetime

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'


class DateTime7Shifts(datetime.datetime):
    """Override representation of dates in datetime objects to match
    7shifts form"""

    def __str__(self):
        return self.strftime(DEFAULT_DATETIME_FORMAT)


def get_local_tz():
    "Return the current local timezone"
    return datetime.datetime.utcnow().astimezone().tzinfo


def to_datetime(date_string, tzinfo=datetime.timezone.utc):
    """Given a datetime string in API format, return a
    :class:`datetime.datetime` object corresponding to the date and time"""
    date = DateTime7Shifts.strptime(
        date_string, DEFAULT_DATETIME_FORMAT)
    return date.replace(tzinfo=tzinfo)


def to_date(date_string, tzinfo=datetime.timezone.utc):
    """Given a date string in API format, return a :class:`datetime.datetime`
    object corresponding to the date and time"""
    date = DateTime7Shifts.strptime(
        date_string, DEFAULT_DATE_FORMAT)
    return date.replace(tzinfo=tzinfo)


def get_epoch_ts_for_date(date):
    "Given a local date of form YYYY-MM-DD, return a unix TS"
    return to_date(date, tzinfo=get_local_tz()).timestamp()


def from_datetime(dt_obj):
    """Converts the datetime object back into a text representation compatible
    with the 7shifts API"""
    return dt_obj.__str__()


def to_y_m_d(dt_obj):
    """Converts a datetime object to text in YYYY-MM-DD format"""
    return dt_obj.strftime("%Y-%m-%d")


def to_h_m_s(dt_obj):
    """Outputs just the time-portion of a datetime object in HH:MM:SS form"""
    return dt_obj.strftime("%H:%M:%S")
