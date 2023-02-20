"""
Library for representing 7shifts Users.
"""
from . import base
from . import exceptions

ENDPOINT = '/v2/company/{company_id}/users'


def get_user(client, company_id, user_id, **urlopen_kw):
    """Implements the 'Read' API in 7Shifts for the given `user_id`.
    Returns a :class:`User` object, or raises
    :class:`exceptions.EntityNotFoundError` if the user wasn't found.
    """
    response = client.read(ENDPOINT.format(company_id=company_id), user_id,
                           **urlopen_kw)
    try:
        return User(**response['data'])
    except KeyError:
        raise exceptions.EntityNotFoundError('User', user_id)


def list_users(client, company_id, **kwargs):
    """Implements the 'List' operation for 7shifts users, returning all the
    users associated with the company you've authenticated with (by default).

    Pass in an active :class:`lib7shifts.APIClient` object, a company ID and
    any of the following parameters supported by the API:

    - modified_since: a YYYY-MM-DD formatted string
    - location_id (not compatible with department_id and role_id)
    - department_id (not compatible with location_id and role_id)
    - role_id (not compatible with location_id and department_id)
    - status: either 'active' or 'inactive'
    - name: filter by full or partial employee name

    Returns a :class:`UserList` object containing :class:`User` objects.
    """
    if 'limit' not in kwargs:
        kwargs['limit'] = 200
    for item in base.page_api_get_results(
            client, ENDPOINT.format(company_id=company_id),
            **kwargs):
        yield User(**item)


class User(base.APIObject):
    """
    Represents a User from the 7shifts API, with all the same attributes
    returned by the API..
    """

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self._company = None
        self._wages = None

    @property
    def punch_code(self):
        """
        Returns the code that the employee uses to punch into time clocking.

        ..note::
            This field is returned as `employee_id` by the 7shifts API, which
            can be confused with the ID number corresponding to the employee,
            so we've added `punch_code` as an alias to be more explicit.
        """
        return self.employee_id

    def is_employee(self):
        """Returns True if the user_type_id is 1 (employee) - doesn't include
        managers"""
        if self.type == "employee":
            return True
        return False

    def is_admin(self):
        "Returns True if the user_type_id is set to 2 (admin)"
        if self.type == "admin":
            return True
        return False

    def is_manager(self):
        "Returns True if the user_type_id is set to 3 (manager)"
        if self.type == "manager":
            return True
        return False

    def is_asst_manager(self):
        "Returns True if the user_type_id is set to 4 (asst mgr)"
        if self.type == "asst mgr":
            return True
        return False

    def is_paid_hourly(self):
        "Returns True if the employee is set to be paid Hourly"
        if self.wage_type == 'hourly':
            return True
        return False

    def is_salaried(self):
        "Returns True if the employee is set to be paid by Salary"
        if self.wage_type == 'salaried':
            return True
        return False

    def get_company(self, client):
        """Return a :class:`lib7shfits.companies.Company` object
        associated with this user. If the initial request to get this user
        returned company data, that data will be used to populate the company
        object. Otherwise, another API fetch must be used to populate
        company data. As such, the richness of company data may not be the
        same between the two methods."""
        if self._company is None:
            from . import companies
            self._company = companies.get_company(
                client, self.company_id)
        return self._company

    def get_departments(self):
        """raise NotImplementedError
        """
        raise NotImplementedError

    def get_locations(self):
        """raise NotImplementedError
        """
        raise NotImplementedError

    def get_permissions(self):
        """raise NotImplementedError
        """
        raise NotImplementedError

    def get_roles(self):
        """raise NotImplementedError."""
        raise NotImplementedError

    def get_wages(self, client):
        """Returns a dictionary of wage data for the user. This method utilizes
        an undocumented API endpoint - the same one used in the 7shifts UI."""
        if self._wages is None:
            from . import wages
            self._wages = wages.list_user_wages(
                client, self.company_id, self.id)
        return self._wages

    def list_assignments(self):
        """Lists assigned locations, departments and roles for this user"""
        return self.client.read(self._api_context, "assignments")['data']

    def list_location_assignments(self):
        """Lists the locations that the current user is assigned to"""
        return self.client.read(
            self._api_context, "location_assignments")['data']

    def list_department_assignments(self):
        """Lists the departments that the current user is assigned to"""
        return self.client.read(
            self._api_context, "department_assignments")['data']

    def list_role_assignments(self):
        """Lists the roles that the current user is assigned to"""
        return self.client.read(
            self._api_context, "role_assignments")['data']

    def _api_context(self):
        """Returns an API context for the current user"""
        return f"{ENDPOINT}/{self.id}"
