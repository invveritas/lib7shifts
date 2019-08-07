"""
Common methods and attributes for the various 7shifts commands
"""
import logging
import sqlite3
import datetime
import json
from lib7shifts import get_client as get_7shifts_client


def print_api_item(item):
    """Pretty-print a dictionary from the API"""
    print(json.dumps(item, indent=2))


def print_api_object(item):
    """Pretty-print an object from the API client library"""
    print(json.dumps(json.loads(item.__str__()), indent=2))


def print_api_data(data):
    """Given a list of objects from the 7shifts API, dump them in an
    easy-to-read format (indented JSON)"""
    try:
        for row in data:
            print(json.dumps(json.loads(row.__str__()), indent=2))
    except TypeError:
        print_api_item(data)


class Sync7Shifts2Sqlite(object):
    """
    This class wraps synchronizing 7shifts data into SQLite3.

    The version here is abstract, modules specific to each 7shifts
    object type should subclass and define the core attributes,
    and perform any method overrides required for specific objects.

    When creating an instance of this class, pass in a path where you
    want your SQLite database to be found (it will be created if not
    already present), as the first argument.

    Pass kwarg `dry_run` to make DB insert operations roll-back (testing)
    """

    #: The name of the table to be created/inserted into
    table_name = None
    #: The query used to create the table. Recommend using 'IF NOT EXISTS'
    #: syntax. Table name should use placeholder, "{table_name}"
    table_schema = None
    #: The query used to insert data into the table.
    #: Table name should use placeholder, "{table_name}"
    insert_query = None
    #: The list of fields to be inserted (should match the names in 7shits API)
    insert_fields = ()

    def __init__(self, db_location, **kwargs):
        self.log = logging.getLogger(self.__class__.__module__)
        self.dry_run = kwargs.get('dry_run', False)
        self._db_location = db_location
        self.kwargs = kwargs
        self.__db_handle = None
        self.__cursor = None

    @property
    def db_handle(self):
        "Returns an sqlite3 database handle"
        if self.__db_handle is None:
            self.log.debug('getting an sqlite3 database handle')
            self.__db_handle = sqlite3.connect(self._db_location)
            self.__db_handle.row_factory = sqlite3.Row
        return self.__db_handle

    def get_table_schema_query(self):
        """Returns the query used to create the database schema, performing
        any required substitutions, such as table_name"""
        return self.table_schema.format(table_name=self.table_name)

    def get_insert_query(self):
        """Returns the query used to insert object rows into the database,
        performing any substituations along the way, such as table_name"""
        return self.insert_query.format(table_name=self.table_name)

    def init_db_schema(self):
        "Run the table_schema query"
        self.log.info("inititalizing database schema")
        schema = self.get_table_schema_query()
        self.log.debug(schema)
        return self.db_handle.cursor().execute(schema)

    def sync_to_database(self, rows):
        """Given a list of dictionary rows, sync them to the database"
        """
        self.log.info("starting database record sync operation")
        cursor = self.db_handle.cursor()
        cursor.executemany(
            self.get_insert_query(), self.filter_fields(rows))
        self.log.info("Inserted/updated %d records", cursor.rowcount)
        if self.dry_run:
            self.db_handle.rollback()
        else:
            self.db_handle.commit()

    def filter_fields(self, items):
        """Given a list of item dicts from 7shifts, yield a tuple per item
        with data for insertion into a database or output as CSV"""
        rownum = 0
        for item in items:
            rownum += 1
            row = list()
            for field in self.insert_fields:
                try:
                    val = getattr(item, field)
                except AttributeError:
                    # passed a dict, not an API object
                    val = item[field]
                if isinstance(val, datetime.datetime):
                    val = val.timestamp()
                row.append(val)
            self.log.debug("row %d: %s", rownum, row)
            yield row
