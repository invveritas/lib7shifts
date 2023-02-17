"""
Library for representing 7shifts Users.
"""
from . import base
from . import exceptions
from .dates import to_local_date

ENDPOINT = '/v2/company/{company_id}/users'


def get_user(client, company_id, user_id, **urlopen_kw):
    """Implements the 'Read' API in 7Shifts for the given `user_id`.
    Returns a :class:`User` object, or raises
    :class:`exceptions.EntityNotFoundError` if the user wasn't found.
    For full user information, pass the following for **urlopen_kw:

        {'deep': 1}

    """
    response = client.read(ENDPOINT.format(company_id=company_id), user_id,
                           **urlopen_kw)
    try:
        return User(**response['data'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('User', user_id)


def list_users(client, company_id, **kwargs):
    """Implements the 'List' operation for 7shifts users, returning all the
    users associated with the company you've authenticated with (by default).

    Pass in an active :class:`lib7shifts.APIClient` object and any of the
    following parameters supported by the API:

    - limit: limit the number of results to be returned
    - offset: return results starting from an offset
    - order_field: a field to order results by, eg: order_field=shift.modified
    - order_dir: "asc" or "desc"

    Returns a :class:`UserList` object containing :class:`User` objects.
    """
    return UserList.from_api_data(
        company_id,
        base.page_api_get_results(
            client, ENDPOINT.format(company_id=company_id),
            **kwargs, limit=200),
        client=client)


class User(base.APIObject):
    """
    Represents a User from the 7shifts API, with all the same attributes
    returned by the API..
    """

    def __init__(self, company_id, **kwargs):
        super(User, self).__init__(**kwargs)
        self.company_id = company_id
        self._company = None

    def __getattr__(self, name):
        """
        Because this class is passed a nested dictionary, the parent's
        behaviour needs to be overloaded to look deeper in the dict to find its
        attributes.
        """
        return self._api_data(name)

    def _api_data(self, name):
        """
        This object wraps calls to the class's underlying data dictionary,
        allowing us to abstract that dictionary away through layers of caching
        etc.
        """
        return super(User, self)._api_data()[name]

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

    def get_company(self):
        """Return a :class:`lib7shfits.companies.Company` object
        associated with this user. If the initial request to get this user
        returned company data, that data will be used to populate the company
        object. Otherwise, another API fetch must be used to populate
        company data. As such, the richness of company data may not be the
        same between the two methods."""
        if self._company is None:
            from . import companies
            self._company = companies.get_company(
                self.client, self.company_id)
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

    def get_wages(self):
        """Returns a dictionary of wage data for the user. This method utilizes
        an undocumented API endpoint - the same one used in the 7shifts UI."""
        return self.client.read(
            self._api_context, "wages")['data']

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


class UserList(list):
    """
    An interable list of User objects.
    """

    @classmethod
    def from_api_data(cls, company_id, data, client=None):
        """Provide this method with the user data returned directly from
        the API in raw format.
        """
        obj_list = []
        for item in data:
            obj_list.append(User(**item, client=client))
        return cls(obj_list)


class Wage(base.APIObject):
    """Represent a wage in a general, easier to use way.

    Populate with a dictionary of kwargs generally containing:
    - user_id: int
    - role_id: int (or None for salaried)
    - effective_date: in YYYY-MM-DD string form
    - wage_type: (either 'hourly' or 'weekly_salary')
    - wage_cents: integer
    """

    def __init__(self, **kwargs):
        super(Wage, self).__init__(**kwargs)
        self.effective_date = to_local_date(kwargs.get('effective_date'))

    @property
    def per_hour(self):
        """Returns the per-hour equivalent for this wage. If this is salaried
        role, returns 0.0"""
        if self.is_salary():
            return 0.0
        return self.wage_cents / 100.0

    def is_hourly(self):
        """Returns True if this is an hourly wage"""
        if self.wage_type == "hourly":
            return True
        return False

    def is_salary(self):
        """Returns True if this is a salaried wage"""
        if self.wage_type == "weekly_salary":
            return True
        return False
