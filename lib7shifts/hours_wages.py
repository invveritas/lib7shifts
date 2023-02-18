"""
Implements the hours_and_wages API endpoint as described here:

https://developers.7shifts.com/reference/gethoursandwages

The hours and wages report looks like this::

        {
            "users": [
                {
                    "user": {
                        "id": 112233,
                        "employee_id": "",
                        "first_name": "James 007",
                        "last_name": "Bond"
                    },
                    "weeks": [
                        {
                            "week": "2022-07-03",
                            "salaried": false,
                            "shifts": [
                                {
                                    "user_id": 112233,
                                    "date": "2022-07-03 09:03:00",
                                    "week_label": "2022-07-03",
                                    "day_label": "Jul 3",
                                    "label": "9:03AM - 3:06PM",
                                    "breaks": [
                                        "Paid Break - 30 min (7:00pm - 7:30pm)"
                                    ],
                                    "location_id": 9876,
                                    "location_label": "Restaurant",
                                    "role_id": 4320,
                                    "role_label": "Host",
                                    "wage": 2.13,
                                    "status": 0,
                                    "salaried": false,
                                    "compliance_exceptions": [],
                                    "total": {
                                        "regular_hours": 6.05,
                                        "regular_pay": 12.89,
                                        "overtime_hours": 0,
                                        "overtime_pay": 0,
                                        "holiday_hours": 0,
                                        "holiday_pay": 0,
                                        "compliance_exceptions_pay": 0,
                                        "total_hours": 6.05,
                                        "total_pay": 12.89,
                                        "total_tips": 39.24,
                                        "cash_tips": 39.24,
                                        "credit_card_tips": 0,
                                        "total_payment_tips": 0,
                                        "auto_gratuity": 0,
                                        "withheld_cc_amount": 0,
                                        "tip_in": 0,
                                        "tip_out": 0,
                                        "earned_tips": 39.24,
                                        "declared_tips": 39.24,
                                        "pos_declared_tips": 0
                                    }
                                }
                            ],
                            "lone_compliance_exceptions": [],
                            "total": {
                                "regular_hours": 6.05,
                                "regular_pay": 12.89,
                                "overtime_hours": 0,
                                "overtime_pay": 0,
                                "holiday_hours": 0,
                                "holiday_pay": 0,
                                "compliance_exceptions_pay": 0,
                                "total_hours": 6.05,
                                "total_pay": 12.89,
                                "total_tips": 39.24,
                                "cash_tips": 39.24,
                                "credit_card_tips": 0,
                                "total_payment_tips": 0,
                                "auto_gratuity": 0,
                                "withheld_cc_amount": 0,
                                "tip_in": 0,
                                "tip_out": 0,
                                "earned_tips": 39.24,
                                "declared_tips": 39.24,
                                "pos_declared_tips": 0
                            }
                        }
                    ],
                    "roles": [
                        {
                            "role_id": 4320,
                            "role_label": "Host",
                            "total": {
                                "regular_hours": 6.05,
                                "regular_pay": 12.89,
                                "overtime_hours": 0,
                                "overtime_pay": 0,
                                "holiday_hours": 0,
                                "holiday_pay": 0,
                                "compliance_exceptions_pay": 0,
                                "total_hours": 6.05,
                                "total_pay": 12.89,
                                "total_tips": 39.24,
                                "cash_tips": 39.24,
                                "credit_card_tips": 0,
                                "total_payment_tips": 0,
                                "auto_gratuity": 0,
                                "withheld_cc_amount": 0,
                                "tip_in": 0,
                                "tip_out": 0,
                                "earned_tips": 39.24,
                                "declared_tips": 39.24,
                                "pos_declared_tips": 0
                            },
                            "location_label": "Cardos Pub - OG"
                        }
                    ],
                    "total": {
                        "regular_hours": 6.05,
                        "regular_pay": 12.89,
                        "overtime_hours": 0,
                        "overtime_pay": 0,
                        "holiday_hours": 0,
                        "holiday_pay": 0,
                        "compliance_exceptions_pay": 0,
                        "total_hours": 6.05,
                        "total_pay": 12.89,
                        "total_tips": 39.24,
                        "cash_tips": 39.24,
                        "credit_card_tips": 0,
                        "total_payment_tips": 0,
                        "auto_gratuity": 0,
                        "withheld_cc_amount": 0,
                        "tip_in": 0,
                        "tip_out": 0,
                        "earned_tips": 39.24,
                        "declared_tips": 39.24,
                        "pos_declared_tips": 0
                    },
                    "salaried": false
                }
            ],
            "show_exception_costs": true,
            "tip_tracking_enabled": false,
            "show_tips": true,
            "total": {
                "regular_hours": 6.05,
                "regular_pay": 12.89,
                "overtime_hours": 0,
                "overtime_pay": 0,
                "holiday_hours": 0,
                "holiday_pay": 0,
                "compliance_exceptions_pay": 0,
                "total_hours": 6.05,
                "total_pay": 12.89,
                "total_tips": 39.24,
                "cash_tips": 39.24,
                "credit_card_tips": 0,
                "total_payment_tips": 0,
                "auto_gratuity": 0,
                "withheld_cc_amount": 0,
                "tip_in": 0,
                "tip_out": 0,
                "earned_tips": 39.24,
                "declared_tips": 39.24,
                "pos_declared_tips": 0
            },
            "start": "2022-07-03",
            "end": "2022-07-09"
        }

"""
ENDPOINT = '/v2/reports/hours_and_wages'


def get_hours_and_wages_report(client, **kwargs):
    """Gets the hours and wages report from 7shifts and returns it in full.

    Supports the following kwargs:

    - punches: boolean - whether or not to use punch data source [required]
    - company_id: the company to pull data for [required]
    - from: YYYY-MM-DD format for starting date [required]
    - to: YYYY-MM-DD format for end date of the report [required]
    - location_id: narrow to a particular location
    - department_id: narrow to a particular department
    - role_id: narrow to a particular role
    - user_id: narrow to a partciular user

    From the 7shifts documentation::

            The Hours & Wages reports can take a significant amount of time to
            create and can result in 500 errors due to time outs. If you
            receive a 500 or 502 error it is recommended to add filters to
            limit the scope of the report.

            It is recommended to always include a location_id to minimize the
            number of locations in the report. If you still receive a time out
            error, it is recommended to shorten the report period to a single
            week.

    """
    return client.get_endpoint(ENDPOINT, fields=kwargs)
