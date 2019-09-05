# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
from datetime import datetime
import re
import pytest


# pylint: disable=R0201,W0201
class TestUtils:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @pytest.mark.parametrize(
        'date,tz,results',
        [
            (1229084481, 'US/Eastern', '2008-12-12T07:21:21-05:00'),
            ('1229084481', 'US/Central', '2008-12-12T06:21:21-06:00'),
            (1229084481.298753, 'America/New_York', '2008-12-12T07:21:21.298753-05:00'),
            ('2017 11 08', 'UTC', '2017-11-08T06:00:00+00:00'),
            ('2017-11-08T16:52:42Z', None, '2017-11-08T16:52:42+00:00'),
            ('2017-11-08 12:52:42-04:00', 'US/Eastern', '2017-11-08T11:52:42-05:00'),
            ('in 1 month', 'US/Central', '2019-'),
            (1556643600000, None, '2019-04-30T17:00:00+00:00'),
        ],
    )
    def test_any_to_datetime(self, tcex, date, tz, results):
        """Test any to datetime"""
        dt = tcex.utils.any_to_datetime(date, tz)
        # print('(\'{}\', \'{}\', \'{}\', \'{}\')'.format(date, tz, dt.isoformat(), results))
        assert dt.isoformat().startswith(results)

    @staticmethod
    def test_any_to_datetime_fail(tcex):
        """Test any to datetime"""
        try:
            tcex.utils.any_to_datetime('abc')
            assert False
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'date,tz,results',
        [
            ('2019-09-25T10:49:41.5-03:00', 'US/Eastern', '2019-09-25 09:49:41.500000-04:00'),
            ('2019-11-08T16:52:42Z', 'US/Eastern', '2019-11-08 11:52:42-05:00'),
            ('2019 11 08', 'US/Eastern', '2019-11-08 '),
            ('2019-01-19 17:21:00', None, '2019-01-19 17:21:00'),
            ('2019-01-19 17:21:00 CST', None, '2019-01-19 17:21:00'),
            ('2019 10:36:28 25 Sep Thu', None, '2019-09-25 10:36:2'),
            ('Sat Oct 11 17:13:46 UTC 2003', 'US/Eastern', '2003-10-11 13:13:46-04:00'),
            ('Thu Sep 25 10:36:28 2003', None, '2003-09-25 10:36:2'),
            # will break in 2020
            ('Thu Sep 25 10:36:28', None, '2019-09-25 10:36:28'),
            # only supported with fuzzy_with_tokens
            # ('Today is January 1, 2047 at 8:21:00AM', None, '2047-01-01 08:21:00'),
            (0, 'US/Eastern', None),
        ],
    )
    def test_date_to_datetime(self, tcex, date, tz, results):
        """Test format datetime"""
        dt = tcex.utils.date_to_datetime(time_input=date, tz=tz)
        # print('(\'{}\', \'{}\', \'{}\', \'{}\')'.format(date, tz, dt, results))
        assert str(dt).startswith(str(results))

    @pytest.mark.parametrize(
        'date,tz,date_format,results',
        [
            (1229084481, 'US/Eastern', '%s', '1229066481'),
            ('1229084481', 'US/Central', None, '2008-12-12T06:21:21-06:00'),
            (1229084481.298753, 'America/New_York', '%Y-%m-%dT%H:%M:%SZ', '2008-12-12T07:21:21Z'),
            ('2017 11 08', 'UTC', '%Y-%m-%dT%H:%M:%S.%fZ', '2017-11-08T06:00:00.000000Z'),
            ('2017-11-08T16:52:42Z', None, None, '2017-11-08T16:52:42+00:00'),
            ('2017-11-08 12:52:42-04:00', 'US/Eastern', '%s', '1510141962'),
            ('in 1 month', 'US/Central', '%Y-%m-%d', '2019-'),
            ('now', 'UTC', '%Y-%m-%dT%H:%M:%S', '2019-'),
        ],
    )
    def test_format_datetime(self, tcex, date, tz, date_format, results):
        """Test format datetime"""
        dt = tcex.utils.format_datetime(time_input=date, tz=tz, date_format=date_format)
        # print('(\'{}\', \'{}\', \'{}\', \'{}\')'.format(date, tz, dt, results))
        # TODO: replace with regex or date calculated differently
        assert str(dt).startswith(results)

    @pytest.mark.parametrize(
        'date,tz,pattern',
        [
            (
                'August 25th, 2008',
                'UTC',
                r'^2008-08-2[5-6]\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                '25 Aug 2008',
                'UTC',
                r'^2008-08-2[5-6]\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'Aug 25 5pm',
                'UTC',
                r'^20[0-9]{2}-08-25\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),  # assumes future
            (
                '5pm August 25',
                'UTC',
                r'^20[0-9]{2}-08-25\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'next saturday',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'tomorrow',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'next thursday at 4pm',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'at 4pm',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'eod',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'tomorrow eod',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'eod tuesday',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'eoy',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'eom',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                'in 5 minutes',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                '5 minutes from now',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                '5 hours before now',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                '2 hours before noon',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            (
                '2 days from tomorrow',
                'UTC',
                r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            ),
            ('0', 'US/Eastern', None),
        ],
    )
    def test_human_date_to_datetime(self, tcex, date, tz, pattern):
        """Test format datetime"""
        dt = tcex.utils.human_date_to_datetime(time_input=date, tz=tz)
        # print('(\'{}\', \'{}\', \'{}\', \'{}\')'.format(date, tz, dt, pattern))
        if pattern is None:
            assert dt is None
        elif not re.match(pattern, str(dt)):
            assert False, 'Results ({}) does not match pattern ({})'.format(str(dt), pattern)

    @staticmethod
    def test_human_date_to_datetime_with_source(tcex):
        """Test format datetime"""
        source_datetime = datetime.now()
        dt = tcex.utils.human_date_to_datetime(
            time_input='now', tz='UTC', source_datetime=source_datetime
        )
        if not re.match(
            r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            str(dt),
        ):
            assert False, 'Results ({}) does not match pattern'.format(str(dt))

    @staticmethod
    def test_timedelta(tcex):
        """Test timedelta module"""
        delta = tcex.utils.timedelta('2018-01-13', '2018-02-14')
        assert delta['days'] == -1
        assert delta['total_days'] == -32
        assert delta['hours'] == 0
        assert delta['total_weeks'] == -4

    @pytest.mark.parametrize(
        'date,tz,results',
        [
            ('1454944545', 'UTC', '2016-02-08T15:15:45+00:00'),
            ('1554944545', 'UTC', '2019-04-11T01:02:25+00:00'),
            ('1854944545', 'US/Eastern', '2028-10-12T02:22:25-04:00'),
            ('1954944545.123456', 'US/Eastern', '2031-12-13T11:09:05.123456-05:00'),
            ('1954944', 'UTC', None),
            ('0', 'UTC', None),
            (0, 'UTC', None),
            ('1556643600', None, '2019-04-30T17:00:00+00:00'),
            ('1556643600', None, '2019-04-30T17:00:00+00:00'),
            ('15566436001', None, '2019-04-30T17:00:00.100000+00:00'),
            ('155664360012', None, '2019-04-30T17:00:00.120000+00:00'),
            ('1556643600123', None, '2019-04-30T17:00:00.123000+00:00'),
            ('15566436001234', None, '2019-04-30T17:00:00.123400+00:00'),
            ('155664360012345', None, '2019-04-30T17:00:00.123450+00:00'),
            ('1556643600123456', None, '2019-04-30T17:00:00.123456+00:00'),
        ],
    )
    def test_unix_time_to_datetime(self, tcex, date, tz, results):
        """Test unix time to datetime"""
        dt = tcex.utils.unix_time_to_datetime(time_input=date, tz=tz)
        if results is None:
            assert dt is None
        else:
            # print('(\'{}\', \'{}\', \'{}\', \'{}\')'.format(date, tz, dt.isoformat(), results))
            assert str(dt.isoformat()).startswith(str(results))
