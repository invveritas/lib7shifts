class APIError(Exception):

    def __init__(self, status, response=None):
        self.status = status
        self.response = response.data

    def __str__(self):
        return "{}\n{}".format(self.status, self.response)

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
