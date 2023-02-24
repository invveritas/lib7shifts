import json


class APIError(Exception):
    """This error is raised whenever an API request fails with a status > 299.
    Most API errors come with JSON-formatted details, which are unpacked by
    this object and broken down nicely for its string representation."""

    def __init__(self, status, response=None):
        self.status = status
        self._response = None
        self.response = response.data

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        try:
            self._response = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            self._response = {'error': f'{value}'}  # use object's built-in

    def pretty_response(self):
        """Since response is a dictionary, this method returns it in a
        pretty-printed key: value formatted string."""
        retval = ""
        for key, value in self.response.items():
            retval += f"{key}: {value}\n"
        return retval

    def __str__(self):
        return "{}\n{}".format(self.status, json.dumps(self.response))

    def __repr__(self):
        return self.__str__()


class EntityNotFoundError(Exception):

    def __init__(self, entity_type, entity_id):
        self.entity_type = entity_type
        self.entity_id = entity_id

    def __str__(self):
        return "{} with id '{}' not found".format(
            self.entity_type, self.entity_id)

    def __repr__(self):
        return "{}({}:{})".format(
            self.__class__.__name__, self.entity_type, self.entity_id)
