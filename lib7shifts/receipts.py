"""
This module is used to interact with the 7shifts API to create or update sales
receipts in 7shifts, which are used for sales projections and dashboards.

See https://www.7shifts.com/partner-api#toc-sales-integration for more details.
"""

ENDPOINT = '/v1/receipts'


def create_receipt(client, **kwargs):
    """Creates a sales receipt in the 7shifts API.
    Provide the following kwargs:
    - total: sales total as an integer number of cents
    - open_date: a string-based UTC timestamp for the record, of form:
      2017-09-10 09:01:15
    - location_id: the id of the location where the sale occurred
    - external_id: optional, a GUID or similar from POS

    Returns a 7shifts integer ID for the newly created receipt.
    """
    response = client.create(ENDPOINT, body={'receipt': kwargs})
    return response['data']['receipt']['id']


def update_receipt(client, receipt_id, **kwargs):
    """Update an sale total for an existing receipt by ID.
    Pass the following kwargs (each are optional):
    - total: sales total as an integer number of cents (to be updated)
    - location_id: the id of the location where the sale occurred
    - external_id: a GUID or similar from the source POS

    location_id and external_id must match the original receipt, and are
    mandatory fields. Only the sale total can be updated, such as in the case
    of a refund.

    Returns the API status dictionary directly.
    """
    response = client.update(ENDPOINT, receipt_id, body={'receipt': kwargs})
    return response
