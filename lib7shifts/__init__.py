"""
Base module for 7shifts API support. This module imports all of the user-facing
classes and functions from the other modules in lib7shifts, so you only need to
import this module to use the full suite, eg::

    from lib7shifts import get_client, list_punches
    client = get_client(api_key='YOURAPIKEYHERE')
    punches = list_punches(client, **{'clocked_in[gte]': '2019-06-07'})
    for punch in punches:
        print(punch)

"""
import logging
import certifi
import urllib3
import datetime
import json
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from . import exceptions
from . import dates

from .events import (create_event, get_event, update_event, delete_event,
                     list_events, Event, EventList)
from .departments import (get_department, list_departments,
                          Department, DepartmentList)
from .roles import (get_role, list_roles, Role, RoleList)
from .users import (get_user, list_users, User)
from .companies import (get_company, list_companies, Company)
from .shifts import (get_shift, list_shifts, Shift, ShiftList)
from .locations import (get_location, list_locations, Location, LocationList)
from .time_punches import (get_punch, list_punches, TimePunch, TimePunchList,
                           TimePunchBreak, TimePunchBreakList)

def get_client(api_key, **kwargs):
    "Returns an :class:`APIClient7Shifts`"
    return APIClient7Shifts(api_key=api_key, **kwargs)

class APIClient7Shifts(object):
    """
    7shifts API v1 client.

    Natively uses urllib3 connection pooling and includes support for rate
    limiting with a RateLimiter from the `apiclient` module. This code was
    originally based on the `apiclient` library, but has diverged substantially
    enough to be something all its own. Still, thanks to Andrey Petrov for the
    original design and inspiration.
    """

    BASE_URL = 'https://api.7shifts.com/v1'
    ENCODING = 'utf8'
    KEEP_ALIVE = True
    USER_AGENT = 'py-lib7shifts'

    def __init__(self, **kwargs):
        """
        Supported kwargs:

        - api_key: the api key to use for requests (required)
        - rate_limit_lock - from apiclient.ratelimiter module
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.api_key = kwargs.pop('api_key')
        self.rate_limit_lock = kwargs.pop('rate_limit_lock', None)
        self.__connection_pool = None

    def read(self, endpoint, item_id, **urlopen_kw):
        """Perform Reads against 7shifts API for the specified endpoint/ID.
        Pass parameters using the `fields` kwarg."""
        return self._request(
            'GET', "{}/{:d}".format(endpoint, item_id), **urlopen_kw)

    def create(self, endpoint, **urlopen_kw):
        """Performs Create operations in the 7shifts API
        IMPORTANT: Pass POST data using the ``body`` kwarg, unencoded. The
        data will be JSON encoded before posting.
        """
        body = json.dumps(urlopen_kw.pop('body', dict()))
        return self._request(
            'POST', endpoint, body=body, **urlopen_kw)

    def update(self, endpoint, item_id, **urlopen_kw):
        """Perform Update operations for the given endpoint/item_id
        IMPORTANT: Pass PUT data using the ``body`` kwarg, unencoded. The
        data will be JSON encoded before posting.
        """
        body = json.dumps(urlopen_kw.pop('body', dict()))
        return self._request(
            'PUT', "{}/{:d}".format(endpoint, item_id), body=body, **urlopen_kw)

    def delete(self, endpoint, item_id, **urlopen_kw):
        "Delete the item at the given endpoint with the given ID"
        return self._request(
            'DELETE', "{}/{:d}".format(endpoint, item_id), **urlopen_kw)

    def list(self, endpoint, **urlopen_kw):
        """Implements the List method for 7shifts API objects.
        Pass a list of parameters using the `fields` kwarg."""
        fields = {}
        for key, val in urlopen_kw.get('fields', {}).items():
            #print('item: {}'.format(key))
            if isinstance(val, bool):
                if val:
                    fields[key] = 1
                else:
                    fields[key] = 0
            elif isinstance(val, datetime.datetime):
                fields[key] = dates.from_datetime(val)
            else:
                fields[key] = val
        urlopen_kw['fields'] = fields
        return self._request(
            'GET', endpoint, **urlopen_kw)

    @property
    def _connection_pool(self):
        """
        Returns an initialized connection pool. If the pool becomes broken
        in some way, it can be destroyed with :meth:`_destroy_pool` and a
        subsequent call to this attribute will initialize a new pool.
        """
        if self.__connection_pool is None:
            self._create_pool()
        return self.__connection_pool

    def _request(self, method, path, **urlopen_kw):
        """
        Wrapper around the ConnectionPool request method to add rate limiting
        and response handling.

        HTTP GET parameters should be passed as 'fields', and will be properly
        encoded by urllib3 and correctly placed into the request uri. For
        POST and PUT operations, the ``body`` kwarg should be supplied and
        already in encoded form (that's generally done by one of the methods
        above.)

        Any headers passed as kwargs will be merged with underlying ones that
        are required to make the API function properly, with the headers
        passed here overriding built-ins (such as to override the user_agent
        for a particular request).
        """
        try:
            self.rate_limit_lock.acquire()
        except AttributeError:
            pass
        response = self._connection_pool.request(
            method.upper(), path, **urlopen_kw)
        return self._handle_response(response)

    def _destroy_pool(self):
        """
        Tear down the existing HTTP(S)ConnectionPool such that a subsequent
        call to :attr:`_connection_pool` generates a new pool to work with.
        Useful in cases where authentication timeouts occur.
        """
        # TODO: locking around this kind of thing for thread safety
        self.__connection_pool = None

    def _create_pool(self):
        """Use the handy urllib3 connection_from_url helper to create a
        pool of the correct type for HTTP/HTTPS.
        This also seeds the pool with the base URL so that subsequent requests
        only use the URI portion rather than an absolute URL.

        Stores a reference to the pool for use with :attr:`_connection_pool`
        """
        headers = urllib3.util.make_headers(
            keep_alive=self.KEEP_ALIVE,
            user_agent=self.USER_AGENT,
            basic_auth='{}:'.format(self.api_key))
        # TODO: locking around this kind of thing for thread safety
        self.__connection_pool = urllib3.connectionpool.connection_from_url(
            self.BASE_URL, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(),
            headers=headers)

    def _handle_response(self, response):
        """
        In the case of a normal response, deserializes the response from
        JSON back into dictionary form and returns it. In case of a response
        code of 300 or higher, raises an :class:`exceptions.APIError` exception.
        Note that if you are seeing weirdness in the API response data, look
        at the :attr:`ENCODING` attribute for this class.
        """
        if response.status > 299:
            raise exceptions.APIError(response.status, response=response)
        return json.loads(response.data.decode(self.ENCODING))
