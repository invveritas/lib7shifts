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
        self._data = kwargs

    @property
    def client(self):
        "Returns a reference to the configured API Client"
        return self._client

    @property
    def created(self):
        "Returns a :class:`datetime.datetime` object for shift creation time"
        return dates.to_datetime(self._data['created'])

    @property
    def modified(self):
        """Returns a :class:`datetime.datetime` object corresponding to the
        last time this shift was modified"""
        return dates.to_datetime(self._data['modified'])

    def __getattr__(self, name):
        """
        Handy method for exposing all of the API properties without creating
        object attributes for them all in advance (new API attributes can show
        up at any time). This method is only called if the object doesn't already
        have an attribute of ``name``, so not a risk of breaking the object
        and thus, we can add attributes to override this behaviour, as well.
        """
        return self._data[name]

    def __str__(self):
        return self._data.__str__()
