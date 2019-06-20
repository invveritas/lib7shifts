"""
Establish base classes with common design patterns, to be inherited by API
Objects
"""

class APIObject(object):
    """
    Define an object that is populated with data about the entity being
    represented, directly from the API (API key-value pairs are constructor
    arguments). Optionally, pass an :class:`lib7shifts.APIClient`
    to the constructor as the :attr:`client` kwarg to enable real-time fetches
    of object-related references (fetch methods must be implemented in sub-
    classes)
    """

    def __init__(self, **kwargs):
        self._client = kwargs.pop('client', None)
        self.__data = kwargs

    @property
    def client(self):
        "Returns a reference to the configured API Client"
        return self._client

    @property
    def created(self):
        "Returns a :class:`datetime.datetime` object for shift creation time"
        return dates.to_datetime(self._api_data('created'))

    @property
    def modified(self):
        """Returns a :class:`datetime.datetime` object corresponding to the
        last time this shift was modified"""
        return dates.to_datetime(self._api_data('modified'))

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
        etc.
        """
        return self.__data[name]

    def __getattr__(self, name):
        """
        Handy method for exposing all of the API properties without creating
        object attributes for them all in advance (new API attributes can show
        up at any time). This method is only called if the object doesn't already
        have an attribute of ``name``, so not a risk of breaking the object
        and thus, we can add attributes to override this behaviour, as well.
        """
        return self._api_data(name)

    def __str__(self):
        return self.__data.__str__()
