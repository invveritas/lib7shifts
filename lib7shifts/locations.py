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
        return Location(**response['data']['location'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Location', location_id)


def list_locations(client, company_id, **kwargs):
    """
    Implement the List method for the 7shifts API.

    Supported kwargs include:

    - limit
    - offset
    - order_field
    - order_dir

    See the API docs for details.
    """
    return LocationList.from_api_data(base.page_api_get_results(
        client, ENDPOINT.format(company_id=company_id), **kwargs))


class Location(base.APIObject):
    """
    Represents a 7shifts Location object, providing all the same attributes
    documented in the Read API for Locations.
    """
    pass


class LocationList(list):
    """
    An interable list of :class:`Location` objects.
    """
    @classmethod
    def from_api_data(cls, data, client=None):
        """
        Pass this method API data from a List operation, get back a
        LocationList populated with :class:`Location` objects.
        """
        obj_list = []
        for item in data:
            obj_list.append(Location(**item, client=client))
        return cls(obj_list)

    @classmethod
    def from_id_list(cls, location_ids, client=None):
        "Pass a list of location id's, get back a LocationList"
        locations = []
        for location in location_ids:
            locations.append(get_location(location, client=client))
        return cls(locations)

    def list_ids(self):
        "Returns a tuple of location IDs rather than the objects themselves"
        location_ids = list()
        for location in self:
            location_ids.append(location.id)
        return tuple(location_ids)
