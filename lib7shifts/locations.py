"""
API methods and objects related to the 7Shifts Location API.

See https://developers.7shifts.com/reference/getlocationlistbycompany for
details.
"""
from . import base
from . import exceptions

ENDPOINT = '/v2/company/{company_id}/locations'


def get_location(client, company_id, location_id):
    """Implments the 'Read' method for 7shifts locations. Returns a
    :class:`Location` object."""
    response = client.read(ENDPOINT.format(company_id=company_id), location_id)
    try:
        return Location(**response['data'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Location', location_id)


def list_locations(client, company_id, **kwargs):
    """
    Implement the List method for the 7shifts API.

    Supports the modified_since kwarg.

    See the API docs for details.
    """
    if 'limit' not in kwargs:
        kwargs['limit'] = 100
    for item in base.page_api_get_results(
            client, ENDPOINT.format(company_id=company_id), **kwargs):
        yield Location(**item, client=client)


class Location(base.APIObject):
    """
    Represents a 7shifts Location object, providing all the same attributes
    documented in the Read API for Locations.
    """
