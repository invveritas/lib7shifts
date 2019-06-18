7shifts Tools
=============

A library for interacting with the 7shifts REST API in Python3.

This library currently only implements read operations against the API, but
can be extended to implement all API operations quite easily.

Example usage::

    import lib7shifts
    api_key = 'YOURAPIKEYHERE'
    client = lib7shifts.get_client(api_key)

    import lib7shifts.time_punch
    tpl = lib7shifts.time_punch.list_punches(**{'clocked_in[gte]':'2019-06-10'}, client=client)
    for punch in tpl:
      print(punch)
