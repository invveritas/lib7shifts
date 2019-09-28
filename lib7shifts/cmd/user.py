#!/usr/bin/env python3
"""usage:
  7shifts user get [options] <user_id>
  7shifts user list [options]
  7shifts user db sync [options] [--] <sqlite_db>
  7shifts user db init [options] [--] <sqlite_db>

  -h --help         show this screen
  -v --version      show version information
  --dry-run         does not commit data to database, but goes through inserts
  -d --debug        enable debug logging (low-level)
  --with-inactive   include inactive users
  --deep            deep-scan of user data (get/list only)

You must provide the 7shifts API key with an environment variable called
API_KEY_7SHIFTS.

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
            payroll_id UNIQUE,
            active NOT NULL,
            user_type_id NOT NULL,
            hire_date,
            company_id NOT NULL
        ) WITHOUT ROWID"""
    insert_query = """INSERT OR REPLACE INTO {table_name}
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    insert_fields = (
        'id', 'firstname', 'lastname', 'email', 'payroll_id',
        'active', 'user_type_id', 'hire_date', 'company_id')


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


def build_list_user_args(args, active=1, limit=500, offset=0):
    """Build a set of parameters to send to the API based on the user-
    specified arguments"""
    list_args = {}
    list_args['active'] = active
    list_args['limit'] = limit
    list_args['offset'] = offset
    if args.get('--deep'):
        list_args['deep'] = 1
    return list_args


def get_user(user_id, deep=0):
    """Returns a single user from the 7shifts API based on the user ID"""
    client = get_7shifts_client()
    fields = dict()
    if deep:
        fields['deep'] = 1
    return lib7shifts.get_user(client, user_id, fields=fields)


def get_users(args, page_size=200, skip_admin=False):
    """Get a list of users from the 7shifts API"""
    client = get_7shifts_client()
    results = 0
    active_vals = [1]
    if args.get('--with-inactive', False):
        active_vals.append(0)
    for active in active_vals:
        offset = 0
        while True:
            LOG.debug(
                "getting up to %d users (active: %d) at offset %d",
                page_size, active, offset)
            api_args = build_list_user_args(
                args, active=active, limit=page_size, offset=offset)
            users = lib7shifts.list_users(
                client,
                **api_args)
            if users:
                for user in users:
                    if skip_admin and user.is_admin():
                        LOG.info(
                            "Skipping admin user %s %s", user.firstname,
                            user.lastname)
                        continue
                    results += 1
                    yield user
                offset += len(users)
                continue
            break
    LOG.debug("returned %d users", results)


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    deep = 0
    if args.get('--deep', False):
        deep = 1
    if args.get('list', False):
        print_api_data(get_users(args))
    elif args.get('get', False):
        print_api_object(get_user(args['<user_id>'], deep=deep))
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
            for user in get_users(args):
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
