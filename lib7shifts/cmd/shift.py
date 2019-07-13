#!/usr/bin/env python3
"""usage:
  7shifts shift list [options]
  7shifts shift db sync [options] [--] <sqlite_db>
  7shifts shift db init [options] [--] <sqlite_db>

  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)
  --dry-run         does not commit data to database, but goes through inserts
  -s --start=DATE   start date (and optional time) to return shifts for
  -e --end=DATE     end date (and optional time) to stop returning shifts after
  --deleted         include deleted shifts in results
  --draft           include draft shifts in results
  --open            whether or not to ONLY return open shifts in results
  --dept-id=NN      specify a department to narrow down on, by id
  --location-id=NN  specify a location to narrow down on, by id

You must provide the 7shifts API key with an environment variable called
API_KEY_7SHIFTS.

"""
import logging
import lib7shifts
from .common import get_7shifts_client, print_api_data, Sync7Shifts2Sqlite

LOG = logging.getLogger('lib7shifts.7shifts.shift')


class SyncShifts2Sqlite(Sync7Shifts2Sqlite):
    """Extend :class:`Sync7Shifts2Sqlite` to work for 7shifts shifts."""

    table_name = 'shifts'
    table_schema = """CREATE TABLE IF NOT EXISTS {table_name} (
            id PRIMARY KEY UNIQUE,
            start NOT NULL,
            end NOT NULL,
            location_id NOT NULL,
            user_id NOT NULL,
            role_id NOT NULL,
            department_id NOT NULL,
            close,
            notes,
            hourly_wage,
            open,
            notified,
            open_offer_type,
            draft,
            deleted,
            bd,
            status,
            late_minutes,
            created,
            modified
        ) WITHOUT ROWID"""
    insert_query = """INSERT OR REPLACE INTO {table_name}
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
               ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    insert_fields = (
        'id', 'start', 'end', 'location_id', 'user_id', 'role_id',
        'department_id', 'close', 'notes', 'hourly_wage', 'open',
        'notified', 'open_offer_type', 'draft', 'deleted', 'bd',
        'status', 'late_minutes', 'created', 'modified')


def build_list_shift_args(args, limit=500, offset=0):
    """Build a set of arguments to pass to the API based on the user's
    specified filters"""
    list_args = {}
    if args.get('--start'):
        list_args['start[gte]'] = args.get('--start')
    if args.get('--end'):
        list_args['start[lte]'] = args.get('--end')
    if args.get('--location-id'):
        list_args['location_id'] = args.get('--location-id')
    if args.get('--dept-id'):
        list_args['department_id'] = args.get('--dept-id')
    list_args['deleted'] = args.get('--deleted')
    list_args['draft'] = args.get('--draft')
    list_args['open'] = args.get('--open')
    list_args['limit'] = limit  # 500 seems to be the API limit
    list_args['offset'] = offset
    LOG.debug("list_shift args: %s", list_args)
    return list_args


def get_shifts(args, page_size=500):
    "Page size: how many results to fetch from the API at a time"
    client = get_7shifts_client()
    offset = 0
    results = 0
    while True:
        LOG.debug(
            "getting up to %d shifts at offset %d",
            page_size, offset)
        shifts = lib7shifts.list_shifts(
            client,
            **build_list_shift_args(args, limit=page_size, offset=offset))
        if shifts:
            for shift in shifts:
                results += 1
                yield shift
            offset += len(shifts)
            continue
        break
    LOG.debug("returned %s shifts", results)


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        print_api_data(get_shifts(args))
    elif args.get('db', False):
        sync_db = SyncShifts2Sqlite(
            args.get('<sqlite_db>'),
            dry_run=args.get('--dry-run'))
        if args.get('sync', False):
            sync_db.sync_to_database(get_shifts(args))
        elif args.get('init', False):
            sync_db.init_db_schema()
        else:
            raise RuntimeError("no valid db action specified")
    else:
        raise RuntimeError("no valid action in args")
    return 0
