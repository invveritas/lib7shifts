"""usage:
  7shifts department list <company_id> [options]
  7shifts department get <company_id> <department_id> [options]

Filtering options for list operations:

  --modified-since=YYYY-MM-DD
  --location-id=DD  filter by location

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


LOG = logging.getLogger('lib7shifts.cli.department')


def build_list_args(args):
    list_args = {}
    if args.get('--modified-since'):
        list_args['modified_since'] = args.get('--modified-since')
    if args.get('--location-id'):
        list_args['location_id'] = args.get('--location-id')
    LOG.debug("list_departments parameters: %s", list_args)
    return list_args


def list_departments(args):
    "Return a list of :class:`lib7shifts.company.Company` objects from the API"
    client = get_7shifts_client()
    return lib7shifts.list_departments(client, args.get('<company_id>'))


def get_department(args):
    "Retrieve a single department from the 7shifts API"
    client = get_7shifts_client()
    return lib7shifts.get_department(
        client, args.get('<company_id>'), args.get('<department_id>'))


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        count = print_api_data(list_departments(args))
        LOG.info("%d departments found", count)
    elif args.get('get', False):
        print_api_object(get_department(args))
    else:
        raise RuntimeError("no valid action in args")
    return 0
