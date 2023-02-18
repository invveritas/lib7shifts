#!/usr/bin/env python3
"""usage:
  7shifts wage get [options] <company_id> <user_id>

  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)

You must provide a 7shifts access token with an environment variable called
ACCESS_TOKEN_7SHIFTS.

"""
import logging
import lib7shifts
from .common import get_7shifts_client, print_api_item

LOG = logging.getLogger('lib7shifts.cli.user')


def get_wages_by_user_id(args):
    """Given a user id, retreive wages from the API for that user"""
    client = get_7shifts_client()
    return lib7shifts.list_user_wages(
        client, args.get('<company_id>'), args.get('<user_id>'))


def main(**args):
    """Run the cli-specified action (list, sync, init_schema)"""
    if args.get('get', False):
        print_api_item(get_wages_by_user_id(args))
    else:
        raise RuntimeError("no valid action in args")
    return 0
