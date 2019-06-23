#!/usr/bin/env python3
"""usage:
  7time_punches2sqlite time_punch list [options]
  7time_punches2sqlite time_punch sync [options] [--] <sqlite_db>
  7time_punches2sqlite time_punch init_schema [options] [--] <sqlite_db>

  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)
  --dry-run         does not commit data to database, but goes through inserts
  -s --start=DATE   start date (and optional time) to return time_punches for
  -e --end=DATE     end date (and optional time) to stop returning time_punches after
  --unapproved      include unapproved time_punches in results
  --only-unapproved  ONLY include unapproved time_punches in results
  --dept-id=NN      specify a department to narrow down on, by id
  --location-id=NN  specify a location to narrow down on, by id

You must provide the 7time_punches API key with an environment variable called
API_KEY_7time_punches.

"""
from docopt import docopt
import sys, os, os.path
import datetime
import sqlite3
import logging
import lib7shifts

DB_NAME = 'time_punches'
DB_TBL_SCHEMA = """CREATE TABLE IF NOT EXISTS {} (
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
) WITHOUT ROWID
""".format(DB_NAME)
DB_INSERT_QUERY = """INSERT OR REPLACE INTO {}
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
           ?, ?, ?, ?)""".format(DB_NAME)
INSERT_FIELDS = ('id', 'shift_id', 'user_id', 'location_id', 'role_id',
                 'department_id', 'approved', 'clocked_in', 'clocked_out',
                 'auto_clocked_out', 'clocked_in_offline', 'clocked_out_offline',
                 'created', 'modified')
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

def filter_time_punch_fields(time_punches, output_fields):
    """Given a list of time_punch dicts from 7shifts, yield a tuple per time_punch with the
    data we need to insert"""
    for time_punch in time_punches:
        row = list()
        for field in output_fields:
            val = getattr(time_punch, field)
            if isinstance(val, datetime.datetime):
                val = val.__str__()
            row.append(val)
        #print(row, file=sys.stdout)
        yield row

def db_query(args, time_punches):
    try:
        cursor(args).executemany(
            DB_INSERT_QUERY, filter_time_punch_fields(time_punches, INSERT_FIELDS))
    except Exception as err:
        print("exception: {}".format(err), file=sys.stderr)
        for row in filter_time_punch_fields(time_punches, INSERT_FIELDS):
            print(row, file=sys.stderr)
        sys.exit(1)

def db_sync(args, per_pass=100):
    print("syncing database", file=sys.stderr)
    time_punches = []
    for time_punch in get_time_punches(args):
        time_punches.append(time_punch)
        if len(time_punches) == per_pass:
            db_query(args, time_punches)
            time_punches = []
    db_query(args, time_punches)
    if args.get('--dry-run', False):
        db_handle(args).rollback()
    else:
        db_handle(args).commit()

def get_api_key():
    try:
        return os.environ['API_KEY_7SHIFTS']
    except KeyError:
        raise AssertionError("API_KEY_7SHIFTS not found in environment")

def build_list_time_punch_args(args, limit=500, offset=0):
    list_args = {}
    if args.get('--start'):
        list_args['clocked_in[gte]'] = args.get('--start')
    if args.get('--end'):
        list_args['clocked_in[lte]'] = args.get('--end')
    if args.get('--location-id'):
        list_args['location_id'] = args.get('--location-id')
    if args.get('--dept-id'):
        list_args['department_id'] = args.get('--dept-id')
    list_args['limit'] = limit # 500 seems to be the API limit
    list_args['offset'] = offset
    return list_args

def get_time_punches(args, page_size=500):
    "Page size: how many results to fetch from the API at a time"
    client = lib7shifts.get_client(get_api_key())
    offset = 0
    results = 0
    while True:
        if args.get('--debug', False):
            print("getting up to {} time_punches at offset {}".format(page_size, offset),
                  file=sys.stderr)
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
    if args.get('--debug', False):
        print("returned {} results".format(results), file=sys.stderr)

def main(**args):
    logging.basicConfig()
    if args['--debug']:
        logging.getLogger().setLevel(logging.DEBUG)
        print("arguments: {}".format(args), file=sys.stderr)
    else:
        logging.getLogger('lib7shifts').setLevel(logging.INFO)
    if args.get('list', False):
        for time_punch in get_time_punches(args):
            print(time_punch)
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
    args = docopt(__doc__, version='7shifts2sqlite 0.1')
    sys.exit(main(**args))
