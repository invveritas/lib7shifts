"""
API methods and objects related to 7Shifts Shifts.

See https://www.7shifts.com/partner-api#toc-shifts for details about supported
operations.
"""
from . import base
from . import dates
from . import exceptions

ENDPOINT = '/v2/company/{company_id}/shifts'


def get_shift(client, company_id, shift_id):
    """Implements the 'Read' method from the 7shifts API for shifts.
    Returns a :class:`Shift` object."""
    response = client.read(ENDPOINT.format(company_id=company_id), shift_id)
    try:
        return Shift(company_id, **response['data'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Shift', shift_id)


def list_shifts(client, company_id, **kwargs):
    """Implements the 'List' operation for 7shifts Shifts, returning the
    shifts associated with the company you've authenticated with based on your
    filter parameters.

    Pass in an active :class:`lib7shifts.APIClient7Shifts` object and any of
    the following parameters supported by the API:

    - location_id: only get shifts for this location
    - start[gte]: datetime or string time format (greater than/equal to)
    - start[lte]: as above, but less than/equal to
    - start[date]: a simple Y-m-d date string that shifts have to start
        on/after
    - department_id
    - user_id
    - deleted: whether or not to include deleted shifts in the results
    - draft: whether or not to include un-published shifts in the results
    - open: whether or not to ONLY retrieve shifts that are "open"
    - limit: limit the number of results to be returned
    - offset: return results starting from an offset
    - order_field: the field to order results by, eg:
        order_field=shift.modified
    - order_dir: "asc" or "desc"

    Returns a :class:`ShiftList` object containing :class:`Shift` objects.
    """
    return ShiftList.from_api_data(
        company_id,
        base.page_api_get_results(
            client, ENDPOINT.format(company_id=company_id),
            **kwargs, limit=200),
        client=client)


class Shift(base.APIObject):
    """
    Represents a 7shifts Shift object, with all the same attributes as the
    Shift object defined in the API documentation.
    """

    def __init__(self, company_id, **kwargs):
        super(Shift, self).__init__(**kwargs)
        self.company_id = company_id
        self._user = None
        self._role = None
        self._location = None
        self._department = None

    @property
    def start(self):
        "Returns a :class:`datetime.datetime` object for the start time"
        # for some reason, shifts are returned in the local timezone
        # in the API (perhapse the timezone of the location)
        return dates.to_datetime(
            self._api_data('start'), dates.get_local_tz())

    @property
    def end(self):
        "Returns a :class:`datetime.datetime` object for the end time"
        # for some reason, shifts are returned in the local timezone
        # in the API (perhapse the timezone of the location)
        return dates.to_datetime(
            self._api_data('end'), dates.get_local_tz())

    def was_sick(self):
        "Returns True if the shift has a Sick status flag"
        if self.attendance_status == "sick":
            return True
        return False

    def was_no_show(self):
        "Returns True if the shift has a No-show status flag"
        if self.attendance_status == "no-show":
            return True
        return False

    def was_late(self):
        "Returns True if the shift has a Late status flag"
        if self.attendance_status == "late":
            return True
        return False

    def get_user(self):
        """Return a :class:`lib7shfits.users.User` class for the user
        associated with this shift.
        An API fetch will be used to fetch this data (once)"""
        if self._user is None:
            from . import users
            self._user = users.get_user(self.user_id, client=self.client)
        return self._user

    def get_role(self):
        """Return a :class:`lib7shifts.roles.Role` object for the role
        specified by the shift.
        An API fetch will be used to fulfill this call."""
        if self._role is None:
            from . import roles
            self._role = roles.get_role(self.role_id, client=self.client)
        return self._role

    def get_location(self):
        """Returns a :class:`lib7shifts.locations.Location` object
        corresponding to the location of the shift.
        An API fetch will be used to fetch this data (once)"""
        if self._location is None:
            from . import locations
            self._location = locations.get_location(
                self.location_id, client=self.client)
        return self._location

    def get_department(self):
        """Returns a :class:`lib7shifts.departments.Department` object
        corresponding to the shift.
        An API fetch will be used to fetch this data (once)"""
        if self._department is None:
            from . import departments
            self._department = departments.get_department(
                self.department_id, client=self.client)
        return self._department


class ShiftList(list):
    """
    An interable list of :class:`Shift` objects.
    """

    @classmethod
    def from_api_data(cls, company_id, data, client=None):
        """Provide this method with the shift data returned directly from
        the API in raw format.
        """
        obj_list = []
        for item in data:
            obj_list.append(Shift(company_id, **item, client=client))
        return cls(obj_list)
