"""
API methods and objects related to the 7Shifts Location API.

See https://www.7shifts.com/partner-api#toc-locations for details.
"""
from . import base

ENDPOINT = '/locations'

def get_location(client, location_id):
    """Implments the 'Read' method for 7shifts locations. Returns a
    :class:`Location` object."""
    response = client.read(ENDPOINT, location_id)
    try:
        return Location(**response['data']['location'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Location', location_id)

def list_locations(client, **kwargs):
    """
    Implement the List method for the 7shifts API.

    Supported kwargs include:

    - limit
    - offset
    - order_field
    - order_dir

    See the API docs for details.
    """
    response = client.list(ENDPOINT, fields=kwargs)
    return LocationList.from_api_data(response['data'], client=client)

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
            obj_list.append(Location(**item['location'], client=client))
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
