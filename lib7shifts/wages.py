"""
Library for representing 7shifts User Wages.
"""
from . import base
from . import exceptions
from .dates import to_local_date

ENDPOINT = '/v2/company/{company_id}/users/{user_id}/wages'


def list_user_wages(client, company_id, user_id, **urlopen_kw):
    """Implements the 'List' API in 7Shifts for the given `user_id`.
    Returns a tuple with 2 :class:`WageList` objects -- one for "current wages"
    and one for "upcoming wages", mathing API behaviour, or raises
    :class:`exceptions.EntityNotFoundError` if the user wasn't found.
    """
    response = client.get_endpoint(
        ENDPOINT.format(company_id=company_id, user_id=user_id),
        **urlopen_kw)
    try:
        return (
            WageList(response['data']['current_wages'], client=client),
            WageList(response['data']['upcoming_wages'], client=client))
    except KeyError:
        raise exceptions.EntityNotFoundError('WageList', user_id)


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


class WageList(list):
    """
    An interable list of User Wage objects.
    """

    @classmethod
    def from_api_data(cls, data, client=None):
        """Provide this method with the user data returned directly from
        the API in raw format.
        """
        obj_list = []
        for item in data:
            obj_list.append(Wage(**item, client=client))
        return cls(obj_list)
