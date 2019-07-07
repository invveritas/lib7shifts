#!/usr/bin/env python3
"""usage:
  7shifts2sqlite user list [options]
  7shifts2sqlite user sync [options] [--] <sqlite_db>
  7shifts2sqlite user init_schema [options] [--] <sqlite_db>

  -h --help         show this screen
  -v --version      show version information
  --dry-run         does not commit data to database, but goes through inserts
  -d --debug        enable debug logging (low-level)
  --only-inactive   only fetch inactive users
  --only-active     only fetch active users

You must provide the 7shifts API key with an environment variable called
API_KEY_7SHIFTS.

"""
from docopt import docopt
import sys
import os
import os.path
import sqlite3
import logging
import lib7shifts
from .util import filter_fields

DB_NAME = 'users'
DB_TBL_SCHEMA = """CREATE TABLE IF NOT EXISTS {} (
    id PRIMARY KEY UNIQUE,
    firstname NOT NULL,
    lastname NOT NULL,
    email,
    payroll_id UNIQUE,
    active NOT NULL,
    hire_date,
    company_id NOT NULL
) WITHOUT ROWID
""".format(DB_NAME)
DB_INSERT_QUERY = """INSERT OR REPLACE INTO {}
    VALUES(?, ?, ?, ?, ?, ?, ?, ?)""".format(DB_NAME)
INSERT_FIELDS = ('id', 'firstname', 'lastname', 'email', 'payroll_id',
                 'active', 'hire_date', 'company_id')
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


def db_sync(args):
    print("syncing database", file=sys.stderr)
    users = get_users(args)
    cursor(args).executemany(
        DB_INSERT_QUERY, filter_fields(
            users, INSERT_FIELDS, print_rows=args.get('--debug', False)))
    if args.get('--dry-run', False):
        db_handle(args).rollback()
    else:
        db_handle(args).commit()


def get_api_key():
    try:
        return os.environ['API_KEY_7SHIFTS']
    except KeyError:
        raise AssertionError("API_KEY_7SHIFTS not found in environment")


def build_list_user_args(args, limit=500, offset=0):
    list_args = {}
    if args.get('--only-inactive'):
        list_args['active'] = 0
    if args.get('--only-active'):
        list_args['active'] = 1
    list_args['limit'] = limit
    list_args['offset'] = offset
    return list_args


def get_users(args, page_size=200):
    client = lib7shifts.get_client(get_api_key())
    offset = 0
    results = 0
    while True:
        if args.get('--debug', False):
            print("getting up to {} users at offset {}".format(page_size, offset),
                  file=sys.stderr)
        users = lib7shifts.list_users(
            client,
            **build_list_user_args(args, limit=page_size, offset=offset))
        if users:
            for user in users:
                results += 1
                yield user
            offset += len(users)
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
        for user in get_users(args):
            print(user)
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
