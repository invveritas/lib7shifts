"""
This module covers Events-related methods and objects for the 7shifts API.

See https://www.7shifts.com/partner-api#toc-events for details.
"""
import datetime
from . import base
from . import dates
from . import locations

ENDPOINT = '/events'

def create_event(client, **kwargs):
    """Creates an event as defined in the API documentation. Supports
    the following parameters:

    - title
    - description
    - date ('YYYY-MM-DD' format)
    - start ('HH:MM:SS' format)
    - color (hexadecimal code as string, eg 'FBAF40')
    - location (as either a list of IDs or a :class:`locations.LocationList`)
    - client (api client object to use)

    Returns the ID of the event upon successful creation.
    """
    location = kwargs.pop('location')
    try:
        location = location.list_ids()
    except AttributeError:
        pass
    body = {'event': kwargs, 'location': location}
    response = client.create(ENDPOINT, body=body)
    return response['data']['event']['id']

def get_event(client, event_id):
    """Implements the 'Read' method from the 7shifts API for events.
    Returns a :class:`Event` object."""
    response = client.read(ENDPOINT, event_id)
    try:
        return Event(**response['data']['event'], client=client)
    except KeyError:
        raise exceptions.EntityNotFoundError('Event', event_id)

def update_event(client, event_id, **kwargs):
    """
    Implements the Update method for the Events API. You can update any of the
    following attributes by providing them as kwargs:

    - title
    - description
    - color
    - date (in 'YYYY-MM-DD' form)
    - start (in 'HH:MM:SS' form)

    You must also pass a 'client' kwarg with an active API client.
    Upon success, returns the ID of the event.
    """
    response = client.update(ENDPOINT, event_id, body={'event': kwargs})
    return response['data']['event']['id']

def delete_event(client, event_id):
    """
    Implements the Delete API method for Events.

    Pass in the ID number for the event to be deleted, and an active API
    client.
    """
    client.delete(ENDPOINT, event_id)

def list_events(client, **kwargs):
    """
    Implements the List operation in the Events API. Provide any of the
    following kwargs as filter criteria:

    - date: ('YYYY-MM-DD' format) for a single date
    - date[gte]: for dates greater than or equal to the value
    - date[lte]: for dates earlier than or on the value
    - limit: limit the results to return
    - offset: return results at a particular offset (for paging)
    - order_field: what to order results by, eg: event.modified
    - order_dir: the direction to order results in, either 'asc' or 'desc'

    You must also pass in an active 'client'.

    Returns an EventsList.
    """
    api_params = {}
    for name, val in kwargs.items():
        if isinstance(val, datetime.datetime):
            api_params[name] = dates.to_y_m_d(val)
        else:
            api_params[name] = val
    response = client.list(ENDPOINT, fields=api_params)
    return EventList.from_api_data(response['data'], client=client)

class Event(base.APIObject):
    """
    Represents the Event object as defined in the API. Attributes defined by
    the API include:

    - id
    - title
    - description
    - date (YYYY-MM-DD)
    - start (returned as full datetime in this class, time only on the API)
    - color
    - location (see also :meth:`get_locations`)
    - created
    - modified

    """
    @property
    def start(self):
        "Returns a :class:`datetime.datetime` object for the start time"
        return dates.to_datetime(
            "{} {}".format(self._api_data('date'), self._api_data('start')))

    def get_locations(self):
        "Returns an array of :class:`lib7shifts.locations.Location` objects"
        return locations.LocationList.from_id_list(
            self.location, client=self.client)

class EventList(list):
    """
    A list of :class:`Event` objects.
    """
    @classmethod
    def from_api_data(cls, data, client=None):
        """
        Given a set of API data from a List call, populate this class with
        :class:`Event` objects corresponding to the events.
        """
        events = list()
        for event in data:
            events.append(Event(**event['event'], client=client))
        return cls(events)
