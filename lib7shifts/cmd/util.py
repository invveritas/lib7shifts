"""
Utility functions and objects used by the other command-related modules.
"""
import sys
import datetime

def filter_fields(items, output_fields, print_rows=False):
    """Given a list of item dicts from 7shifts, yield a tuple per item with data
    for insertion into a database or output as CSV"""
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
        print_rows and print(row, file=sys.stdout)
        yield row
