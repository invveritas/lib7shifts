"""
Utilities for handling dates from the 7Shifts API
"""
import datetime

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def to_datetime(date_string):
    """Given a date string in API format, return a :class:`datetime.datetime`
    object corresponding to the date and time"""
    return datetime.datetime.strptime(date_string, DEFAULT_DATETIME_FORMAT)

def from_datetime(dt_obj):
    """Converts the datetime object back into a text representation compatible
    with the 7shifts API"""
    return dt_obj.strftime(DEFAULT_DATETIME_FORMAT)

def to_y_m_d(dt_obj):
    """Converts a datetime object to text in YYYY-MM-DD format"""
    return dt_obj.strftime("%Y-%m-%d")

def to_h_m_s(dt_obj):
    """Outputs just the time-portion of a datetime object in HH:MM:SS form"""
    return dt_obj.strftime("%H:%M:%S")
