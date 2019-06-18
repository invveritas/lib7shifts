import apiclient
import urllib3
import json
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from . import exceptions

__version__ = "0.1"

def get_client(api_key, *args, **kwargs):
    "Returns an :class:`APIClient`"
    return APIClient(api_key, *args, **kwargs)

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

class APIClient(apiclient.APIClient):
    """
    Extension of the APIClient class from apiclient, specific to 7shifts.
    """

    BASE_URL = 'https://api.7shifts.com/v1'

    def __init__(self, api_key, *args, **kwargs):
        super(APIClient, self).__init__(*args, **kwargs)
        self.api_key = api_key
        self.auth_headers = urllib3.util.make_headers(
            basic_auth='{}:'.format(self.api_key))
        self._user_cache = {}
        self._role_cache = {}

    def _request(self, method, path, headers=None, params=None):
        try:
            headers = merge_two_dicts(headers, self.auth_headers)
        except (TypeError, AttributeError):
            headers = self.auth_headers

        url = self._compose_url(path, params)

        self.rate_limit_lock and self.rate_limit_lock.acquire()
        r = self.connection_pool.urlopen(method.upper(), url, headers=headers)

        return self._handle_response(r)

    def _compose_url(self, path, params=None):
        return self.BASE_URL + path + '?' + urlencode(params)

    def _handle_response(self, response):
        if response.status > 299:
            raise exceptions.APIError(response.status, response=response)
        return super(APIClient, self)._handle_response(response)
