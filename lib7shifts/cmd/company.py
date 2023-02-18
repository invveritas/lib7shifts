"""usage:
  7shifts company list [options]

  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)

You must provide a 7shifts access token with an environment variable called
ACCESS_TOKEN_7SHIFTS.

"""
import logging
import lib7shifts
from .common import get_7shifts_client, print_api_data


LOG = logging.getLogger('lib7shifts.cli.company')


def list_companies():
    "Return a list of :class:`lib7shifts.company.Company` objects from the API"
    client = get_7shifts_client()
    return lib7shifts.list_companies(client)


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        count = print_api_data(list_companies())
        LOG.info("%d companies found", count)
    else:
        raise RuntimeError("no valid action in args")
    return 0
