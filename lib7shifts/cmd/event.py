"""usage:
  7shifts event list <company_id> <start_date> <end_date> [options]
  7shifts event get <company_id> <event_id>

Filter parameters for list operations:

  --location-id=SS  integer location ID for event

General parameters:

  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)

<start_date> and <end_date> must be in YYYY-MM-DD format.

You must provide a 7shifts access token with an environment variable called
ACCESS_TOKEN_7SHIFTS.

"""
import logging
import lib7shifts
from .common import get_7shifts_client, print_api_data, print_api_object


LOG = logging.getLogger('lib7shifts.7shifts.event')


def list_events(args):
    "Return a list of :class:`lib7shifts.company.Company` objects from the API"
    client = get_7shifts_client()
    kwargs = {
        'start_date': args.get('<start_date>'),
        'end_date': args.get('<end_date>')
    }
    if args.get('--location-id'):
        kwargs['location_id'] = args.get('--location-id')
    return lib7shifts.list_events(client, args.get('<company_id>'), **kwargs)


def get_event(args):
    "Get a single event from the API"
    client = get_7shifts_client()
    return lib7shifts.get_event(
        client, args.get('<company_id>'), args.get('<event_id>'))


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        count = print_api_data(list_events(args))
        LOG.info("%d events found", count)
    elif args.get('get'):
        print_api_object(get_event(args))
    else:
        raise RuntimeError("no valid action in args")
    return 0
