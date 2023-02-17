#!/usr/bin/env python3
"""usage:
  7shifts user get [options] <company_id> <user_id>
  7shifts user list <company_id> [options]
  7shifts user db sync <company_id> [options] [--] <sqlite_db>
  7shifts user db init [options] [--] <sqlite_db>

Filtering options for 'list' operations:

  --modified-since=YYYY-MM-DD  optionally list users modified after a date
  --location-id=N   restrict to users at a particular location ID
  --department-id=N  restrict to a particular department ID
  --role-id=N       restrict to a particular department
  --name=SS         filter by full or partial employee name
  --inactive        get inactive users (default is active only)

Standard options:
  -h --help         show this screen
  -v --version      show version information
  --dry-run         does not commit data to database, but goes through inserts
  -d --debug        enable debug logging (low-level)

You must provide the 7shifts API key with an environment variable called
ACCESS_TOKEN_7SHIFTS.

"""
import logging
import lib7shifts
from .common import (
    get_7shifts_client, print_api_data, print_api_object, Sync7Shifts2Sqlite)

LOG = logging.getLogger('lib7shifts.cli.user')


class SyncUsers2Sqlite(Sync7Shifts2Sqlite):
    """Extend :class:`Sync7Shifts2Sqlite` to work for 7shifts users."""

    table_name = 'users'
    table_schema = """CREATE TABLE IF NOT EXISTS {table_name} (
            id PRIMARY KEY UNIQUE,
            firstname NOT NULL,
            lastname NOT NULL,
            email,
            payroll_id,
            active NOT NULL,
            user_type_id NOT NULL,
            hire_date,
            company_id NOT NULL,
            wage_type,
            created NOT NULL,
            modified NOT NULL,
            birth_date
        ) WITHOUT ROWID"""
    insert_query = """INSERT OR REPLACE INTO {table_name}
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    insert_fields = (
        'id', 'firstname', 'lastname', 'email', 'payroll_id',
        'active', 'user_type_id', 'hire_date', 'company_id',
        'wage_type', 'created', 'modified', 'birth_date')


class SyncUsersRole2Sqlite(Sync7Shifts2Sqlite):
    """Extend :class:`Sync7Shifts2Sqlite` to work for 7shifts user's roles."""

    table_name = 'users_role'
    table_schema = """CREATE TABLE IF NOT EXISTS {table_name} (
            id PRIMARY KEY UNIQUE,
            user_id NOT NULL,
            role_id NOT NULL,
            sort_order,
            hourly_wage,
            skill_level,
            is_primary,
            deleted,
            created,
            modified
        ) WITHOUT ROWID"""
    insert_query = """INSERT OR REPLACE INTO {table_name}
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    insert_fields = (
        'id', 'user_id', 'role_id', 'sort', 'hourly_wage',
        'skill_level', 'primary', 'deleted', 'created', 'modified')


def build_list_user_args(args):
    """Build a set of parameters to send to the API based on the user-
    specified arguments"""
    list_args = {'status': 'active'}
    if args.get('--inactive'):
        list_args['status'] = 'inactive'
    if args.get('--modified-since'):
        list_args['modified_since'] = args.get('--modified-since')
    if args.get('--location-id'):
        list_args['location_id'] = args.get('--location-id')
    elif args.get('--department-id'):
        list_args['department_id'] = args.get('--department-id')
    elif args.get('--role-id'):
        list_args['role_id'] = args.get('--role-id')
    return list_args


def get_user(company_id, user_id, deep=0):
    """Returns a single user from the 7shifts API based on the user ID"""
    client = get_7shifts_client()
    fields = dict()
    if deep:
        fields['deep'] = 1
    return lib7shifts.get_user(client, company_id, user_id, fields=fields)


def list_users(args):
    """Get a list of users from the 7shifts API"""
    client = get_7shifts_client()
    return lib7shifts.list_users(
        client, args.get('<company_id>'), **build_list_user_args(args))


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    deep = 0
    if args.get('--deep', False):
        deep = 1
    if args.get('list', False):
        print_api_data(list_users(args))
    elif args.get('get', False):
        print_api_object(get_user(
            args.get('<company_id>'), args.get('<user_id>')))
    elif args.get('db', False):
        sync_user_db = SyncUsers2Sqlite(
            args.get('<sqlite_db>'),
            dry_run=args.get('--dry-run'))
        sync_user_roles_db = SyncUsersRole2Sqlite(
            args.get('<sqlite_db>'),
            dry_run=args.get('--dry-run'))
        if args.get('sync', False):
            args['--deep'] = 1  # a deep fetch is required for this
            users = list()
            user_roles = list()
            for user in list_users(args):
                users.append(user)
                for role in user.get_roles():
                    user_roles.append(role.users_role)
            sync_user_db.sync_to_database(users)
            sync_user_roles_db.sync_to_database(user_roles)
        elif args.get('init', False):
            sync_user_db.init_db_schema()
            sync_user_roles_db.init_db_schema()
        else:
            raise RuntimeError("no valid db action specified")
    else:
        raise RuntimeError("no valid action in args")
    return 0
