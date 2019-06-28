"""
Utilities for handling dates from the 7Shifts API
"""
import datetime

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class DateTime7Shifts(datetime.datetime):
    """Override representation of dates in datetime objects to match 7shifts form"""
    def __str__(self):
        return self.strftime(DEFAULT_DATETIME_FORMAT)

def to_datetime(date_string):
    """Given a date string in API format, return a :class:`datetime.datetime`
    object corresponding to the date and time"""
    date = DateTime7Shifts.strptime(
        date_string, DEFAULT_DATETIME_FORMAT)
    return date.replace(tzinfo=datetime.timezone.utc)

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
