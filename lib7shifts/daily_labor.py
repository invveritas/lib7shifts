"""
API methods to access the daily_labor API endpoint. This is not part of
the officially documented API, but it is used by the webapp to show the Sales
vs Labor dashboard to managers and administrators.

Given the undocumented nature of this API, assume that it is unsupported and
could change/go away at any time.
"""
ENDPOINT = '/v1/daily_labor'


def get_daily_labor(client, **params):
    """Make an API call against the daily_labor endpoint for the given
    parameters, and return the data in dictionary form (rather than an object).
    Required kwargs:

    - week: YYYY-MM-DD format, the start of a sales week
    - actuals: boolean, show actual vs projected/scheduled
    - location_id: a numeric id for the location in question
    - department_id: a numeric department id for narrower results
    - include_unapproved: boolean, whether or not to include unapproved labour

    NOTE: 'from' is a reserved python keyword, so it can only be passed into
          this function in **dict from.

    Returns a dictionary like this::

        "daily": [
            {
                "labor_target_percentage": 31.61,
                "labor_hours_scheduled": 101,
                "labor_cost_scheduled": 1653.75,
                "labor_hours_worked": 87.13333333333334,
                "labor_actual": 1548.65,
                "location_id": [YOUR LOCATION ID],
                "date": "2019-01-07",
                "projected_sales": 5231,
                "actual_sales": 4808.23
            }
        ],
        "weekly": 6480.218571428572,
        "labor_percentage": 0.4820006048181009


    The 'daily' section contains a list of dictionaries, with each dict
    representing a single day's data.
    """
    if params.get('include_unapproved', False):
        params['include_unapproved'] = 'true'   # api requires lower-case text
    else:
        params['include_unapproved'] = 'false'
    response = client.get_endpoint(ENDPOINT, fields=params)
    return response['data']
