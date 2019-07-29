"""
Library for representing 7shifts Users.
"""
from . import base
from . import exceptions

ENDPOINT = '/v1/users'


def get_user(client, user_id):
    """Implements the 'Read' API in 7Shifts for the given `user_id`.
    Returns a :class:`User` object, or raises
    :class:`exceptions.EntityNotFoundError` if the user wasn't found."""
    response = client.read(ENDPOINT, user_id)
    try:
        return User(**response['data']['user'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('User', user_id)


def list_users(client, **kwargs):
    """Implements the 'List' operation for 7shifts users, returning all the
    users associated with the company you've authenticated with (by default).

    Pass in an active :class:`lib7shifts.APIClient` object and any of the
    following parameters supported by the API:

    - limit: limit the number of results to be returned
    - offset: return results starting from an offset
    - order_field: the field to order results by, eg: order_field=shift.modified
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
        "Returns True if the user_type_id is 1 (employee) - doesn't include mgmt"
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
        associated with this shift.
        An API fetch will be used to fetch this data (once)"""
        if self._company is None:
            from . import companies
            self._company = companies.get_company(
                self.company_id, self.client)
        return self._company

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
