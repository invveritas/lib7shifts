"""
API methods and objects related to 7Shifts Shifts.

See https://developers.7shifts.com/reference/listshift for details about
supported operations.
"""
from . import base
from . import dates
from . import exceptions

ENDPOINT = '/v2/company/{company_id}/shifts'


def get_shift(client, company_id, shift_id, **params):
    """Implements the 'Read' method from the 7shifts API for shifts.
    Returns a :class:`Shift` object. Pass the following optional parameters:

    - include_deleted: return a shift even if deleted (True or False)
    """
    response = client.read(
        ENDPOINT.format(company_id=company_id), shift_id, fields=params)
    try:
        return Shift(**response['data'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Shift', shift_id)


def list_shifts(client, company_id, **kwargs):
    """Implements the 'List' operation for 7shifts Shifts, returning the
    shifts associated with the company you've authenticated with based on your
    filter parameters.

    Pass in an active :class:`lib7shifts.APIClient7Shifts` object and any of
    the following parameters supported by the API:

    - location_id: only get shifts for this location
    - shift_ids: a comma-separated list of shift IDs
    - department_id: a specific department to search for
    - department_ids: a list of department IDs to search for
    - role_id: shifts for a specific role
    - user_id: shifts for a specific user
    - start[gte]: a datetime-like object specifying a time to filter shifts
                    based on their start time (on/after this datetime)
    - start[lte]: as above, but return shifts that start on/before the date
    - end[lte]: a datetime-like object that filters shifts based on their end
                    times (on/before this datetime)
    - end[gte]: as above, but return shifts on/after this datetime
    - deleted: boolean, whether to include deleted shifts in the results
    - draft: boolean, include ONLY un-published shifts in the results.
                        Overrides the deleted flag.
    - include_draft: whether to include un-published shifts in results
    - open: return ONLY shifts that are "open" (not assigned to a user)
    - modified_since: a YYYY-MM-DD string, shifts modified on or after date
    - sort_by: either 'start' or 'end' shift time
    - sort_dir: either 'asc' or 'desc' for ascending/decending

    All date-time start/end arguments will be cast to an iso8601 format
    supported by the 7shifts API. If the supplied datetime is unaware of
    timezones, then the local timezone will be used. Unfortunately the
    `modified_since` paramter can only be cast to YYYY-MM-DD format based on
    API limitations.

    Returns a :class:`ShiftList` object containing :class:`Shift` objects.
    """
    if 'limit' not in kwargs:
        kwargs['limit'] = 500
    if kwargs.get('start[lte]'):
        # cast to iso8601 because the endpoint supports full date-time
        kwargs['start[lte]'] = dates.iso8601_dt(
            kwargs.get('start[lte]'))
    if kwargs.get('start[gte]'):
        # cast to iso8601 because the endpoint supports full date-time
        kwargs['start[gte]'] = dates.iso8601_dt(
            kwargs.get('start[gte]'))
    if kwargs.get('end[lte]'):
        # cast to iso8601 because the endpoint supports full date-time
        kwargs['end[lte]'] = dates.iso8601_dt(
            kwargs.get('end[lte]'))
    if kwargs.get('end[gte]'):
        # cast to iso8601 because the endpoint supports full date-time
        kwargs['end[gte]'] = dates.iso8601_dt(
            kwargs.get('end[gte]'))
    for item in base.page_api_get_results(
            client, ENDPOINT.format(company_id=company_id),
            **kwargs):
        yield Shift(**item)


class Shift(base.APIObject):
    """
    Represents a 7shifts Shift object, with all the same attributes as the
    Shift object defined in the API documentation.
    """

    def __init__(self, **kwargs):
        super(Shift, self).__init__(**kwargs)
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

    def get_user(self, client):
        """Return a :class:`lib7shfits.users.User` class for the user
        associated with this shift.
        An API fetch will be used to fetch this data (once)"""
        if self._user is None:
            from . import users
            self._user = users.get_user(self.user_id, client=client)
        return self._user

    def get_role(self, client):
        """Return a :class:`lib7shifts.roles.Role` object for the role
        specified by the shift.
        An API fetch will be used to fulfill this call."""
        if self._role is None:
            from . import roles
            self._role = roles.get_role(self.role_id, client=client)
        return self._role

    def get_location(self, client):
        """Returns a :class:`lib7shifts.locations.Location` object
        corresponding to the location of the shift.
        An API fetch will be used to fetch this data (once)"""
        if self._location is None:
            from . import locations
            self._location = locations.get_location(
                self.location_id, client=client)
        return self._location

    def get_department(self, client):
        """Returns a :class:`lib7shifts.departments.Department` object
        corresponding to the shift.
        An API fetch will be used to fetch this data (once)"""
        if self._department is None:
            from . import departments
            self._department = departments.get_department(
                self.department_id, client=client)
        return self._department
