"""
API methods to access the daily_sales_and_labour API endpoint. See the
following for more details:

https://developers.7shifts.com/reference/getdailysalesandlabor
"""
ENDPOINT = '/v2/reports/daily_sales_and_labor'


def get_daily_sales_and_labor(client, **params):
    """Make an API call against the daily_sales_and_labour endpoint for the
    given date range and return sales and labour data in dictionary form
    (rather than an object).

    Supported kwargs:

    - start_date: YYYY-MM-DD format, the start of a sales period [required]
    - end_date: YYYY-MM-DD format, end of the sales period [required]
    - location_id: a numeric id for the location in question [required]
    - department_id: a numeric department id for narrower results [optional]

    Returns a list of dictionaries like this::

        [
            {
                "date": "2023-01-01",
                "actual_sales": 473313,
                "projected_sales": 331330,
                "actual_labor_cost": 23527,
                "projected_labor_cost": 0,
                "sales_per_labor_hour": 17894.631379962193,
                "labor_percent": 0.04970706488095615
            },
            {
                "date": "2023-01-02",
                "actual_sales": 234289,
                "projected_sales": 0,
                "actual_labor_cost": 21549,
                "projected_labor_cost": 0,
                "sales_per_labor_hour": 8608.291488058789,
                "labor_percent": 0.09197614911498192
            }
        ]

    """
    if 'start_date' not in params:
        raise RuntimeError('No start_date in params (required)')
    if 'end_date' not in params:
        raise RuntimeError('No end_date in params (required)')
    if 'location_id' not in params:
        raise RuntimeError('No location_id in params (required)')
    response = client.get_endpoint(ENDPOINT, fields=params)
    return response['data']
