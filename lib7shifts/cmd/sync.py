#!/usr/bin/env python
"""Migrate 7shifts data to any SQLAlchemy-supported database.

Usage:
  7shifts sync punches [options]
  7shifts sync shifts [options]
  7shifts sync users [options]
  7shifts sync wages [options]
  7shifts sync roles [options]
  7shifts sync receipts [options]
  7shifts sync locations [options]
  7shifts sync companies [options]
  7shifts sync daily_sales_and_labor [options]
  7shifts sync all [options]

Sync Options:

  --db=url              An SQLAlchemy engine url. Required for actual use.
                        [default: sqlite+pysqlite:///:memory:]
  --unapproved          Include unapproved time punches
  --inactive-users      Include deactivated users (default is active only)
  --modified-since=DD   Only sync items modified since the specified date
                        (applies to most synced items)
  --start-date=DD       Sync punches, shifts and receipts starting on the
                        given date (incompatible with --modified-since).
  --end-date=DD         If --start-date is used, specify the last day to sync,
                        defaults to today
  --company-id=NN       Provide a company ID in cases where one cannot be
                        inferred from API data (if you have multiple companies)

Dates are in YYYY-MM-DD format. If neither --modified-since or --start-date
are set, then the date is assumed to be yesterday from 12:00 AM to 11:59 PM.
The url format for --db needs 4 slashes for on-disk paths on *Nix systems.

General Options:

  -h --help             Show this screen
  -v --version          Show version information
  -d --debug            Enable debug logging (low-level)
  --debug-db            Enable database debug logging
  -l --log=FILE         Specify an output log file (instead of stderr),
                        relative to <workdir> if not absolute
  --append-log          Append instead of replacing logfile

You will also need to provide a 7shifts API token with an environment
variable called ACCESS_TOKEN_7SHIFTS.

Note that all sync actions require that you install the latest Pandas and
SQLAlchemy python packages.

"""
import logging
import pandas
import sqlalchemy
from datetime import timedelta, timezone, datetime
from docopt import docopt
import lib7shifts
from lib7shifts.dates import (
    to_local_date, yesterday, to_y_m_d, datetime_to_human_datetime)


_CLIENT_7SHIFTS = None
_DB_CONNECTION = None


def get_7shifts():
    global _CLIENT_7SHIFTS
    if _CLIENT_7SHIFTS is None:
        _CLIENT_7SHIFTS = lib7shifts.get_client()
    return _CLIENT_7SHIFTS


def get_db(url=None, db_debug=False):
    global _DB_CONNECTION
    if _DB_CONNECTION is None:
        _DB_CONNECTION = sqlalchemy.create_engine(
            url, echo=db_debug)
    return _DB_CONNECTION


def logger():
    """Returns a handle to a python logger with the name 'sync7shifts'
    """
    return logging.getLogger('lib7shifts.cli.7shifts.sync')


def parse_dates(args):
    """Given args, figure out the necessary date fields to supply to 7shifts
    API calls. If no end date was supplied, make it yesterday at 11:59pm. These
    are timezone-aware objects and assume local timezone, converting those
    timestamps to UTC prior to API requests.

    Returns a dict with named fields (start, end, modified_since)."""
    retval = {}
    if args.get('--modified-since'):
        retval['modified_since'] = args.get('--modified-since')
        retval['modified_end_ymd'] = to_y_m_d(yesterday())
        logger().info(
            "Using the following dates: modified_since:%s (up to %s)",
            retval['modified_since'], retval['modified_end_ymd'])
    else:
        eod = timedelta(hours=23, minutes=59, seconds=59)
        start_date = yesterday()
        if args.get("--start-date"):
            start_date = to_local_date(args.get('--start-date'))
        retval['start'] = datetime.fromtimestamp(
            start_date.timestamp(), timezone.utc)
        end_date = start_date + eod
        if args.get('--end-date'):
            end_date = to_local_date(args.get('--end-date')) + eod
        retval['end'] = datetime.fromtimestamp(
            end_date.timestamp(), timezone.utc)
        logger().info(
            "Using the following dates: start:%s, end:%s",
            datetime_to_human_datetime(retval['start']),
            datetime_to_human_datetime(retval['end']))
    return retval


