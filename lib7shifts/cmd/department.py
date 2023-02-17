"""usage:
  7shifts department list <company_id> [options]
  7shifts department db sync <company_id> [options] [--] <sqlite_db>
  7shifts department db init [options] [--] <sqlite_db>

  -h --help         show this screen
  -v --version      show version information
  --dry-run         does not commit data to database, but goes through inserts
  -d --debug        enable debug logging (low-level)

You must provide the 7shifts API key with an environment variable called
ACCESS_TOKEN_7SHIFTS.

"""
import lib7shifts
from .common import get_7shifts_client, print_api_data, Sync7Shifts2Sqlite


class SyncDepartments2Sqlite(Sync7Shifts2Sqlite):
    """Extend :class:`Sync7Shifts2Sqlite` to work for 7shifts departments."""

    table_name = 'departments'
    table_schema = """CREATE TABLE IF NOT EXISTS {table_name} (
            id PRIMARY KEY UNIQUE,
            name NOT NULL,
            location_id,
            created,
            modified
        ) WITHOUT ROWID
        """
    insert_query = """INSERT OR REPLACE INTO {table_name}
        VALUES(?, ?, ?, ?, ?)"""
    insert_fields = ('id', 'name', 'location_id', 'created', 'modified')


def get_departments(company):
    "Return a list of :class:`lib7shifts.company.Company` objects from the API"
    client = get_7shifts_client()
    return lib7shifts.list_departments(client, company)


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    if args.get('list', False):
        print_api_data(get_departments(args.get('<company_id>')))
    elif args.get('db', False):
        sync_db = SyncDepartments2Sqlite(
            args.get('<sqlite_db>'),
            dry_run=args.get('--dry-run'))
        if args.get('sync', False):
            sync_db.sync_to_database(get_departments(args.get('<company_id>')))
        elif args.get('init', False):
            sync_db.init_db_schema()
        else:
            raise RuntimeError("no valid db action specified")
    else:
        raise RuntimeError("no valid action in args")
    return 0
