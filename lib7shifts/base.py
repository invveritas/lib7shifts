"""
Establish base classes with common design patterns, to be inherited by API
Objects
"""
import json
from . import dates


def page_api_get_results(client, endpoint, **kwargs):
    """Execute an API call (GET) that is expected to have paging support.
    This method will yield individual result rows as an iterable, avoiding the
    need for the caller to concern themselves with the details of paging.

    Unless `limit` is explicitly passed by the caller, a default page size of
    100 will be used.
    """
    if 'limit' not in kwargs:
        kwargs['limit'] = 100
    next = True
    while next:
        response = client.list(endpoint, fields=kwargs)
        for item in response['data']:
            yield item
        next = response['meta']['cursor']['next']
        kwargs['cursor'] = next


class APIObject(dict):
    """
    Define a dict-like object that is populated with data about the entity
    being represented, directly from the API (API key-value pairs are
    constructor arguments).
    """

    def __init__(self, *args, **kwargs):
        super(APIObject, self).__init__(*args, **kwargs)

    @property
    def created(self):
        "Returns a :class:`datetime.datetime` object for shift creation time"
        return dates.to_datetime(self.get('created'))

    @property
    def modified(self):
        """Returns a :class:`datetime.datetime` object corresponding to the
        last time this shift was modified"""
        return dates.to_datetime(self.get('modified'))

    def refresh(self):
        """Full CRUD implementations need to ensure that objects can be
        refreshed after they are updated through the API. This method provides
        a common code path to trigger object updates. Generally speaking,
        this method should call the appropriate Read method for the
        object being refreshed and replace the object's underlying _data
        dict with the new dataset.
        """
        raise NotImplementedError

    def _api_data(self, name):
        """
        This object wraps calls to the class's underlying data dictionary,
        allowing us to abstract that dictionary away through layers of caching
        etc. *Note: This is here only for backwards compatibility with older
        code*.
        """
        return self.get(name)

    def _update_api_data(self, new_data):
        """
        Use this method to replace the underlying API data for an object.
        This method is important to trigger invalidation/refreshes of any
        underlying cache layer. At the moment, the entirety of the object's
        data must be replaced, no merging takes place.

        Should only be called from within an object or its descendants.
        """
        raise NotImplementedError
