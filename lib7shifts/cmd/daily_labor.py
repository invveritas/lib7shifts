"""usage:
  7shifts daily_labor list --loc=ID --week=D [options]

Options:
  -h --help         show this screen
  -v --version      show version information
  --dry-run         does not commit data to database, but goes through inserts
  -d --debug        enable debug logging (low-level)
  --week=D          the starting date to pull data for
  --loc=ID          a numeric id for the location in question
  --unapproved      include unapproved labour in report

Dates should be in YYYY-MM-DD format, in the local timezone.

You must provide the 7shifts API key with an environment variable called
API_KEY_7SHIFTS.

"""
import lib7shifts
from .common import (
    get_7shifts_client, print_api_item)


def build_args(args):
    """Build a list of arguments to provide to
    :func:`lib7shifts.get_sales_and_labour` based on user args."""
    list_args = {}
    if args.get('--unapproved'):
        list_args['include_unapproved'] = True
    if args.get('--loc'):
        list_args['location_id'] = args.get('--loc')
    if args.get('--week'):
        list_args['week'] = args.get('--week')
    return list_args


def get_daily_labor(args):
    "Return sales and labour data from the 7shifts API (raw dict form)"
    client = get_7shifts_client()
    return lib7shifts.get_daily_labor(
        client,
        **build_args(args))


def main(**args):
    """Run the cli-specified action (list, sync, init_schema)"""
    if args.get('list', False):
        data = get_daily_labor(args)
        print_api_item(data)
    else:
        raise RuntimeError("no valid action in args")
    return 0
