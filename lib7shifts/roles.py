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
        return Role(**response['data'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Role', role_id)


def list_roles(client, company_id, **kwargs):
    """Implements the 'List' operation for 7shifts roles, returning all the
    roles associated with the company you've authenticated with (by default).

    Pass in an active :class:`lib7shifts.APIClient` object and any of the
    following parameters supported by the API:

    - order_field: the field to order results by, eg:
        order_field=shift.modified
    - order_dir: "asc" or "desc"

    Returns a :class:`RoleList` object containing :class:`Role` objects.
    """
    if 'limit' not in kwargs:
        kwargs['limit'] = 200
    for item in base.page_api_get_results(
            client, ENDPOINT.format(company_id=company_id),
            **kwargs):
        yield Role(**item, client=client)


class Role(base.APIObject):
    """
    Represents a 7shifts Role object, with all the same attributes as the
    Role object defined in the API documentation.
    """
    pass
