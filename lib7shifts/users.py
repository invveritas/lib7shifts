"""
Library for representing 7shifts Users.
"""
from . import base
from . import exceptions
from .dates import to_local_date

ENDPOINT = '/v1/users'


def get_user(client, user_id, **urlopen_kw):
    """Implements the 'Read' API in 7Shifts for the given `user_id`.
    Returns a :class:`User` object, or raises
    :class:`exceptions.EntityNotFoundError` if the user wasn't found.
    For full user information, pass the following for **urlopen_kw:

        {'deep': 1}

    """
    response = client.read(ENDPOINT, user_id, **urlopen_kw)
    try:
        return User(**response['data'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('User', user_id)


def list_users(client, **kwargs):
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
    response = client.list(ENDPOINT, fields=kwargs)
    return UserList.from_api_data(response['data'], client=client)


class User(base.APIObject):
    """
    Represents a User from the 7shifts API, with all the same attributes
    returned by the API..
    """

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self._company = None

    def __getattr__(self, name):
        """
        Because this class is passed a nested dictionary, the parent's
        behaviour needs to be overloaded to look deeper in the dict to find its
        attributes.
        """
        return self._api_data('user')[name]

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
        if self.user_type_id == 1:
            return True
        return False

    def is_admin(self):
        "Returns True if the user_type_id is set to 2 (admin)"
        if self.user_type_id == 2:
            return True
        return False

    def is_manager(self):
        "Returns True if the user_type_id is set to 3 (manager)"
        if self.user_type_id == 3:
            return True
        return False

    def is_asst_manager(self):
        "Returns True if the user_type_id is set to 4 (asst mgr)"
        if self.user_type_id == 4:
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
            try:
                self._company = companies.Company(
                    **self._api_data('company'), client=self.client)
            except KeyError:
                self._company = companies.get_company(
                    self.client, self.company_id)
        return self._company

    def get_departments(self):
        """Return an iterable of :class:`lib7shifts.Department` objects that
        apply to this user.

        IMPORTANT: This method only works if the call to get this user was
        made directly against the user id rather than through a list method.
        """
        from . import departments
        try:
            for data in self._api_data('department'):
                yield departments.Department(**data, client=self.client)
        except KeyError:
            raise RuntimeError((
                "Unable to get department information for user without"
                " deep=1"))

    def get_locations(self):
        """Return an iterable of :class:`lib7shifts.Location` objects that
        apply to this user.

        IMPORTANT: This method only works if the call to get this user was
        made directly against the user id rather than through a list method.
        """
        from . import locations
        try:
            for data in self._api_data('location'):
                yield locations.Location(**data, client=self.client)
        except KeyError:
            raise RuntimeError((
                "Unable to get location information for user without"
                " deep=1"))

    def get_permissions(self):
        """Return a dictionary of permissions settings for this user.

        IMPORTANT: This method only works if the call to get this user was
        made directly against the user id rather than through a list method.
        """
        try:
            return self._api_data('permission')
        except KeyError:
            raise RuntimeError((
                "Unable to get permission information for user without"
                " deep=1"))

    def get_roles(self):
        """Return role information for the user, such as the name, department
        id, etc. A :class:`lib7shifts.RoleList` object will be returned, since
        users can have more than one role associated with them.

        IMPORTANT: This method only works if the call to get this user was
        made directly against the user id rather than through a list method."""
        try:
            from . import roles
            for data in self._api_data('role'):
                yield roles.Role(**data, client=self.client)
        except KeyError:
            raise RuntimeError(
                "Unable to get role information for user without deep=1")

    def get_wages(self):
        """Returns a dictionary of wage data for the user. This method utilizes
        an undocumented API endpoint - the same one used in the 7shifts UI."""
        return self.client.read(
            "/v1/user/{:d}".format(self.id), "wages")['data']


class UserList(list):
    """
    An interable list of User objects.
    """

    @classmethod
    def from_api_data(cls, data, client=None):
        """Provide this method with the user data returned directly from
        the API in raw format.
        """
        obj_list = []
        for item in data:
            obj_list.append(User(**item['user'], client=client))
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
