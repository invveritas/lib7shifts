#!/usr/bin/env python3
"""usage:
  7shifts time_punch list <company_id> [options]
  7shifts time_punch get <company_id> <punch_id> [options]

Filtering/sorting parameters for list operations:

  --location-id=NN      a location to narrow down on, by id
  --department-id=NN    a department to narrow down on, by id
  --role-id=NN          a role to filter on
  --user-id=NN          return punches only for the given user ID
  --unapproved          return unapproved time punches only
  --approved            return approved time punches only
  --modified-since=DD   return punches modified on/after this date (YYYY-MM-DD)
  --clocked-in-on-after=DD  return punches with clock-ins on/after date
  --clocked-in-before-on=DD  return punches with clock-ins before/on date
  --clocked-out-on-after=DD  return punches with clock-outs on/after date
  --clocked-out-before-on=DD  return punches with clock-outs before/on date
  --sort-by=SS          name of a field and direction to sort by.
                        eg: modified.asc or clocked_in.desc

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


LOG = logging.getLogger('lib7shifts.7shifts.time_punch')


def build_list_time_punch_args(args):
    """Build a set of arguments to pass to the 7shfits API based on the
    user-specified cli parameters"""
    list_args = {}
    if args.get('--location-id'):
        list_args['location_id'] = args.get('--location-id')
    if args.get('--department-id'):
        list_args['department_id'] = args.get('--department-id')
    if args.get('--role-id'):
        list_args['role_id'] = args.get('--role-id')
    if args.get('--user-id'):
        list_args['user_id'] = args.get('--user-id')
    if args.get('--unapproved'):
        list_args['approved'] = False
    if args.get('--approved'):
        list_args['approved'] = True
    if args.get('--modified-since'):
        list_args['modified_since'] = parse_last_modified(
            args.get('--modified-since'))
    if args.get('--clocked-in-on-after'):
        list_args['clocked_in[gte]'] = args.get('--clocked-in-on-after')
    if args.get('--clocked-in-before-on'):
        list_args['clocked_in[lte]'] = args.get('--clocked-in-before-on')
    if args.get('--clocked-out-on-after'):
        list_args['clocked_out[gte]'] = args.get('--clocked-out-on-after')
    if args.get('--clocked-out-before-on'):
        list_args['clocked_out[lte]'] = args.get('--clocked-out-before-on')
    if args.get('--sort-by'):
        list_args['sort_by'] = args.get('--sort-by')
    LOG.debug("list_time_punches args: %s", list_args)
    return list_args


def list_time_punches(args):
    "Use the 7shifts API to get a list of time punches based on CLI params"
    client = get_7shifts_client()
    return lib7shifts.list_punches(
        client, args.get('<company_id>'), **build_list_time_punch_args(args))


def get_time_punch(args):
    "Use the 7shifts API to get details about a specific time punch"
    client = get_7shifts_client()
    return lib7shifts.get_punch(
        client, args.get('<company_id>'), args.get('<punch_id>'))


def main(**args):
    """Run the cli-specified action (list, sync, init_schema)"""
    if args.get('list', False):
        count = print_api_data(list_time_punches(args))
        LOG.info("%d time punches found", count)
    elif args.get('get'):
        print_api_object(get_time_punch(args))
    else:
        raise RuntimeError("no valid action in args")
    return 0
