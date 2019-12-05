"""usage:
  7shifts location list [options]
  7shifts location db sync [options] [--] <sqlite_db>
  7shifts location db init [options] [--] <sqlite_db>

  -h --help         show this screen
  -v --version      show version information
  --dry-run         does not commit data to database, but goes through inserts
  -d --debug        enable debug logging (low-level)

You must provide the 7shifts API key with an environment variable called
API_KEY_7SHIFTS.

"""
import lib7shifts
from .common import get_7shifts_client, print_api_data, Sync7Shifts2Sqlite


class SyncLocations2Sqlite(Sync7Shifts2Sqlite):
    """Extend :class:`Sync7Shifts2Sqlite` to work for 7shifts locations."""

    table_name = 'locations'
    table_schema = """CREATE TABLE IF NOT EXISTS {table_name} (
            id PRIMARY KEY UNIQUE,
            address NOT NULL,
            timezone,
            hash UNIQUE
        ) WITHOUT ROWID
        """
    insert_query = """INSERT OR REPLACE INTO {table_name}
        VALUES(?, ?, ?, ?)"""
    insert_fields = (
        'id', 'address', 'timezone', 'hash')


def get_locations():
    """Return a list of :class:`lib7shifts.location.Location` objects from
    the API"""
    client = get_7shifts_client()
    return lib7shifts.list_locations(client)


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        print_api_data(get_locations())
    elif args.get('db', False):
        sync_db = SyncLocations2Sqlite(
            args.get('<sqlite_db>'),
            dry_run=args.get('--dry-run'))
        if args.get('sync', False):
            sync_db.sync_to_database(get_locations())
        elif args.get('init', False):
            sync_db.init_db_schema()
        else:
            raise RuntimeError("no valid db action specified")
    else:
        raise RuntimeError("no valid action in args")
    return 0
