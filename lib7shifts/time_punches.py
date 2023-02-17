"""
This library is used for all time-punch related code and objects.
"""
from . import base
from . import dates
from . import exceptions

ENDPOINT = '/v2/company/{company_id}/time_punches'


def get_punch(client, company_id, punch_id):
    """Implements the 'Read' operation from the 7shifts API. Supply a punch ID.
    Returns a :class:`TimePunch` object.
    """
    response = client.read(ENDPOINT.format(company_id=company_id), punch_id)
    try:
        punch_id = response['data']['time_punch']
        return TimePunch(**response['data'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Time Punch', punch_id)


def list_punches(client, company_id, **kwargs):
    """Implements the 'List' method for Time Punches as outlined in the API,
    and returns a TimePunchList object representing all the punches. Provide a
    'client' parameter with an active :class:`lib7shifts.APIClient`
    object.

    Supports the same kwargs as the API arguments, such as:

    - clocked_in[gte] (datetime format optional)
    - clocked_in[lte] (datetime format optional)
    - clocked_out[gte] (datetime format optional)
    - clocked_out[lte] (datetime format optional)
    - location_id
    - department_id
    - limit
    - offset
    - order_field
    - order_dir

    See https://www.7shifts.com/partner-api#crud-toc-time-punches-list for
    details.
    """
    return TimePunchList.from_api_data(
        company_id,
        base.page_api_get_results(
            client, ENDPOINT.format(company_id=company_id),
            **kwargs, limit=200),
        client=client)


class TimePunch(base.APIObject):
    """
    An object representing a time punch, including break data. Requires the
    `time_punch` parameter to be useful, but can also be seeded with:

    - time_punch_break
    - location
    - department
    - shift
    - user

    All of the above come in directly from an API 'Read' call, and thus are
    directly present whenever a :class:`TimePunch` is instantiated from a call
    to :func:`api_read`. However, :class:`TimePunch` has several fetch methods
    that will fall back to the API whenever details about the above are not
    present, and will return appropriate objects, which are cached internally,
    so subsequent calls to retrieve the same location will not keep hitting
    the 7shifts API.
    """

    def __init__(self, company_id, **kwargs):
        super(TimePunch, self).__init__(**kwargs)
        self.company_id = company_id
        self._breaks = None
        self._user = None
        self._role = None
        self._location = None
        self._department = None
        self._shift = None

    def get_shift(self):
        """Return a :class:`lib7shifts.shifts.Shift`
        object corresponding to the shift that the punch was associated with.
        An API fetch will be used if this object wasn't initially seeded with
        shift data from a :func:`read` operation.
        """
        if self._shift is None:
            from . import shifts
            self._shift = shifts.get_shift(
                self.client, self.company_id, self.shift_id)
        return self._shift

    def get_user(self):
        """Return a :class:`lib7shfits.users.User` class for the user.
        An API fetch will be used if this object wasn't initially seeded with
        user data from a :func:`read` operation."""
        if self._user is None:
            from . import users
            self._user = users.get_user(
                self.client, self.company_id, self.user_id)
        return self._user

    def get_role(self):
        """Return a :class:`lib7shifts.roles.Role` object for the role
        specified by the punch.
        An API fetch will be used to fulfill this call."""
        if self._role is None:
            from . import roles
            self._role = roles.get_role(
                self.client, self.company_id, self.role_id)
        return self._role

    def get_location(self):
        """Returns a :class:`lib7shifts.locations.Location` object
        corresponding to the location of the punch.
        An API fetch will be used if this object wasn't initially seeded with
        location data from a :func:`read` operation."""
        if self._location is None:
            from . import locations
            self._location = locations.get_location(
                self.client, self.company, self.location_id)
        return self._location

    def get_department(self):
        """Returns a :class:`lib7shifts.departments.Department` object
        corresponding to the punch.
        An API fetch will be used if this object wasn't initially seeded with
        department data from a :func:`read` operation."""
        if self._department is None:
            from . import departments
            self._department = departments.get_department(
                self.client, self.company, self.department_id)
        return self._department

    @property
    def clocked_in(self):
        "Returns a :class:`datetime.datetime` object for the punch-in time"
        return dates.to_datetime(self._api_data('clocked_in'))

    @property
    def clocked_out(self):
        "Returns a :class:`datetime.datetime` object for the punch-out time"
        if self._api_data()['clocked_out'] \
                == '0000-00-00 00:00:00':
            # currently logged in shift, return now
            return dates.DateTime7Shifts.now()
        return dates.to_datetime(self._api_data('clocked_out'))

    @property
    def created(self):
        "Returns a :class:`datetime.datetime` object for punch creation time"
        return dates.to_datetime(self._api_data('created'))

    @property
    def modified(self):
        """Returns a :class:`datetime.datetime` object corresponding to the
        last time this punch was modified"""
        return dates.to_datetime(self._api_data('modified'))

    @property
    def breaks(self):
        """Returns a TimePunchBreakList object with all breaks
        for this punch"""
        if self._breaks is None:
            self._breaks = TimePunchBreakList.from_api_data(
                self._api_data('breaks'))
        return self._breaks


class TimePunchList(list):
    """
    Object representing a list of TimePunch objects, including vivifying
    them from API response data.
    """

    @classmethod
    def from_api_data(cls, company_id, data, client=None):
        """Provide this method with the punch data returned directly from
        the API in raw format.
        """
        obj_list = []
        for item in data:
            obj_list.append(TimePunch(company_id, **item, client=client))
        return cls(obj_list)


class TimePunchBreak(base.APIObject):
    "Represent a Time Punch Break"

    def __init__(self, company_id, **kwargs):
        super(TimePunchBreak, self).__init__(**kwargs)
        self.company_id = company_id
        self._user = None

    @property
    def in_time(self):
        """Returns a :class:`datetime.datetime` object corresponding to the
        time the break started"""
        return dates.to_datetime(self._api_data('in'))

    @property
    def out_time(self):
        """Returns a :class:`datetime.datetime` object corresponding to the
        time the break ended"""
        return dates.to_datetime(self._api_data('out'))

    @property
    def paid(self):
        """Returns True if 7shifts thinks this is a paid break"""
        return self._api_data('paid')

    def get_user(self):
        """Perform an API fetch and return a :class:`lib7shfits.users.User`
        class for the user"""
        if self._user is None:
            from . import users
            self._user = users.get_user(self.client, self.user_id)
        return self._user

    @property
    def created(self):
        raise NotImplementedError

    @property
    def modified(self):
        raise NotImplementedError


class TimePunchBreakList(list):
    """
    An interable list of TimePunchBreak objects.
    """

    @classmethod
    def from_api_data(cls, company_id, data, client=None):
        """Provide this method with the break data returned directly from
        the API in raw format.
        """
        obj_list = []
        for item in data:
            obj_list.append(TimePunchBreak(company_id, **item, client=client))
        return cls(obj_list)
