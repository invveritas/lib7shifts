"""usage:
  7shifts whoami [options]

  -h --help         show this screen
  -v --version      show version information
  -d --debug        enable debug logging (low-level)

You must provide a 7shifts access token with an environment variable called
ACCESS_TOKEN_7SHIFTS.

"""
import lib7shifts
from .common import get_7shifts_client, print_api_item


def main(**args):
    """Run the cli-specified action (list, sync, init)"""
    client = get_7shifts_client()
    print_api_item(lib7shifts.get_whoami(client))
    return 0
