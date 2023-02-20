"""
Common methods and attributes for the various 7shifts commands
"""
import logging
import datetime
import json
from lib7shifts import get_client as get_7shifts_client


def print_api_item(item):
    """Pretty-print a dictionary from the API"""
    print(json.dumps(item, indent=2))


def print_api_object(item):
    """Pretty-print an object from the API client library"""
    print(json.dumps(item, indent=2))


def print_api_data(data):
    """Given a list of objects from the 7shifts API, dump them in an
    easy-to-read format (indented JSON). Returns the count of printed
    results."""
    count = 0
    try:
        for row in data:
            print_api_item(row)
            count += 1
    except TypeError:
        print_api_item(data)
        count += 1
    return count
