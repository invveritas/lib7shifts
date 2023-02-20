"""
API methods and objects related to 7Shifts Departments.

See https://developers.7shifts.com/reference/listdepartments for details about
supported operations.
"""
from . import base
from . import exceptions
from . import companies

ENDPOINT = '/v2/company/{company_id}/departments'


def get_department(client, company_id, department_id):
    """Implements the 'Read' method from the 7shifts API for departments.
    Returns a :class:`Department` object."""
    response = client.read(ENDPOINT.format(company_id=company_id),
                           department_id)
    try:
        return Department(**response['data'])
    except KeyError:
        raise exceptions.EntityNotFoundError('Department', department_id)


def list_departments(client, company_id, **kwargs):
    """Implements the 'List' operation for 7shifts departments, returning the
    departments associated with the company you've authenticated with (by
    default).

    Pass in an active :class:`lib7shifts.APIClient` object and any of the
    following parameters supported by the API:

    - modified_since: a YYYY-MM-DD date string
    - location_id: filter to a specific location

    Returns an iterable of :class:`Department` objects.
    """
    if 'limit' not in kwargs:
        kwargs['limit'] = 100
    for item in base.page_api_get_results(
            client, ENDPOINT.format(company_id=company_id), **kwargs):
        yield Department(**item)


class Department(base.APIObject):
    """
    Represents a 7shifts Shift object, with all the same attributes as the
    Shift object defined in the API documentation.
    """
