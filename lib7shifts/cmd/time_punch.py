#!/usr/bin/env python3
"""usage:
  7shifts time_punch list [options]
  7shifts time_punch db sync [options] [--] <sqlite_db>
  7shifts time_punch db init [options] [--] <sqlite_db>

  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)
  --dry-run         does not commit data to database, but goes through inserts
  -s --start=DATE   start date to return time_punches for
  -e --end=DATE     end date to stop returning time punches after
  --unapproved      include unapproved time_punches in results
  --only-unapproved  ONLY include unapproved time_punches in results
  --dept-id=NN      specify a department to narrow down on, by id
  --location-id=NN  specify a location to narrow down on, by id

You must provide the 7time_punches API key with an environment variable called
API_KEY_7time_punches.

"""
import logging
import lib7shifts
from .common import get_7shifts_client, print_api_data, Sync7Shifts2Sqlite

LOG = logging.getLogger('lib7shifts.7shifts.shift')


class SyncPunches2Sqlite(Sync7Shifts2Sqlite):
    """Extend :class:`Sync7Shifts2Sqlite` to work for 7shifts shifts."""

    table_name = 'time_punches'
    table_schema = """CREATE TABLE IF NOT EXISTS {table_name} (
        id PRIMARY KEY UNIQUE,
        shift_id,
        user_id NOT NULL,
        location_id NOT NULL,
        role_id NOT NULL,
        department_id NOT NULL,
        approved NOT NULL,
        clocked_in NOT NULL,
        clocked_out NOT NULL,
        auto_clocked_out,
        clocked_in_offline,
        clocked_out_offline,
        created,
        modified
    ) WITHOUT ROWID"""
    insert_query = """INSERT OR REPLACE INTO {table_name}
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
               ?, ?, ?, ?)"""
    insert_fields = (
        'id', 'shift_id', 'user_id', 'location_id', 'role_id',
        'department_id', 'approved', 'clocked_in', 'clocked_out',
        'auto_clocked_out', 'clocked_in_offline', 'clocked_out_offline',
        'created', 'modified')


def build_list_time_punch_args(args, limit=500, offset=0):
    """Build a set of arguments to pass to the 7shfits API based on the
    user-specified cli parameters"""
    list_args = {}
    if args.get('--start'):
        list_args['clocked_in[gte]'] = args.get('--start')
    if args.get('--end'):
        list_args['clocked_in[lte]'] = args.get('--end')
    if args.get('--location-id'):
        list_args['location_id'] = args.get('--location-id')
    if args.get('--dept-id'):
        list_args['department_id'] = args.get('--dept-id')
    list_args['limit'] = limit  # 500 seems to be the API limit
    list_args['offset'] = offset
    return list_args


def get_time_punches(args, page_size=500):
    "Page size: how many results to fetch from the API at a time"
    client = get_7shifts_client()
    offset = 0
    results = 0
    while True:
        LOG.debug(
            "getting up to %d time_punches at offset %d",
            page_size, offset)
        time_punches = lib7shifts.list_punches(
            client,
            **build_list_time_punch_args(args, limit=page_size, offset=offset))
        if time_punches:
            for time_punch in time_punches:
                if time_punch.approved:
                    if args.get('--only-unapproved', False):
                        continue
                else:
                    if not (args.get('--unapproved', False) or
                            args.get('--only-unapproved', False)):
                        continue
                results += 1
                yield time_punch
            offset += len(time_punches)
            continue
        break
    LOG.debug("returned %d time punches", results)


def main(**args):
    """Run the cli-specified action (list, sync, init_schema)"""
    if args.get('list', False):
        print_api_data(get_time_punches(args))
    elif args.get('db', False):
        sync_db = SyncPunches2Sqlite(
            args.get('<sqlite_db>'),
            dry_run=args.get('--dry-run'))
        if args.get('sync', False):
            sync_db.sync_to_database(get_time_punches(args))
        elif args.get('init', False):
            sync_db.init_db_schema()
        else:
            raise RuntimeError("no valid db action specified")
    else:
        raise RuntimeError("no valid action in args")
    return 0
