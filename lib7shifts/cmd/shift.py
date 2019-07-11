#!/usr/bin/env python3
"""usage:
  7shifts shift list [options]
  7shifts shift sync [options] [--] <sqlite_db>
  7shifts shift init_schema [options] [--] <sqlite_db>

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
from docopt import docopt
import sys
import os
import os.path
import datetime
import sqlite3
import logging
import lib7shifts
from .util import filter_fields

DB_NAME = 'shifts'
DB_TBL_SCHEMA = """CREATE TABLE IF NOT EXISTS {} (
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
) WITHOUT ROWID
""".format(DB_NAME)
DB_INSERT_QUERY = """INSERT OR REPLACE INTO {}
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
           ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(DB_NAME)
INSERT_FIELDS = ('id', 'start', 'end', 'location_id', 'user_id', 'role_id',
                 'department_id', 'close', 'notes', 'hourly_wage', 'open',
                 'notified', 'open_offer_type', 'draft', 'deleted', 'bd',
                 'status', 'late_minutes', 'created', 'modified')
_DB_HNDL = None
_CRSR = None


def db_handle(args):
    global _DB_HNDL
    if _DB_HNDL is None:
        _DB_HNDL = sqlite3.connect(args.get('<sqlite_db>'))
    return _DB_HNDL


def cursor(args):
    global _CRSR
    if _CRSR is None:
        _CRSR = db_handle(args).cursor()
    return _CRSR


def db_init_schema(args):
    tbl_schema = DB_TBL_SCHEMA
    print('initializing db schema', file=sys.stderr)
    print(tbl_schema, file=sys.stderr)
    cursor(args).execute(tbl_schema)


def db_query(args, shifts):
    cursor(args).executemany(
        DB_INSERT_QUERY, filter_fields(
            shifts, INSERT_FIELDS, print_rows=args.get('--debug', False)))
    if args.get('--dry-run', False):
        db_handle(args).rollback()
    else:
        db_handle(args).commit()


def db_sync(args, per_pass=100):
    if args.get('--debug', False):
        print("syncing database with args {}".format(args), file=sys.stderr)
    shifts = []
    shift_count = 0
    for shift in get_shifts(args):
        shifts.append(shift)
        shift_count += 1
        if len(shifts) == per_pass:
            db_query(args, shifts)
            shifts = []
    db_query(args, shifts)
    if args.get('--debug', False):
        print("synced {:d} shifts".format(shift_count), file=sys.stderr)
    if args.get('--dry-run', False):
        db_handle(args).rollback()
    else:
        db_handle(args).commit()


def get_api_key():
    try:
        return os.environ['API_KEY_7SHIFTS']
    except KeyError:
        raise AssertionError("API_KEY_7SHIFTS not found in environment")


def build_list_shift_args(args, limit=500, offset=0):
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
    if args.get('--debug', False):
        print("list_shift args: {}".format(list_args), file=sys.stderr)
    return list_args


def get_shifts(args, page_size=500):
    "Page size: how many results to fetch from the API at a time"
    client = lib7shifts.get_client(get_api_key())
    offset = 0
    results = 0
    while True:
        if args.get('--debug', False):
            print("getting up to {} shifts at offset {}".format(page_size, offset),
                  file=sys.stderr)
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
    if args.get('--debug', False):
        print("returned {} results".format(results), file=sys.stderr)


def main(**args):
    if args.get('list', False):
        for shift in get_shifts(args):
            print(shift)
    elif args.get('sync', False):
        db_sync(args)
    elif args.get('init_schema', False):
        db_init_schema(args)
    else:
        print("no valid action in args", file=sys.stderr)
        print(args, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    args = docopt(__doc__, version='7shifts 0.1')
    logging.basicConfig()
    if args['--debug']:
        logging.getLogger().setLevel(logging.DEBUG)
        print("arguments: {}".format(args), file=sys.stderr)
    else:
        logging.getLogger('lib7shifts').setLevel(logging.INFO)
    sys.exit(main(**args))
