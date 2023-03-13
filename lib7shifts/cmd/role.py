#!/usr/bin/env python3
"""usage:
  7shifts role list <company_id> [options]
  7shifts role get <company_id> <role_id> [options]

Ordering options for list operations:

  --order-field=F   the name of a field to order by
  --order-asc       order ascending
  --order-desc      order descending
  --modified-since=DD  A YYYY-MM-DD formatted string to find roles
                    modified on/after a date.

General options:

  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)

You must provide a 7shifts access token with an environment variable called
ACCESS_TOKEN_7SHIFTS.

"""
import logging
import lib7shifts
from .util import parse_last_modified
from .common import get_7shifts_client, print_api_data, print_api_object


LOG = logging.getLogger('lib7shifts.7shifts.role')


def build_list_args(args):
    list_args = {}
    if args.get('--order-field'):
        list_args['order_field'] = args.get('--order-field')
    if args.get('--order-asc'):
        list_args['order_dir'] = 'asc'
    elif args.get('--order-desc'):
        list_args['order_dir'] = 'desc'
    if args.get('--modified-since'):
        list_args['modified_since'] = parse_last_modified(
            args.get('--modified-since'))
    LOG.debug("list_roles parameters: %s", list_args)
    return list_args


def list_roles(args):
    """Return a list of :class:`lib7shifts.role.Role` objects from
    the API"""
    client = get_7shifts_client()
    return lib7shifts.list_roles(
        client, args.get('<company_id>'), **build_list_args(args))


def get_role(args):
    """Retrieve a single role from the 7shifts API"""
    client = get_7shifts_client()
    return lib7shifts.get_role(
        client, args.get('<company_id>'), args.get('<role_id>'))


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        count = print_api_data(list_roles(args))
        LOG.info('%d roles found', count)
    elif args.get('get'):
        print_api_object(get_role(args))
    else:
        raise RuntimeError("no valid action in args")
    return 0
