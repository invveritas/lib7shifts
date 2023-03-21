"Test the dates module. This file only has partial coverage right now."
import unittest
from unittest.mock import patch
import datetime
from lib7shifts.dates import *

#: This TZ is used for testing anytime the "Current" timezone should be used
TEST_TZ1 = datetime.timezone(-datetime.timedelta(hours=8), name='TestTZ1')

#: This TZ is used when creating DT objects that are TZ aware
TEST_TZ2 = datetime.timezone(-datetime.timedelta(hours=7), name='TestTZ2')

#: This TZ is used when testing zulu timezones (GMT/UTC offset 00:00)
TEST_TZ3 = datetime.timezone(datetime.timedelta(hours=0), name='ZuluTC')


class TestDateUtils(unittest.TestCase):

    @patch('lib7shifts.dates.get_local_tz')
    def test_iso8601_dt(self, mock_get_local_tz):
        dt_obj = datetime.datetime(
            year=1999, month=9, day=1, hour=7, minute=11, second=33,
            microsecond=392)
        mock_get_local_tz.return_value = TEST_TZ1
        # right now the dt_obj is tz-unaware, look for TZ1 timezone
        self.assertEqual(iso8601_dt(dt_obj), '1999-09-01T15:11:33Z')
        dt_obj = dt_obj.replace(tzinfo=TEST_TZ2)
        # now we should see TZ2 timezone
        self.assertEqual(iso8601_dt(dt_obj), '1999-09-01T14:11:33Z')
        dt_obj = dt_obj.replace(tzinfo=TEST_TZ3)
        self.assertEqual(iso8601_dt(dt_obj), '1999-09-01T07:11:33Z')
        with self.assertRaises(AssertionError):
            iso8601_dt('1999-04-10')


if __name__ == '__main__':
    unittest.main()
