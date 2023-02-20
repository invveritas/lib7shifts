"""
A library to house all API-related calls and objects for 7Shifts Companies.

See https://www.7shifts.com/partner-api#toc-companies for more details.
"""
from . import base
from . import exceptions

ENDPOINT = '/v2/companies'


def get_company(client, company_id):
    """Implements the 'Read' API in 7Shifts for Companies.
    Returns a :class:`Company` object."""
    response = client.read(ENDPOINT, company_id)
    try:
        return Company(**response['data'])
    except KeyError:
        raise exceptions.EntityNotFoundError('Company', company_id)


def list_companies(client):
    """Implements the 'List' operation for 7shifts companies.
    """
    for item in client.list(ENDPOINT)['data']:
        yield Company(**item)


class Company(base.APIObject):
    """
    Represents a Company in 7shifts. This object has the same attributes as
    the API object.
    """
    pass
