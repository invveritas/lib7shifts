lib7shifts
==========

A library for interacting with the 7shifts REST API in Python3.

Before using this library, it's a good idea to be familiar with 7shifts,
itself, and read the API documentation, here:

https://www.7shifts.com/partner-api

Here's a quick example of the code usage::

    import lib7shifts
    client = lib7shifts.get_client(api_key='YOURAPIKEYHERE')
    for shift in lib7shifts.list_shifts(client, user_id=1000):
        print(shift)

Object Model
------------
This package includes modules for each of the objects represented by the 7shifts
API, including:

- Company
- Location
- Department
- Role
- User
- Shift
- TimePunch
- TimePunchBreak
- Event

The above are the object names in lib7shifts, and each object is designed to
mimic the API object representations
exactly, that is to say that they have the same attributes and generally the
same data types (except date fields, which are converted to datetime
objects). So if the API says that the ``User`` object has an attribute called
*id*, then our ``User`` class also has an attribute called *id*, and the value
is an integer. Similar for booleans, text fields, etc.

Each object is a thin wrapper around an underlying dictionary provided by
the API, but many have methods to make programming workflows simpler. For
example, objects that have a *user_id* attribute embedded within them also
have a ``get_user()`` method, which returns a ``lib7shifts.users.User``
representation of the user, which in turn has convenience methods for fetching
company data, and so on.

All of the objects above are defined in modules for each type, which is where
you want to look for documentation, but each one is imported directly into
the main package scope, so you need only to ``import lib7shifts`` to
access all of the objects programmatically.

Generally speaking, print calls on objects results in a simple dictionary
print of the underlying API data used to populate the object. Future code
improvements should bring better support for serialized object representations.

Functional Design Pattern
-------------------------
For speed and simplicity, functional
code is used for all supported CRUD operations (*Create, Read, Update and
Delete*, as well as *List*, a specialized version of *Read*). Each of the
objects listed above should have a ``create_[object]()`` function associated
with them, such as ``create_department()`` or ``create_event()``. Similarly,
read-type operations are done with ``get_`` or ``list_``
functions like ``get_user()`` and ``list_time_punches()``. You can probably
guess that delete operations start with the ``delete_`` prefix, and update
operations
start with the ``update_`` prefix. All of these functions take an
``APIClient7Shifts`` object as their first parameter, which is described in
more detail further below.

The 7shifts API supports the full gamut of CRUD operations for all object types
except users (that is probably coming). Due to time constraints, this package
doesn't yet have every CRUD operation supported for every object type, but
it is trivial to add it now (see the ``lib7shifts.events`` module for an
example of a complete CRUD implementation).

All of the CRUD functions are imported directly into the main package scope,
so you simply need to ``import lib7shifts`` to get access to all of them.

Get An API Client
-----------------
Before you can do anything, you need to obtain/initialize a
``lib7shifts.APIClient7Shifts`` object, which you generally do using the
``lib7shifts.get_client`` function, as follows::

    import lib7shifts
    client = lib7shifts.get_client(api_key='YOURAPIKEYHERE')

*APIClient7Shifts* contains the code that performs all of the
low-level API interaction, including defining the underlying methods used
in all CRUD operations, defining parameter/field encodings, etc. This class
was originally just a child of the *apiclient* library's ``APIClient``
class, but it outgrew that and now features very little in common with that
codebase, but an important feature is the ability to rate limit requests by
passing a ``apiclient.RateLimiter`` object to the client using the
``rate_limit_lock`` named parameter.

Events
------
Here's an example of a workflows to perform all CRUD operations for events::

    # CREATE
    event_id = lib7shifts.create_event(
        client, title='Some Event', description='A thing is happening',
        date='2019-06-03', start='12:00:00', color='FBAF40',
        location=[12345]) # location has to be a list

    # READ
    event = lib7shifts.get_event(client, event_id)
    print(event)
    # {'id': 664814, 'title': 'Some Event', 'description': 'A thing is happening', 'date': '2019-06-03', 'start': '12:00:00', 'all_day': False, 'color': 'FBAF40', 'created': '2019-06-20 08:34:40', 'modified': '2019-06-20 08:34:40'}

    # UPDATE
    lib7shifts.update_event(client, event.id, date='2019-06-06', title='Testing')

    # DELETE
    lib7shifts.delete_event(event.id)

    # LIST
    events = lib7shifts.list_events(client, date='2019-06-03')

Locations
---------
Here are some examples::

    # List all 7shifts locations
    for location in lib7shifts.list_locations(client):
        print(location)

    # Get a particular location
    location = lib7shifts.get_location(client, 1234)
    print(location.address)


Departments
-----------
Here's an example of looping over a list of departments to print their name and
ID number::

    for department in lib7shifts.list_departments(client):
        print("{:8d}: {}".format(department.id, department.name))

Shifts
------
Shifts have two different read-based methods - ``get_shift`` and ``list_shifts``.
The *get* method is designed to find a shift based on a specified ID,
whereas the *list* method finds all the shifts matching specified criteria. For
example, here's how we find all the shifts for the user with ID 1000::

    for shift in lib7shifts.list_shifts(client, user_id=1000):
        print(shift)

Note that we are printing a ``lib7shifts.shifts.Shift`` object in the for
loop.

Time Punches
------------
This is a quick example of looping over time punches for a specific period::

    for punch in lib7shifts.list_punches(client, **{'clocked_in[gte]':'2019-06-10'}):
        print("{:8d} From:{} To:{} User ID: {}".format(
            punch.id, punch.clocked_in, punch.clocked_out, punch.user_id))

This example uses 7shifts' *clocked_in[gte]* parameter to find all the punches
where the user clocked in on 2019-06-10 at 12am or later (in the timezone
of the company as configured in 7shifts, itself). Because Python functions
don't directly support brackets in the parameter names, you need to either
set them up as keys in a dictionary and pass in as ``**kwargs``, or you need
to use the syntax shown here to expand a dictionary into function parameters
inline.