def get_one_company_data(company_id):
    data = pandas.DataFrame.from_dict([
        lib7shifts.get_company(get_7shifts(), company_id), ])
    if len(data) > 0:
        data.set_index('id', drop=True, inplace=True)
    logger().debug("retrieved %d rows with %d columns for company id %d",
                   *data.shape, company_id)
    return data


def get_all_company_data():
    data = pandas.DataFrame.from_dict(
        lib7shifts.list_companies(get_7shifts()))
    if len(data) > 0:
        data.set_index('id', drop=True, inplace=True)
    logger().debug("retrieved %d companies with %d total fields", *data.shape)
    return data


def sync_company_data(company):
    with get_db().begin() as conn:
        clean = company.drop(columns=['meta', ])
        return clean.to_sql('companies', conn, if_exists='replace')


def get_location_data(company_id, date_args={}):
    kwargs = {}
    if 'modified_since' in date_args:
        kwargs['modified_since'] = date_args['modified_since']
    return pandas.DataFrame.from_dict(lib7shifts.list_locations(
        get_7shifts(), company_id, **kwargs))


def sync_location_data(company_id, date_args):
    data = get_location_data(company_id, date_args)
    if len(data) > 0:
        data.set_index('id', drop=True, inplace=True)
    logger().debug(
        "retrieved %d location records with %d fields for company %d",
        *data.shape, company_id)
    with get_db().begin() as conn:
        return data.to_sql('locations', conn, if_exists='replace')


def get_department_data(company_id, date_args):
    kwargs = {}
    if 'modified_since' in date_args:
        kwargs['modified_since'] = date_args['modified_since']
    return pandas.DataFrame.from_dict(lib7shifts.list_departments(
        get_7shifts(), company_id, **kwargs))


def sync_deparment_data(company_id, date_args):
    data = get_department_data(company_id, date_args)
    if len(data) > 0:
        data.set_index('id', drop=True, inplace=True)
    logger().debug(
        "retrieved %d department records with %d fields for company %d",
        *data.shape, company_id)
    with get_db().begin() as conn:
        return data.to_sql('departments', conn, if_exists='replace')


def get_role_data(company_id, date_args):
    kwargs = {}
    if 'modified_since' in date_args:
        kwargs['modified_since'] = date_args['modified_since']
    roles = []
    stations = []
    for role in lib7shifts.list_roles(
            get_7shifts(), company_id, **kwargs):
        if role.get('num_stations') > 0:
            stations.extend(role.pop('stations'))
        roles.append(role)
    return (
        pandas.DataFrame.from_dict(roles),
        pandas.DataFrame.from_dict(stations)
    )


def sync_role_data(company_id, date_args):
    roles, stations = get_role_data(company_id, date_args)
    if len(roles) > 0:
        roles.drop(columns=['stations', ], inplace=True)
        roles.set_index('id', drop=True, inplace=True)
    if len(stations) > 0:
        stations.set_index('id', drop=True, inplace=True)
    logger().debug(
        "retrieved %d roles with %d fields for company %d (%d stations)",
        *roles.shape, stations.shape[0], company_id)
    with get_db().begin() as conn:
        return (
            roles.to_sql('roles', conn, if_exists='replace'),
            stations.to_sql('stations', conn, if_exists='replace')
        )


def get_user_data(company_id, date_args, status):
    kwargs = {'status': status}
    if 'modified_since' in date_args:
        kwargs['modified_since'] = date_args['modified_since']
    return pandas.DataFrame.from_dict(lib7shifts.list_users(
        get_7shifts(), company_id, **kwargs))


def sync_user_data(company_id, date_args, status='active'):
    data = get_user_data(company_id, date_args, status)
    if len(data) > 0:
        data.set_index('id', drop=True, inplace=True)
    logger().debug(
        "retrieved %d user records with %d fields for company %d",
        *data.shape, company_id)
    with get_db().begin() as conn:
        return data.to_sql('users', conn, if_exists='replace')


