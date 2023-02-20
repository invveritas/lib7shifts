"""
This module covers Events-related methods and objects for the 7shifts API.

See https://www.7shifts.com/partner-api#toc-events for details.
"""
from . import base
from . import dates
from . import locations
from . import exceptions

ENDPOINT = '/v2/company/{company_id}/events'


def list_events(client, company_id, **kwargs):
    """Retrieve a list of schedule events for the given timeframe.

    Supported kwargs::

        - location_id: the location bound to the schedule events
        - start_date: a YYYY-MM-DD formatted date (required)
        - end_date: a YYYY-MM-DD formatted date (required)

    """
    if 'start_date' not in kwargs:
        raise RuntimeError("start_date not provided for list_events, required")
    if 'end_date' not in kwargs:
        raise RuntimeError("end_date not provided for list_events, required")
    for item in client.list(ENDPOINT.format(
            company_id=company_id), fields=kwargs)['data']:
        yield Event(**item)


def get_event(client, company_id, event_id):
    """Implements the 'Read' method from the 7shifts API for events.
    Returns a :class:`Event` object."""
    response = client.read(ENDPOINT.format(
        company_id=company_id), event_id)
    try:
        return Event(**response['data'])
    except KeyError:
        raise exceptions.EntityNotFoundError('Event', event_id)


def create_event(client, company_id, **kwargs):
    """Creates an event as defined in the API documentation. Supports
    the following parameters:

    - location_ids: a required list of integers ie: [1232, 4392]
    - start_date: a required YYYY-MM-DD format date
    - start_time: a required time string eg. 09:00:00
    - end_date: required, same format as above
    - end_time: required, same format as above
    - title: required, a text-based name for the event
    - is_multi_day: required boolean, set true for events spanning days
    - description: a textual description of the event
    - color: a hex RGB code for the event color, eg. 5ea17c
    - recurrence: see RFC 5545. Eg.
        "Daily for 10 occurrences ==> 
            (1997 9:00 AM EDT) September 2-11 DTSTART;
            TZID=America/New_York:19970902T090000
            RRULE:FREQ=DAILY;COUNT=10"

    Returns the ID of the event upon successful creation.
    """
    response = client.create(ENDPOINT.format(
        company_id=company_id), body=kwargs)
    return response


def update_event(client, company_id, event_id, **kwargs):
    """
    Implements the Update method for the Events API. You can update any of the
    following attributes by providing them as kwargs:

    - location_ids: a required list of integers ie: [1232, 4392]
    - start_date: a required YYYY-MM-DD format date
    - start_time: a required time string eg. 09:00:00
    - end_date: required, same format as above
    - end_time: required, same format as above
    - title: required, a text-based name for the event
    - is_multi_day: required boolean, set true for events spanning days
    - description: a textual description of the event
    - color: a hex RGB code for the event color, eg. 5ea17c
    - recurrence: see RFC 5545. Eg.
        "Daily for 10 occurrences ==> 
            (1997 9:00 AM EDT) September 2-11 DTSTART;
            TZID=America/New_York:19970902T090000
            RRULE:FREQ=DAILY;COUNT=10"
    - recurrence_target: either "THIS" or "THIS_AND_FUTURE"

    You must also pass a 'client' kwarg with an active API client, and a
    company_id.
    Upon success, returns the event JSON for all affected events.
    """
    response = client.update(ENDPOINT.format(
        company_id=company_id), event_id, method='PATCH', body=kwargs)
    return response['data']


def delete_event(client, company_id, event_id, **kwargs):
    """
    Implements the Delete API method for Events.

    Pass in the ID number for the event to be deleted, a company ID, 
    and an active API client. Also supports these kwargs:

    - recurrence_target: either THIS or THIS_AND_FUTURE
    - start_date: start of the targeted range for recurrence, in format:
        YYYY-MM-DD HH:MM:SS

    """
    client.delete(ENDPOINT.format(
        company_id=company_id), event_id, fields=kwargs)


class Event(base.APIObject):
    """
    Represents the Event object as defined in the API. Attributes defined by
    the API include:

    - id
    - title
    - description
    - start_date (YYYY-MM-DD format)
    - start_time (HH:MM:SS format)
    - end_date (YYYY-MM-DD format)
    - end_time (HH:MM:SS format)
    - color
    - location_ids (see also :meth:`get_locations`)
    - event_type
    - recurrence (see RFC 5545)
    - is_multi_day (true or false)

    """
    @property
    def start(self):
        "Returns a :class:`datetime.datetime` object for the start time"
        return dates.to_datetime(
            "{} {}".format(self.get('date'), self.get('start')))
