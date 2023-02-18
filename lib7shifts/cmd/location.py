"""usage:
  7shifts location list <company_id> [options]
  7shifts location get <company_id> <location_id> [options]

Ordering parameters for list operations:

  --modified-since=YYYY-MM-DD

General options:

  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)

You must provide a 7shifts access token with an environment variable called
ACCESS_TOKEN_7SHIFTS.

"""
import logging
import lib7shifts
from .common import get_7shifts_client, print_api_data, print_api_object


LOG = logging.getLogger('lib7shifts.7shifts.location')


def build_args_for_list_locations(args):
    list_args = {}
    if args.get('--modified-since'):
        list_args['modified_since'] = args.get('--modified-since')
    LOG.debug("list_locations parameters: %s", list_args)
    return list_args


def list_locations(args):
    """Return a list of :class:`lib7shifts.location.Location` objects from
    the API"""
    client = get_7shifts_client()
    return lib7shifts.list_locations(client, args.get('<company_id>'))


def get_location(args):
    "Retrieve a single location from the API"
    client = get_7shifts_client()
    return lib7shifts.get_location(
        client, args.get('<company_id>'), args.get('<location_id>'))


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        count = print_api_data(list_locations(args))
        LOG.info("%d locations found", count)
    elif args.get('get', False):
        print_api_object(get_location(args))
    else:
        raise RuntimeError("no valid action in args")
    return 0