def get_user_wage_data(company_id, user_id):
    data = lib7shifts.list_user_wages(get_7shifts(), company_id, user_id)
    wages = data[0]
    wages.extend(data[1])
    return pandas.DataFrame.from_dict(wages)


def sync_wage_data(company_id, date_args, status='active'):
    # wage data is sought on a per-user basis
    users = get_user_data(company_id, date_args, status)
    updated = 0
    with get_db().begin() as conn:
        for user in users.itertuples():
            wages = get_user_wage_data(company_id, user.id)
            if len(wages) > 0:
                wages.set_index('id', drop=True, inplace=True)
            logger().debug(
                "retrieved %d wage records for user %s %s (id: %d)",
                wages.shape[0], user.first_name, user.last_name, user.id)
            updated += wages.to_sql('wages', conn, if_exists='replace')
        return updated


def get_receipt_data(company_id, location_id, date_args):
    "Note: Does not return a data frame, so that results can be chunked"
    kwargs = {}
    if 'modified_since' in date_args:
        kwargs['modified_since'] = date_args['modified_since']
    else:
        kwargs['receipt_date[gte]'] = date_args['start']
        kwargs['receipt_date[lte]'] = date_args['end']
    kwargs['location_id'] = location_id
    return lib7shifts.list_receipts(get_7shifts(), company_id, **kwargs)


def _sync_receipt_chunk(connection, chunk):
    frame = pandas.DataFrame.from_dict(chunk)
    if len(frame) > 0:
        frame.drop(
            columns=['receipt_lines', 'tip_details'], inplace=True)
        frame.set_index('id', drop=True, inplace=True)
    logger().info('writing %d receipt records', len(frame))
    return frame.to_sql('receipts', connection, if_exists='replace')


def sync_receipt_data(company_id, date_args, chunk_size=1000):
    # location data is required for receipts
    locations = get_location_data(company_id)
    written = 0
    with get_db().begin() as conn:
        for location in locations.itertuples():
            logger().info('gathering receipt data for location: %s',
                          location.name)
            chunk = []
            data = get_receipt_data(company_id, location.id, date_args)
            while True:
                try:
                    chunk.append(next(data))
                except StopIteration:
                    written += _sync_receipt_chunk(conn, chunk)
                    break
                else:
                    if len(chunk) >= chunk_size:
                        written += _sync_receipt_chunk(conn, chunk)
                        del chunk[:]
    return written


def get_shift_data(company_id, date_args):
    kwargs = {}
    if 'modified_since' in date_args:
        kwargs['modified_since'] = date_args['modified_since']
    else:
        kwargs['start[gte]'] = date_args['start']
        kwargs['start[lte]'] = date_args['end']
    return pandas.DataFrame.from_dict(
        lib7shifts.list_shifts(get_7shifts(), company_id, **kwargs))


def sync_shift_data(company_id, dates):
    """Get the pandas data frame from 7shifts API data and sync it to the
    database.
    """
    data = get_shift_data(company_id, dates)
    if len(data) > 0:
        data.drop(columns=['breaks', ], inplace=True)
        data.set_index('id', drop=True, inplace=True)
    logger().info(
        "retrieved %d shifts with %d total fields for company %d",
        *data.shape, company_id)
    with get_db().begin() as conn:
        return data.to_sql(
            'shifts', conn, if_exists='replace', chunksize=500)


def get_punch_data(company_id, date_args, approved=None):
    kwargs = {}
    if 'modified_since' in date_args:
        kwargs['modified_since'] = date_args['modified_since']
    else:
        kwargs['clocked_in[gte]'] = date_args['start']
        kwargs['clocked_in[lte]'] = date_args['end']
    if approved is not None:
        kwargs['approved'] = approved
    return pandas.DataFrame.from_dict(
        lib7shifts.list_punches(get_7shifts(), company_id, **kwargs))


