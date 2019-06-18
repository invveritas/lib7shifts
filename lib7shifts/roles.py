"""
API methods and objects related to 7Shifts Roles.

See https://www.7shifts.com/partner-api#toc-roles for details about supported
operations.
"""
from . import base
from . import dates

ENDPOINT = '/roles'

def get_role(role_id, client=None):
    """Implements the 'Read' method from the 7shifts API for roles.
    Returns a :class:`Role` object."""
    response = client.call("{}/{:d}".format(ENDPOINT, role_id))
    try:
        return Role(**response['data']['role'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Role', role_id)

def list_roles(**kwargs):
    """Implements the 'List' operation for 7shifts roles, returning all the
    roles associated with the company you've authenticated with (by default).

    Pass in an active :class:`lib7shifts.APIClient` object and any of the
    following parameters supported by the API:

    - limit: limit the number of results to be returned
    - offset: return results starting from an offset
    - order_field: the field to order results by, eg: order_field=shift.modified
    - order_dir: "asc" or "desc"

    Returns a :class:`RoleList` object containing :class:`Role` objects.
    """
    client = kwargs.pop('client')
    response = client.call("{}".format(ENDPOINT), params=kwargs)
    return RoleList.from_api_data(response['data'], client=client)

class Role(base.APIObject):
    """
    Represents a 7shifts Role object, with all the same attributes as the
    Role object defined in the API documentation.
    """
    pass

class RoleList(list):
    """
    An interable list of Role objects.
    """

    @classmethod
    def from_api_data(cls, data, client=None):
        """Provide this method with the role data returned directly from
        the API in raw format.
        """
        obj_list = []
        for item in data:
            obj_list.append(Role(**item, client=client))
        return cls(obj_list)
