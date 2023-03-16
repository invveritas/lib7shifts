"""
Library for representing 7shifts User Assignments.
"""
from . import base
from . import exceptions

ENDPOINT = '/v2/company/{company_id}/users/{user_id}/assignments'


def list_user_assignments(client, company_id, user_id, **urlopen_kw):
    """Implements the 'List' API in 7Shifts for the given `user_id`.
    Returns a :class:`Assignments` object or raises
    :class:`exceptions.EntityNotFoundError` if the user wasn't found.
    """
    response = client.get_endpoint(
        ENDPOINT.format(company_id=company_id, user_id=user_id),
        **urlopen_kw)
    try:
        return Assignments(**response['data'])
    except KeyError:
        raise exceptions.EntityNotFoundError('Assignments', user_id)


class Assignments(base.APIObject):
    """Represent a user assignment including locations, departments, and roles.

    The assignment is designed to be populated from API data, whereby a dict
    is passed in that looks like this::

            {
                "locations": [
                    {
                        "id": 4569,
                        "name": "Restaurant"
                    }
                ],
                "departments": [
                    {
                        "id": 7890,
                        "company_id": 1234,
                        "location_id": 4569,
                        "name": "FOH"
                    }
                ],          
                "roles": [
                    {
                        "id": 2583,
                        "company_id": 1234,
                        "location_id": 4569,
                        "department_id": 7890,
                        "name": "Host",
                        "is_primary": false,
                        "skill_level": 2,
                        "sort": 0
                    }
                    ]
            }

    """

    def __init__(self, **kwargs):
        super(Assignments, self).__init__(**kwargs)
