"""
API methods and objects related to the 7Shifts Location API.

See https://www.7shifts.com/partner-api#toc-locations for details.
"""
from . import base

ENDPOINT = '/locations'

def get_location(location_id, client=None):
    """Implments the 'Read' method for 7shifts locations. Returns a
    :class:`Location` object."""
    response = client.call("{}/{:d}".format(ENDPOINT, location_id))
    try:
        return Location(**response['data']['location'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Location', location_id)

class Location(base.APIObject):
    """
    Represents a 7shifts Location object, providing all the same attributes
    documented in the Read API for Locations.
    """
    pass