def sync_punch_data(company_id, dates, approved=True):
    """Get the pandas data frame from 7shifts API data and sync it to the
    database.
    """
    data = get_punch_data(company_id, dates, approved=approved)
    if len(data) > 0:
        data.set_index('id', drop=True, inplace=True)
    logger().info(
        "retrieved %d time punch rows with %d total fields for company %d",
        *data.shape, company_id)
    with get_db().begin() as conn:
        clean = data.drop(columns=['breaks', ])  # breaks can't insert directly
        return clean.to_sql(
            'time_punches', conn, if_exists='replace', chunksize=500)
    # TODO: Breaks


def get_daily_sales_and_labor_data(kwargs={}):
    return pandas.DataFrame.from_dict(
        lib7shifts.get_daily_sales_and_labor(
            get_7shifts(), **kwargs))


def sync_daily_sales_and_labor_data(company_id, dates):
    """Get the pandas data frame from 7shifts API data and sync it to the
    database.
    """
    kwargs = {}
    if 'start' in dates:
        kwargs['start_date'] = to_y_m_d(dates['start'])
        kwargs['end_date'] = to_y_m_d(dates['end'])
    else:
        kwargs['start_date'] = dates['modified_since']
        kwargs['end_date'] = dates['modified_end_ymd']

    # location data is required for daily sales and labour
    locations = get_location_data(company_id)
    written = 0
    with get_db().begin() as conn:
        for location in locations.itertuples():
            kwargs['location_id'] = location.id
            data = get_daily_sales_and_labor_data(kwargs)
            if len(data) > 0:
                data['location_id'] = location.id
                data.set_index(['location_id', 'date'],
                               drop=True, inplace=True)
            logger().info(
                "found %d sales + labour records for company %d, location %d",
                data.shape[0], company_id, location.id)
            written += data.to_sql(
                'daily_sales_and_labor', conn, if_exists='replace')
    return written


def main(**args):
    get_db(args.get('--db'), args.get('--debug-db'))
    dates = parse_dates(args)
    companies = None
    if args.get('--company-id'):
        companies = get_one_company_data(args.get('--company-id'))
    else:
        companies = get_all_company_data()
    if args.get('all') or args.get('companies'):
        logger().info("Synced %d companies", sync_company_data(companies))
    for company in companies.itertuples():
        if args.get('all') or args.get('locations'):
            logger().info("Synced %d locations",
                          sync_location_data(company.Index, dates))
        if args.get('all') or args.get('deparments'):
            logger().info("Synced %d departments",
                          sync_deparment_data(company.Index, dates))
        if args.get('all') or args.get('roles'):
            logger().info("Synced %d roles with %d stations",
                          *sync_role_data(company.Index, dates))
        if args.get('all') or args.get('users'):
            logger().info("Synced %d active users",
                          sync_user_data(company.Index, dates, 'active'))
            if args.get("--inactive-users"):
                logger().info("Synced %d inactive users",
                              sync_user_data(company.Index, dates, 'inactive'))
        if args.get('all') or args.get('wages'):
            logger().info("Synced %d wages for active users",
                          sync_wage_data(company.Index, dates, 'active'))
            if args.get("--inactive-users"):
                logger().info("Synced %d wages for inactive users",
                              sync_wage_data(company.Index, dates, 'inactive'))
        if args.get('all') or args.get('receipts'):
            logger().info("Synced %d receipts",
                          sync_receipt_data(company.Index, dates))
        if args.get('all') or args.get('shifts'):
            logger().info("Synced %d shifts",
                          sync_shift_data(company.Index, dates))
        if args.get('all') or args.get('punches'):
            logger().info("Synced %d approved time punches",
                          sync_punch_data(
                              company.Index, dates, approved=True))
            if args.get('--unapproved'):
                logger().info("Synced %d non-approved time punches",
                              sync_punch_data(
                                  company.Index, dates, approved=False))
        if args.get('all') or args.get('daily_sales_and_labor'):
            logger().info("Synced %d daily sales and labour records",
                          sync_daily_sales_and_labor_data(
                              company.Index, dates))
    return 0
