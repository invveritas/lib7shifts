"""
API methods and objects related to 7Shifts Roles.

See https://developers.7shifts.com/reference/listroles for details about
supported operations.
"""
from . import base
from . import exceptions

ENDPOINT = '/v2/company/{company_id}/roles'


def get_role(client, company_id, role_id):
    """Implements the 'Read' method from the 7shifts API for roles.
    Returns a :class:`Role` object."""
    response = client.read(ENDPOINT.format(company_id=company_id), role_id)
    try:
        return Role(**response['data'])
    except KeyError:
        raise exceptions.EntityNotFoundError('Role', role_id)


def list_roles(client, company_id, **kwargs):
    """Implements the 'List' operation for 7shifts roles, returning all the
    roles associated with the company you've authenticated with (by default).

    Pass in an active :class:`lib7shifts.APIClient` object and any of the
    following parameters supported by the API:

    - location_id:      an optional location to narrow down on
    - department_id:    an optional department to narrow down on
    - modified_since:   a YYYY-MM-DD formatted date to find records changed
                        after

    Returns an iterable of :class:`Role` objects.
    """
    if 'limit' not in kwargs:
        kwargs['limit'] = 200
    for item in base.page_api_get_results(
            client, ENDPOINT.format(company_id=company_id),
            **kwargs):
        yield Role(**item)


class Role(base.APIObject):
    """
    Represents a 7shifts Role object, with all the same attributes as the
    Role object defined in the API documentation.
    """
