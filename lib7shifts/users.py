"""
Library for representing 7shifts Users.
"""
from . import base
from . import exceptions

ENDPOINT = '/users'

def get_user(user_id, client=None):
    """Implements the 'Read' API in 7Shifts for the given `user_id`.
    Returns a :class:`User` object, or raises
    :class:`exceptions.EntityNotFoundError` if the user wasn't found."""
    response = client.call("{}/{:d}".format(ENDPOINT, user_id))
    try:
        return User(**response['data']['user'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('User', user_id)

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

    @property
    def payroll_id(self):
        """
        Returns the employee ID number used in payroll integrations/reports.

        ..note::
            This field wasn't present in the API documentation but it does
            exist in the API results as of June 2019
        """
        return self.payroll_id

    def is_employee(self):
        "Returns True if the user_type_id is 1 (employee) - doesn't include mgmt"
        if self.user_type_id == 1:
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
                self.company_id, client=self.client)
        return self._company
