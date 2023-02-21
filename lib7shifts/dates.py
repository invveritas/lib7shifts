"""
Utilities for handling dates from the 7Shifts API
"""
import datetime

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'


class DateTime7Shifts(datetime.datetime):
    """Override representation of dates in datetime objects to match
    7shifts form. Vitually identical to datetime.datetime"""

    def __str__(self):
        return self.strftime(DEFAULT_DATETIME_FORMAT)


def today(tzinfo=None):
    """Returns a DateTime7Shifts object corresponding to today at 12:00 AM in
    the timezone specified by tzinfo. If no timezone is specified, uses the
    local timezone as determined by :func:`get_local_tz` below.
    """
    if not tzinfo:
        tzinfo = get_local_tz()
    date = datetime.date.today()
    dtobj = DateTime7Shifts(date.year, date.month, date.day)
    return dtobj.replace(tzinfo=tzinfo)


def tomorrow(tzinfo=None):
    """Returns a :class:`DateTime7Shifts` object corresponding to 12:00 AM
    tomorrow, defaulting to the current timezone (non-naiive)
    """
    return today(tzinfo=tzinfo) + datetime.timedelta(days=1)


def yesterday(tzinfo=None):
    """Returns a :class:`DateTime7Shifts` object corresponding to 12:00 AM
    yesterday in the local timezone (unless a different tzinfo is
    specified). Non-naiive."""
    return today(tzinfo=tzinfo) - datetime.timedelta(days=1)


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
    """Given a date string in YYYY-MM-DD format, return a
    :class:`datetime.datetime` object corresponding to the date at 12AM"""
    date = DateTime7Shifts.strptime(
        date_string, DEFAULT_DATE_FORMAT)
    return date.replace(tzinfo=tzinfo)


def to_local_date(date_string):
    """Returns a :class:`DateTime7Shifts` object for the specified date
    string (YYYY-MM-DD form), in the local timezone."""
    return to_date(date_string, tzinfo=get_local_tz())


def to_local_datetime(date_string):
    """Returns a :class:`DateTime7Shifts` object for the specified date
    and time string (YYYY-MM-DD HH:MM:SS form), in the local timezone."""
    return to_datetime(date_string, tzinfo=get_local_tz())


def _get_epoch_ts_for_date(date):
    "Given a local date of form YYYY-MM-DD, return a unix TS"
    return to_date(date, tzinfo=get_local_tz()).timestamp()


def days_ago(ndays=0, tzinfo=None):
    """Given a number of days ago, return a :class:`DateTime7Shifts` for the
    start of the day, that many days ago (date snapping). Defaults to the local
    timezone that the code runs in, but provide an alternate to tzinfo if need
    be. By default, returns an epoch timestamp for the start of today"""
    return today(tzinfo=tzinfo) - datetime.timedelta(days=ndays)


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


def datetime_to_human_date(dt_obj):
    return dt_obj.strftime('%Y-%m-%d')


def datetime_to_human_datetime(dt_obj):
    return dt_obj.strftime('%Y-%m-%d %H:%M:%S')
