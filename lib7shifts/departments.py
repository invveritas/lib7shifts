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
        return Department(**response['data']['department'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Department', department_id)


def list_departments(client, company_id, **kwargs):
    """Implements the 'List' operation for 7shifts departments, returning the
    departments associated with the company you've authenticated with (by
    default).

    Pass in an active :class:`lib7shifts.APIClient` object and any of the
    following parameters supported by the API:

    - limit: limit the number of results to be returned
    - offset: return results starting from an offset
    - order_field: the field to order results by, eg:
        order_field=shift.modified
    - order_dir: "asc" or "desc"

    Returns a :class:`RoleList` object containing :class:`Role` objects.
    """
    return DepartmentList.from_api_data(base.page_api_get_results(
        client, ENDPOINT.format(company_id=company_id), **kwargs))


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
            obj_list.append(Department(**item, client=client))
        return cls(obj_list)
