"""
A library to house all API-related calls and objects for 7Shifts Companies.

See https://www.7shifts.com/partner-api#toc-companies for more details.
"""
from . import base

ENDPOINT = '/companies'

def get_company(company_id, client=None):
    """Implements the 'Read' API in 7Shifts for Companies.
    Returns a :class:`Company` object."""
    response = client.call("{}/{:d}".format(ENDPOINT, company_id))
    try:
        return Company(**response['data']['company'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Company', company_id)

class Company(base.APIObject):
    """
    Represents a Company in 7shifts. This object has the same attributes as
    the API object.
    """
    pass
