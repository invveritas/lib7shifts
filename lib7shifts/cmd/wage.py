#!/usr/bin/env python3
"""usage:
  7shifts wage list [options]
  7shifts wage db sync [options] [--] <sqlite_db>
  7shifts wage db init [options] [--] <sqlite_db>

  -h --help         show this screen
  -v --version      show version information
  --dry-run         does not commit data to database, but goes through inserts
  -d --debug        enable debug logging (low-level)

You must provide the 7shifts API key with an environment variable called
API_KEY_7SHIFTS.

"""
import logging
from lib7shifts.exceptions import APIError
from .user import get_users
from .common import print_api_item, Sync7Shifts2Sqlite

LOG = logging.getLogger('lib7shifts.cli.user')


class SyncWages2Sqlite(Sync7Shifts2Sqlite):
    """Extend :class:`Sync7Shifts2Sqlite` to work for 7shifts wages."""

    table_name = 'wages'
    table_schema = """CREATE TABLE IF NOT EXISTS {table_name} (
            category NOT NULL,
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            effective_date,
            wage_type NOT NULL,
            wage_cents NOT NULL,
            PRIMARY KEY (category, user_id, role_id)
        ) WITHOUT ROWID"""
    insert_query = """INSERT OR REPLACE INTO {table_name}
        VALUES(?, ?, ?, ?, ?, ?)"""
    insert_fields = (
        'category', 'user_id', 'role_id', 'effective_date',
        'wage_type', 'wage_cents')


def get_wages(args, page_size=200):
    """First, get a list of users direct from the API, then call the
    `get_wages()` method for each user and yield it out to the caller"""
    for user in get_users(args, page_size, skip_admin=True):
        try:
            for category, data in user.get_wages().items():
                for wage in data:
                    if wage['role_id']:
                        wage['category'] = category
                        yield wage
        except APIError as err:
            LOG.error(
                "Caught error while processing user %s %s: %s",
                user.firstname, user.lastname, err.response)


def main(**args):
    """Run the cli-specified action (list, sync, init_schema)"""
    if args.get('list', False):
        for wage in get_wages(args):
            print_api_item(wage)
    elif args.get('db', False):
        sync_db = SyncWages2Sqlite(
            args.get('<sqlite_db>'),
            dry_run=args.get('--dry-run'))
        if args.get('sync', False):
            sync_db.sync_to_database(get_wages(args))
        elif args.get('init', False):
            sync_db.init_db_schema()
        else:
            raise RuntimeError("no valid db action specified")
    else:
        raise RuntimeError("no valid action in args")
    return 0
