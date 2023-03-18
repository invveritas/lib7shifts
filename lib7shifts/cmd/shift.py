#!/usr/bin/env python3
"""usage:
  7shifts shift list <company_id> [options]
  7shifts shift get <company_id> <shift_id> [options]

Filtering options for list operations:

  --department-id=NN  a department to narrow down on, by id
  --department-ids=NN  a comma-separated list of department IDs to filter on
  --location-id=NN  a location to narrow down on, by id
  --shift-ids=NN    a comma-separated list of shift IDs to return data for
  --role-id=NN      specify a particular role, by id
  --user-id=NN      return shifts for a particular user, by id
  --start-before-on=DD  return shifts that start on or before date
  --start-on-after=DD  return shifts that start on or after date
  --end-before-on=DD  return shifts that end on or before date
  --end-on-after=DD  return shifts that end on or after date
  --deleted         return shifts that were published and since deleted
  --draft-only      return only un-published shifts in results
                    (overrides --deleted)
  --include-draft   include un-published shifts in the results
  --open            return only open shifts in results
  --modified-since=DD  Return shifts modifed since date (inclusive)
  --sort-by-end     sort by shift end time
  --sort-by-start   sort by shift start time
  --sort-asc        Sort ascending by time order
  --sort-desc       Sort descending by time order

Note, get operations also support the --deleted parameter. Dates are in
ISO8601 format and support values like YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, or
YYYY-MM-DDTHH:MM:SS-07:00. --modified-since only supports YYYY-MM-DD format
due to API restrictions.

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


LOG = logging.getLogger('lib7shifts.7shifts.shift')


def build_list_shift_args(args):
    """Build a set of arguments to pass to the API based on the user's
    specified filters"""
    list_args = dict()
    if args.get('--department-id'):
        list_args['department_id'] = args.get('--department-id')
    if args.get('--department-ids'):
        list_args['department_ids'] = args.get('--department-ids')
    if args.get('--location-id'):
        list_args['location_id'] = args.get('--location-id')
    if args.get('--shift-ids'):
        list_args['shift_ids'] = args.get('--shift-ids')
    if args.get('--role-id'):
        list_args['role_id'] = args.get('--role-id')
    if args.get('--user-id'):
        list_args['user_id'] = args.get('--user-id')
    if args.get('--start-before-on'):
        list_args['start[lte]'] = args.get('--start-before-on')
    if args.get('--start-on-after'):
        list_args['start[gte]'] = args.get('--start-on-after')
    if args.get('--end-before-on'):
        list_args['end[lte]'] = args.get('--end-before-on')
    if args.get('--end-on-after'):
        list_args['end[gte]'] = args.get('--end-on-after')
    if args.get('--draft-only'):
        list_args['draft'] = True
    elif args.get('--deleted'):
        list_args['deleted'] = True
    if args.get('--include-draft'):
        list_args['include_draft'] = True
    if args.get('--open'):
        list_args['open'] = True
    if args.get('--modified-since'):
        list_args['modified_since'] = parse_last_modified(
            args.get('--modified-since'))
    if args.get('--sort-by-end'):
        list_args['sort_by'] = 'end'
    elif args.get('--sort-by-start'):
        list_args['sort_by'] = 'start'
    if args.get('--sort-asc'):
        list_args['sort_dir'] = 'asc'
    elif args.get('--sort-desc'):
        list_args['sort_dir'] = 'desc'
    LOG.debug("list_shift args: %s", list_args)
    return list_args


def list_shifts(args):
    "Use the API to return shifts based on CLI filter parameters"
    client = get_7shifts_client()
    return lib7shifts.list_shifts(
        client, args.get('<company_id>'), **build_list_shift_args(args))


def get_shifts(args):
    "Use the API to retrieve a specific shift"
    client = get_7shifts_client()
    params = {}
    if args.get('--deleted'):
        params['include_deleted'] = True
    return lib7shifts.get_shift(
        client, args.get('<company_id>'), args.get('<shift_id>'), **params)


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        count = print_api_data(list_shifts(args))
        LOG.info("%d shifts found", count)
    elif args.get('get'):
        print_api_object(get_shifts(args))
    else:
        raise RuntimeError("no valid action in args")
    return 0
