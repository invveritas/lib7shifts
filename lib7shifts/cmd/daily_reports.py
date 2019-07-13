"""usage:
  7shifts daily_reports list --loc=ID --from=D --to=D [options]
  7shifts daily_reports db sync --loc=ID --from=D --to=D [options] <sqlite_db>
  7shifts daily_reports db init [options] [--] <sqlite_db>

Options:
  -h --help         show this screen
  -v --version      show version information
  --dry-run         does not commit data to database, but goes through inserts
  -d --debug        enable debug logging (low-level)
  --from=D          the starting date to pull data for
  --to=D            the last date to pull data for
  --loc=ID          a numeric id for the location in question
  --unapproved      include unapproved labour in report

Dates should be in YYYY-MM-DD format, in the local timezone.

You must provide the 7shifts API key with an environment variable called
API_KEY_7SHIFTS.

"""
import lib7shifts
from .common import (
    get_7shifts_client, print_api_item, Sync7Shifts2Sqlite)


class SyncDailyReports2Sqlite(Sync7Shifts2Sqlite):
    """Extend :class:`Sync7Shifts2Sqlite` to work for 7shifts Daily Reports."""

    table_name = 'daily_sales_and_labor'
    table_schema = """CREATE TABLE IF NOT EXISTS {table_name} (
            date UNIQUE,
            location_id NOT NULL,
            labor_target_percentage,
            labor_hours_scheduled,
            labor_cost_scheduled,
            labor_hours_worked,
            labor_actual,
            projected,
            actual,
        PRIMARY KEY (date, location_id)
        ) WITHOUT ROWID
        """
    insert_query = """INSERT OR REPLACE INTO {table_name}
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    insert_fields = (
        'date', 'location_id', 'labor_target_percentage',
        'labor_hours_scheduled', 'labor_cost_scheduled',
        'labor_hours_worked', 'labor_actual', 'projected', 'actual')


def build_args(args):
    """Build a list of arguments to provide to
    :func:`lib7shifts.get_sales_and_labour` based on user args."""
    list_args = {}
    if args.get('--unapproved'):
        list_args['include_unapproved'] = True
    if args.get('--loc'):
        list_args['location_id'] = args.get('--loc')
    if args.get('--from'):
        list_args['from'] = args.get('--from')
    if args.get('--to'):
        list_args['to'] = args.get('--to')
    return list_args


def get_sales_and_labor(args):
    "Return sales and labour data from the 7shifts API (raw dict form)"
    client = get_7shifts_client()
    return lib7shifts.get_sales_and_labor(
        client,
        **build_args(args))


def main(**args):
    """Run the cli-specified action (list, sync, init_schema)"""
    if args.get('list', False):
        data = get_sales_and_labor(args)
        print_api_item(data['daily'])
        print(
            'Total Labour: ${:0.2f} ({:0.2f} percent of sales)'.format(
                data['weekly'], data['labor_percentage'] * 100
            ))
    elif args.get('db', False):
        sync_db = SyncDailyReports2Sqlite(
            args.get('<sqlite_db>'),
            dry_run=args.get('--dry-run'))
        if args.get('sync', False):
            sync_db.sync_to_database(get_sales_and_labor(args)['daily'])
        elif args.get('init_schema', False):
            sync_db.init_db_schema()
        else:
            raise RuntimeError("no valid db action specified")
    else:
        raise RuntimeError("no valid action in args")
    return 0
