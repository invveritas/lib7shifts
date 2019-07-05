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

class DB(object):
    """Abstract class representing a database
    """

    @property
    def connection(self):
        """Returns an active, open database connection
        """
        raise NotImplementedError("connection is not implemented")

    @property
    def cursor(self):
        """Returns a cursor to execute queries against"""
        raise NotImplementedError("cursor is not implemented")

class SQLite3DB(DB):

    def __init__(self, filename):
        self._file = filename
        self._conn = None

    @property
    def connection(self):
        if not self._conn:
            import sqlite3
            self._conn = sqlite3.connect(self._file)
        return self._conn

    @property
    def cursor(self):
        return self.connection.cursor()
