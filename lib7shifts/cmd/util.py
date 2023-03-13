"""
Utility functions and objects used by the other command-related modules.
"""
import sys
import datetime
from lib7shifts.dates import get_local_tz, DateTime7Shifts


def filter_fields(items, output_fields, print_rows=False):
    """Given a list of item dicts from 7shifts, yield a tuple per item with
    data for insertion into a database or output as CSV"""
    for item in items:
        row = list()
        for field in output_fields:
            try:
                val = getattr(item, field)
            except AttributeError:
                # passed a dict, not an API object
                val = item[field]
            if isinstance(val, datetime.datetime):
                val = val.timestamp()
            row.append(val)
        if print_rows:
            print(row, file=sys.stdout)
        yield row


def parse_last_modified(valuestring):
    """Given a last modified date/datetime string from CLI input, parse into
    an appropriate datetime object."""
    try:
        date = DateTime7Shifts.fromisoformat(valuestring)
    except ValueError:
        raise RuntimeError(
            "--modified-since doesn't appear to be an ISO datetime")
    if date.tzinfo is None:
        # attach local zone
        date = date.replace(tzinfo=get_local_tz())
    return date
