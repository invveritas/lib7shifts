"""usage:
  7shifts receipt list <company_id> <location_id> [options]
  7shifts receipt get <company_id> <receipt_id> [options]

Filter parameters for list operations:

  --receipt-before-or-on=DD  return receipts on/before date
  --receipt-on-or-after=DD  return receipts on or after date
  --modified-since=DD       return receipts modified on/after date
  --open                    return open receipts
  --closed                  return closed receipts
  --voided                  return voided receipts
  --deleted                 return deleted receipts
  --external-user-id=DD     return receipts created by the specified ID

All dates must be in YYYY-MM-DD format, and cannot be greater than 90 days in
the past. Receipts older than 90 days will not be included.

General parameters:

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


LOG = logging.getLogger('lib7shifts.7shifts.receipt')


def build_list_args(args):
    list_args = {}
    if args.get('<location_id>'):
        list_args['location_id'] = args.get('<location_id>')
    if args.get('--receipt-before-or-on'):
        list_args['receipt_date[lte]'] = args.get('--receipt-before-or-on')
    if args.get('--receipt-on-or-after'):
        list_args['receipt_date[gte]'] = args.get('--receipt-on-or-after')
    if args.get('--modified-since'):
        list_args['modified_since'] = parse_last_modified(
            args.get('--modified-since'))
    if args.get('--open'):
        list_args['status'] = 'open'
    elif args.get('--closed'):
        list_args['status'] = 'closed'
    elif args.get('--voided'):
        list_args['status'] = 'voided'
    elif args.get('--deleted'):
        list_args['status'] = 'deleted'
    if args.get('--external-user-id'):
        list_args['external_user_id'] = args.get('--external-user-id')
    LOG.debug("list_receipts arguments: %s", list_args)
    return list_args


def list_receipts(args):
    "Return a list of :class:`lib7shifts.company.Company` objects from the API"
    client = get_7shifts_client()
    return lib7shifts.list_receipts(
        client, args.get('<company_id>'),
        **build_list_args(args))


def get_receipt(args):
    "Get a single receipt from the API"
    client = get_7shifts_client()
    return lib7shifts.get_receipt(
        client, args.get('<company_id>'), args.get('<receipt_id>'))


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        returned = print_api_data(list_receipts(args))
        LOG.info("%d sales receipts found", returned)
    elif args.get('get'):
        print_api_object(get_receipt(args))
    else:
        raise RuntimeError("no valid action in args")
    return 0
