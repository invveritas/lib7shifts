"""usage:
  7shifts daily_sales_labor <location_id> <start_date> <end_date> [options]

Filter parameters:

  --department-id=ID  a numerical department id (optional)

General options:
  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)

Dates should be in YYYY-MM-DD format, in the local timezone.

Note that this command is unique in that it uses a location ID rather than a
company ID. It's easy to get confused with so many other API endpoints using
the company ID. Also, experimentation shows that --department-id, though
supported in the documentation, does not work as of February 2023 (no 
sales or labour data is returned -- all are zeroes).

You must provide the 7shifts API key with an environment variable called
ACCESS_TOKEN_7SHIFTS.

"""
import lib7shifts
from .common import (
    get_7shifts_client, print_api_item)


def build_args(args):
    """Build a list of arguments to provide to
    :func:`lib7shifts.get_daily_sales_and_labor` based on user args."""
    list_args = {
        'start_date': args.get('<start_date>'),
        'end_date': args.get('<end_date>'),
        'location_id': args.get('<location_id>')
    }
    if args.get('--department-id'):
        list_args['department_id'] = args.get('--department-id')
    return list_args


def get_daily_labor(args):
    "Return sales and labour data from the 7shifts API (raw dict form)"
    client = get_7shifts_client()
    return lib7shifts.get_daily_sales_and_labor(
        client,
        **build_args(args))


def main(**args):
    """Run the cli-specified action (list, sync, init_schema)"""

    print_api_item(get_daily_labor(args))

    return 0
