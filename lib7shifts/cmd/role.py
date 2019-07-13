#!/usr/bin/env python3
"""usage:
  7shifts role list [options]
  7shifts role db sync [options] [--] <sqlite_db>
  7shifts role db init [options] [--] <sqlite_db>

  -h --help         show this screen
  -v --version      show version information
  --dry-run         does not commit data to database, but goes through inserts
  -d --debug        enable debug logging (low-level)

You must provide the 7shifts API key with an environment variable called
API_KEY_7SHIFTS.

"""
import lib7shifts
from .common import get_7shifts_client, print_api_data, Sync7Shifts2Sqlite


class SyncRoles2Sqlite(Sync7Shifts2Sqlite):
    """Extend :class:`Sync7Shifts2Sqlite` to work for 7shifts roles."""

    table_name = 'roles'
    table_schema = """CREATE TABLE IF NOT EXISTS {table_name} (
            id PRIMARY KEY UNIQUE,
            name NOT NULL,
            department_id NOT NULL,
            location_id NOT NULL,
            created,
            modified
        ) WITHOUT ROWID"""
    insert_query = """INSERT OR REPLACE INTO {table_name}
        VALUES(?, ?, ?, ?, ?, ?)"""
    insert_fields = (
        'id', 'name', 'department_id', 'location_id',
        'created', 'modified')


def get_roles():
    """Return a list of :class:`lib7shifts.role.Role` objects from
    the API"""
    client = get_7shifts_client()
    return lib7shifts.list_roles(client)


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        print_api_data(get_roles())
    elif args.get('db', False):
        sync_db = SyncRoles2Sqlite(
            args.get('<sqlite_db>'),
            dry_run=args.get('--dry-run'))
        if args.get('sync', False):
            sync_db.sync_to_database(get_roles())
        elif args.get('init', False):
            sync_db.init_db_schema()
        else:
            raise RuntimeError("no valid db action specified")
    else:
        raise RuntimeError("no valid action in args")
    return 0
