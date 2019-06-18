class APIError(Exception):

    def __init__(self, status, response=None):
        self.status = status
        self.response = response.data
        #self.status_text = self.response['status']
        #self.message = self.response['message']
        #self.type_text = self.response['type']

    def __str__(self):
        return "{}\n{}".format(self.status, self.response)
        #return "{}:{}\n{}".format(self.status_text, self.type_text, self.message)

    def __repr__(self):
        return self.__str__()

class EntityNotFoundError(object):

    def __init__(self, entity_type, entity_id):
        self.entity_type = entity_type
        self.entity_id = entity_id

    def __str__(self):
        return "{} with id '{}' not found".format(
            self.entity_type, self.entity_id)

    def __repr__(self):
        return "{}({}:{})".format(
            self.__name__, self.entity_type, self.entity_id)
