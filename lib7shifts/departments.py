"""
API methods and objects related to 7Shifts Departments.

See https://www.7shifts.com/partner-api#toc-departments for details about
supported operations.
"""
from . import base

ENDPOINT = '/v1/departments'

def get_department(client, department_id):
    """Implements the 'Read' method from the 7shifts API for departments.
    Returns a :class:`Department` object."""
    response = client.read(ENDPOINT, department_id)
    try:
        return Department(**response['data']['department'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Department', department_id)

def list_departments(client, **kwargs):
    """Implements the 'List' operation for 7shifts departments, returning the
    departments associated with the company you've authenticated with (by default).

    Pass in an active :class:`lib7shifts.APIClient` object and any of the
    following parameters supported by the API:

    - limit: limit the number of results to be returned
    - offset: return results starting from an offset
    - order_field: the field to order results by, eg: order_field=shift.modified
    - order_dir: "asc" or "desc"

    Returns a :class:`RoleList` object containing :class:`Role` objects.
    """
    response = client.list(ENDPOINT, fields=kwargs)
    return DepartmentList.from_api_data(response['data'], client=client)

class Department(base.APIObject):
    """
    Represents a 7shifts Shift object, with all the same attributes as the
    Shift object defined in the API documentation.
    """
    pass

class DepartmentList(list):
    """
    An interable list of :class:`Department` objects.
    """

    @classmethod
    def from_api_data(cls, data, client=None):
        """Provide this method with the department data returned directly from
        the API in raw format.
        """
        obj_list = []
        for item in data:
            obj_list.append(Department(**item['department'], client=client))
        return cls(obj_list)
