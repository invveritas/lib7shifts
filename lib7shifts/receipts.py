"""
This module is used to interact with the 7shifts API to create or update sales
receipts in 7shifts, which are used for sales projections and dashboards.

See https://developers.7shifts.com/reference/listsalesreceipts for more
details.
"""
from . import base

ENDPOINT = '/v2/company/{company_id}/receipts'


def list_receipts(client, company_id, **kwargs):
    """List sales receipts from 7shifts. If no arguments are provided,
    the past 90 days' worth of receipts will be provided. Narrow that down with
    the following filter params, as kwargs:

      - location_id: the location where the transaction happened [required]
      - receipt_date[gte]: YYYY-MM-DD format for first date of receipts
      - receipt_date[lte]: as above but for end date
      - modified_since: YYYY-MM-DD format for receipts modified on/after date
      - status: one of [open, closed, voided, deleted]
      - external_user_id: filter results by external user id that created them
      - cursor: used in paging
      - limit: the desired number of results to include

    Note that receipts older than 90 days cannot be found. An error will be
    returned if you attempt to query past 90 days.

    Data will be yielded out in an iterable format like this::

        [
            {
                "id": "2811d1f2-de7b-4ed5-9b4b-f6e21332eafe",
                "company_id": 165819,
                "location_id": 210363,
                "pos_id": 4,
                "receipt_id": "8ae8f784-4d61-420f-bc6c-19b8406c82eb",
                "receipt_date": "2022-12-31T21:00:43+00:00",
                "net_total": 517,
                "gross_total": 517,
                "tips": 0,
                "total_receipt_discounts": 0,
                "total_item_discounts": 0,
                "external_user_id": null,
                "revenue_center": null,
                "receipt_lines": [],
                "tip_details": [],
                "status": "closed",
                "created_date": "2022-12-31T22:24:19+00:00",
                "modified_date": "2023-01-01T00:25:28+00:00"
            },
            {
                "id": "3e470209-a7e9-4ed4-8e73-28538f42a89d",
                "company_id": 165819,
                "location_id": 210363,
                "pos_id": 4,
                "receipt_id": "37b0f237-e779-45e3-a8a6-0c82cba931fa",
                "receipt_date": "2022-12-31T21:01:54+00:00",
                "net_total": 3729,
                "gross_total": 3729,
                "tips": 0,
                "total_receipt_discounts": 0,
                "total_item_discounts": 0,
                "external_user_id": null,
                "revenue_center": null,
                "receipt_lines": [],
                "tip_details": [],
                "status": "closed",
                "created_date": "2022-12-31T22:24:19+00:00",
                "modified_date": "2023-01-01T00:25:28+00:00"
            }
        ]

    """
    return base.page_api_get_results(
        client, ENDPOINT.format(company_id=company_id), **kwargs)


def create_receipt(client, company_id, **kwargs):
    """Creates a sales receipt in the 7shifts API.

    Implements the API as outlined here:
    https://developers.7shifts.com/reference/createcompletereceipt

    See the above documentation for a complete list of kwarg parameters.

    Returns a 7shifts UUID for the newly created receipt.
    """
    response = client.create(
        ENDPOINT.format(company_id=company_id), body=kwargs)
    return response['uuid']


def update_receipt(client, company_id, receipt_id, **kwargs):
    """Update an sale total for an existing receipt by ID.
    company_id and receipt_id must match the original receipt, and are
    mandatory fields. Several receipt fields can be updated, see the following
    documentation for a full list of fields that can be passed in as kwargs:

    https://developers.7shifts.com/reference/updatecompletereceipt

    Returns the API status dictionary directly. The status dictionary has
    these top-level keys:

    - object: The full receipt object
    - data: includes two sub-keys:
        - uuid: UUID for the accepted receipt
        - receipt_id: external ID (receipt_id) for the accepted receipt

    """
    response = client.update(
        ENDPOINT.format(company_id=company_id), receipt_id,
        body=kwargs)
    return response
