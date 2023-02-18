"""
Retrieve the identity associated with the current Bearer access token.
"""

ENDPOINT = '/v2/whoami'


def get_whoami(client):
    """Retrieve the results from the 'whoami' endpoint to determine the current
    identity associated with the access token in use."""
    return client.get_endpoint(ENDPOINT)['data']
