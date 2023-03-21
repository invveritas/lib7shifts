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
        return TimePunch(**response['data'])
    except KeyError:
        raise exceptions.EntityNotFoundError('Time Punch', punch_id)


def list_punches(client, company_id, **kwargs):
    """Implements the 'List' method for Time Punches as outlined in the API,
    and returns a TimePunchList object representing all the punches. Provide a
    'client' parameter with an active :class:`lib7shifts.APIClient`
    object.

    Supports the same optional kwargs as the API arguments, such as:

    - location_id
    - department_id
    - role_id
    - user_id
    - approved: boolean
    - modified_since: return punches modified since the specified date
    - clocked_in[gte]: datetime object used to filter punches based on clock-in
                        time. Return punches with clock-in on/after this date
    - clocked_in[lte] as above, but for clock-in before/on this datetime
    - clocked_out[gte] datetime object used to filter punches based on
                        clock-out time. Return punches with clock-out on/after
                        this date
    - clocked_out[lte] as above, but with clock-out before/on this date
    - localize_search_time If true, convert any date ranges to consider the
      local timezone of the punches. Only applies to modified_since in this
      method because all clocked_in/clocked_out dates are supplied to the API
      as full date-time values with timezone offsets.
    - sort_by: name of the field and direction to sort by, ie. user_id.asc

    Note that datetime objects may be passed in for the clocked_in/clocked_out
    parameters, as well as modified_since.

    See https://developers.7shifts.com/reference/gettimepunches for
    details.
    """
    if 'limit' not in kwargs:
        kwargs['limit'] = 500
    if kwargs.get('clocked_in[gte]'):
        # cast to iso8601 because the endpoint supports full date-time
        kwargs['clocked_in[gte]'] = dates.iso8601_dt(
            kwargs.get('clocked_in[gte]'))
    if kwargs.get('clocked_in[lte]'):
        # cast to iso8601 because the endpoint supports full date-time
        kwargs['clocked_in[lte]'] = dates.iso8601_dt(
            kwargs.get('clocked_in[lte]'))
    if kwargs.get('clocked_out[gte]'):
        # cast to iso8601 because the endpoint supports full date-time
        kwargs['clocked_out[gte]'] = dates.iso8601_dt(
            kwargs.get('clocked_out[gte]'))
    if kwargs.get('clocked_out[lte]'):
        # cast to iso8601 because the endpoint supports full date-time
        kwargs['clocked_out[lte]'] = dates.iso8601_dt(
            kwargs.get('clocked_out[lte]'))
    for item in base.page_api_get_results(
            client, ENDPOINT.format(company_id=company_id),
            **kwargs):
        yield TimePunch(**item)


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

    def __init__(self, **kwargs):
        super(TimePunch, self).__init__(**kwargs)
        self._breaks = None
        self._user = None
        self._role = None
        self._location = None
        self._department = None
        self._shift = None

    def get_shift(self, client):
        """Return a :class:`lib7shifts.shifts.Shift`
        object corresponding to the shift that the punch was associated with.
        An API fetch will be used if this object wasn't initially seeded with
        shift data from a :func:`read` operation.
        """
        if self._shift is None:
            from . import shifts
            self._shift = shifts.get_shift(
                client, self.company_id, self.shift_id)
        return self._shift

    def get_user(self, client):
        """Return a :class:`lib7shfits.users.User` class for the user.
        An API fetch will be used if this object wasn't initially seeded with
        user data from a :func:`read` operation."""
        if self._user is None:
            from . import users
            self._user = users.get_user(
                client, self.company_id, self.user_id)
        return self._user

    def get_role(self, client):
        """Return a :class:`lib7shifts.roles.Role` object for the role
        specified by the punch.
        An API fetch will be used to fulfill this call."""
        if self._role is None:
            from . import roles
            self._role = roles.get_role(
                client, self.company_id, self.role_id)
        return self._role

    def get_location(self, client):
        """Returns a :class:`lib7shifts.locations.Location` object
        corresponding to the location of the punch.
        An API fetch will be used if this object wasn't initially seeded with
        location data from a :func:`read` operation."""
        if self._location is None:
            from . import locations
            self._location = locations.get_location(
                client, self.company, self.location_id)
        return self._location

    def get_department(self, client):
        """Returns a :class:`lib7shifts.departments.Department` object
        corresponding to the punch.
        An API fetch will be used if this object wasn't initially seeded with
        department data from a :func:`read` operation."""
        if self._department is None:
            from . import departments
            self._department = departments.get_department(
                client, self.company, self.department_id)
        return self._department

    @property
    def clocked_in(self):
        "Returns a :class:`datetime.datetime` object for the punch-in time"
        return dates.to_datetime(self.get('clocked_in'))

    @property
    def clocked_out(self):
        "Returns a :class:`datetime.datetime` object for the punch-out time"
        if self._api_data()['clocked_out'] \
                == '0000-00-00 00:00:00':
            # currently logged in shift, return now
            return dates.DateTime7Shifts.now()
        return dates.to_datetime(self.get('clocked_out'))

    @property
    def created(self):
        "Returns a :class:`datetime.datetime` object for punch creation time"
        return dates.to_datetime(self.get('created'))

    @property
    def modified(self):
        """Returns a :class:`datetime.datetime` object corresponding to the
        last time this punch was modified"""
        return dates.to_datetime(self.get('modified'))

    @property
    def breaks(self):
        """Returns a TimePunchBreakList object with all breaks
        for this punch"""
        if self._breaks is None:
            self._breaks = TimePunchBreakList.from_api_data(
                self.get('breaks'))
        return self._breaks


class TimePunchBreak(base.APIObject):
    "Represent a Time Punch Break"

    def __init__(self, **kwargs):
        super(TimePunchBreak, self).__init__(**kwargs)
        self._user = None

    @property
    def in_time(self):
        """Returns a :class:`datetime.datetime` object corresponding to the
        time the break started"""
        return dates.to_datetime(self.get('in'))

    @property
    def out_time(self):
        """Returns a :class:`datetime.datetime` object corresponding to the
        time the break ended"""
        return dates.to_datetime(self.get('out'))

    @property
    def paid(self):
        """Returns True if 7shifts thinks this is a paid break"""
        return self.get('paid')

    def get_user(self, client):
        """Perform an API fetch and return a :class:`lib7shfits.users.User`
        class for the user"""
        if self._user is None:
            from . import users
            self._user = users.get_user(client, self.user_id)
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
    def from_api_data(cls, data):
        """Provide this method with the break data returned directly from
        the API in raw format.
        """
        obj_list = []
        for item in data:
            obj_list.append(TimePunchBreak(**item))
        return cls(obj_list)
