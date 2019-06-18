7shifts Tools
=============

A library for interacting with the 7shifts REST API in Python3.

Before using this API, it's a good idea to get familiarized with 7shifts itself
and then read the API documentation, here:

https://www.7shifts.com/partner-api

This library currently implements read operations only, but it
can be extended to implement all API operations relatively easily.

Object Model
------------
This is object-oriented code. All of the
objects in lib7shifts are designed to mimic the API object representations
exactly, that is to say that they have the same attributes and generally the
same types (except date fields, which are always converted to datetime objects).

Each object is a thin wrapper around the underlying dictionary data provided by
the API, but many have methods to make programming workflows simpler.

For example, objects that have a user_id attribute embedded within them also
have a `get_user()` method, which returns a :class:`lib7shifts.users.User`
representation of the user, which in turn has convenience methods for fetching
company data, and so on.

Get An API Client
-----------------
Before you can do anything, you need to obtain and authenticate an API client
of type :class:`lib7shifts.APIClient`, with the :meth:`lib7shifts.get_client`
method, as follows::

    import lib7shifts
    api_key = 'YOURAPIKEYHERE'
    client = lib7shifts.get_client(api_key)

Departments
-----------
Here's an example of looping over a list of departments to print their name and
ID number::

    from lib7shifts.departments import list_departments
    for department in list_departments(client=client):
      print("{:8d}: {}".format(department.id, department.name))

Shifts
------
Shifts have two different read-based methods - `get_shift` and `list_shifts`.
The get-based method is designed to find a shift based on a specified ID,
whereas the list method finds all the shifts matching specified criteria. For
example, here's how we find all the shifts for the user with ID 1000::

    from lib7shifts.shifts import list_shifts
    for shift in list_shifts(user_id=1000, client=client):
        print(shift)

Note the we are printing a :class:`lib7shifts.shifts.Shift` object in the for
loop. Each object representation is designed to have a convenient string
representation, with the fallback being a dict-style print of the object.

Time Punches
------------
This is a quick example of looping over time punches for a specific period::

    from lib7shifts.time_punch import list_punches
    for punch in list_punches(**{'clocked_in[gte]':'2019-06-10'}, client=client):
        print("{:8d} From:{} To:{} User ID: {}".format(
            punch.id, punch.clocked_in, punch.clocked_out, punch.user_id))

This example uses 7shifts `clocked_in[gte]` parameter to find all the punches
where the user clocked in on 2019-06-10 at 12am or later.
