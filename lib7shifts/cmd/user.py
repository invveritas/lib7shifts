#!/usr/bin/env python3
"""usage:
  7shifts user get [options] <company_id> <user_id>
  7shifts user list <company_id> [options]

Filtering options for 'list' operations:

  --modified-since=YYYY-MM-DD  optionally list users modified after a date
  --location-id=N   restrict to users at a particular location ID
  --department-id=N  restrict to a particular department ID
  --role-id=N       restrict to a particular department
  --name=SS         filter by full or partial employee name
  --inactive        return inactive users ONLY (default is active only)

Standard options:
  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)

You must provide a 7shifts access token with an environment variable called
ACCESS_TOKEN_7SHIFTS.

"""
import logging
import lib7shifts
from .common import (
    get_7shifts_client, print_api_data, print_api_object)


LOG = logging.getLogger('lib7shifts.cli.user')


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
    if args.get('--name'):
        list_args['name'] = args.get('--name')
    elif args.get('--department-id'):
        list_args['department_id'] = args.get('--department-id')
    elif args.get('--role-id'):
        list_args['role_id'] = args.get('--role-id')
    LOG.debug("list_users arguments: %s", list_args)
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
    """Run the cli-specified action (list, get)"""
    if args.get('list', False):
        count = print_api_data(list_users(args))
        LOG.info("%d users found", count)
    elif args.get('get', False):
        print_api_object(get_user(
            args.get('<company_id>'), args.get('<user_id>')))
    else:
        raise RuntimeError("no valid action in args")
    return 0
