# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""
import operator
import re
from datetime import datetime, timedelta

import pytz
import pytest


# pylint: disable=no-self-use
class TestUtils:
    """Test the TcEx Utils Module."""

    @pytest.mark.parametrize(
        'date,tz,results',
        [
            (1229084481, 'US/Eastern', r'2008-12-12T07:21:21-05:00'),
            ('1229084481', 'US/Central', r'2008-12-12T06:21:21-06:00'),
            (1229084481.298753, 'America/New_York', r'2008-12-12T07:21:21.298753-05:00'),
            ('2017 11 08', 'UTC', r'2017-11-08T06:00:00\+00:00'),
            ('2017-11-08T16:52:42Z', None, r'2017-11-08T16:52:42\+00:00'),
            ('2017-11-08 12:52:42-04:00', 'US/Eastern', r'2017-11-08T11:52:42-05:00'),
            (1556643600000, None, r'2019-04-30T17:00:00\+00:00'),
            # (
            #     'in 1 month',
            #     'US/Central',
            #     {
            #         'operator': operator.add,
            #         'strftime': '%Y-%m-%dT%H:%M',
            #         'timedelta': {'days': 30}},
            # ),
        ],
    )
    def test_utils_datetime_any_to_datetime(self, tcex, date, tz, results):
        """Test **any_to_datetime** method of TcEx Utils datetime module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            date (str): The input datetime expression.
            tz (str, Optional): The timezone value as a string.
            results (dict,str): The expected results.
        """
        if isinstance(results, dict):
            results = results.get('operator')(
                datetime.now().astimezone(pytz.timezone(tz)), timedelta(**results.get('timedelta'))
            ).strftime(results.get('strftime'))

        dt = tcex.utils.datetime.any_to_datetime(date, tz)
        if not re.match(results, dt.isoformat()):
            assert False, f'Input: {date}, Output: {dt.isoformat()}, Expected: {results}'

    @staticmethod
    def test_utils_datetime_any_to_datetime_fail(tcex):
        """Test failure handling of **any_to_datetime** method of TcEx Utils datetime module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        try:
            tcex.utils.datetime.any_to_datetime('abc')
            assert False
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'date,tz,results',
        [
            ('2019-09-25T10:49:41.5-03:00', 'US/Eastern', r'2019-09-25T09:49:41.500000-04:00'),
            ('2019-11-08T16:52:42Z', 'US/Eastern', r'2019-11-08T11:52:42-05:00'),
            ('2019 11 08', 'US/Eastern', r'2019-11-08T'),
            ('2019-01-19 17:21:00', None, r'2019-01-19T17:21:00'),
            ('2019-01-19 17:21:00 CST', None, r'2019-01-19T17:21:00'),
            ('2019 10:36:28 25 Sep Thu', None, r'2019-09-25T10:36:28'),
            ('Sat Oct 11 17:13:46 UTC 2003', 'US/Eastern', r'2003-10-11T13:13:46-04:00'),
            ('Thu Sep 25 10:36:28 2003', None, r'2003-09-25T10:36:28'),
            ('Thu Sep 25 10:36:28', None, r'2020-09-25T10:36:28'),
            # only supported with fuzzy_with_tokens
            # ('Today is January 1, 2047 at 8:21:00AM', None, '2047-01-01 08:21:00'),
        ],
    )
    def test_utils_datetime_date_to_datetime(self, tcex, date, tz, results):
        """Test **date_to_datetime** method of TcEx Utils datetime module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            date (str): The input datetime expression.
            tz (str, Optional): The timezone value as a string.
            results (dict,str): The expected results.
        """
        dt = tcex.utils.datetime.date_to_datetime(time_input=date, tz=tz)
        if not re.match(results, dt.isoformat()):
            assert False, f'Input: {date}, Output: {dt.isoformat()}, Expected: {results}'

    @pytest.mark.parametrize(
        'date,tz,date_format,results',
        [
            (1229084481, 'US/Eastern', '%s', r'1229066481'),
            ('1229084481', 'US/Central', None, r'2008-12-12T06:21:21-06:00'),
            (1229084481.298753, 'America/New_York', r'%Y-%m-%dT%H:%M:%SZ', '2008-12-12T07:21:21Z'),
            ('2017 11 08', 'UTC', '%Y-%m-%dT%H:%M:%S.%fZ', r'2017-11-08T06:00:00.000000Z'),
            ('2017-11-08T16:52:42Z', None, None, r'2017-11-08T16:52:42\+00:00'),
            ('2017-11-08 12:52:42-04:00', 'US/Eastern', '%s', r'1510141962'),
            # (
            #     'in 1 month',
            #     'US/Central',
            #     r'%Y-%m-%d',
            #     {'operator': operator.add, 'strftime': '%Y-%m-%d', 'timedelta': {'days': 30}},
            # ),
            ('now', 'UTC', '%Y-%m-%dT%H:%M:%S', r'20[0-9]{2}-[0-9]{2}-[0-9]{2}'),
        ],
    )
    def test_utils_datetime_format_datetime(self, tcex, date, tz, date_format, results):
        """Test **format_datetime** method of TcEx Utils datetime module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            date (str): The input datetime expression.
            tz (str, Optional): The timezone value as a string.
            date_format (str, Optional): The strftime format for the date.
            results (dict,str): The expected results.
        """
        if isinstance(results, dict):
            results = results.get('operator')(
                datetime.now().astimezone(pytz.timezone(tz)), timedelta(**results.get('timedelta'))
            ).strftime(results.get('strftime'))

        dt = tcex.utils.datetime.format_datetime(time_input=date, tz=tz, date_format=date_format)
        if not re.match(results, str(dt)):
            assert False, f'Input: {date}, Output: {dt}, Expected: {results}'

    @pytest.mark.parametrize(
        'date,tz,results',
        [
            (
                'August 25th, 2008',
                'UTC',
                {
                    'operator': operator.add,
                    'strftime': r'2008-08-2[0-9]T',
                    'timedelta': {'days': 1},
                },
            ),
            (
                '25 Aug 2008',
                'UTC',
                {
                    'operator': operator.add,
                    'strftime': r'2008-08-2[0-9]T',
                    'timedelta': {'days': 1},
                },
            ),
            (
                'Aug 25 5pm',
                'UTC',
                {
                    'operator': operator.add,
                    'strftime': '%Y-08-25T22:00:00',
                    'timedelta': {'days': 1},
                },
            ),
            (
                '5pm August 25',
                'UTC',
                {
                    'operator': operator.add,
                    'strftime': '%Y-08-25T22:00:00',
                    'timedelta': {'days': 1},
                },
            ),
            (
                'tomorrow',
                'UTC',
                {'operator': operator.add, 'strftime': '%Y-%m-[0-9]{2}T', 'timedelta': {'days': 1}},
            ),
            # ('next thursday at 4pm', 'UTC', '202[0-9]-[0-9]{2}-[0-9]{2}T22:00:00'),
            (
                'at 4pm',
                'UTC',
                {
                    'operator': operator.add,
                    'strftime': '%Y-%m-[0-9]{2}T[0-9]{2}:00:00',
                    'timedelta': {},
                },
            ),
            (
                'eod',
                'UTC',
                {
                    'operator': operator.add,
                    'strftime': '%Y-%m-[0-9]{2}T[0-9]{2}:00:00',
                    'timedelta': {},
                },
            ),
            (
                'tomorrow eod',
                'UTC',
                {
                    'operator': operator.add,
                    'strftime': '%Y-%m-[0-9]{2}T[0-9]{2}:00:00',
                    'timedelta': {'days': 1},
                },
            ),
            ('eod tuesday', 'UTC', {'operator': operator.add, 'strftime': '%Y-', 'timedelta': {}},),
            (
                'eoy',
                'UTC',
                {
                    'operator': operator.add,
                    'strftime': r'%Y-12-31T[0-9]{2}:00:00\+00:00',
                    'timedelta': {},
                },
            ),
            ('eom', 'UTC', {'operator': operator.add, 'strftime': '%Y-%m-', 'timedelta': {}},),
            (
                'in 5 minutes',
                'UTC',
                {
                    'operator': operator.add,
                    'strftime': '%Y-%m-%dT%H:%M:%S',
                    'timedelta': {'minutes': 5},
                },
            ),
            (
                '5 minutes from now',
                'UTC',
                {
                    'operator': operator.add,
                    'strftime': '%Y-%m-%dT%H:%M:%S',
                    'timedelta': {'minutes': 5},
                },
            ),
            (
                '5 hours before now',
                'UTC',
                {
                    'operator': operator.sub,
                    'strftime': '%Y-%m-%dT%H:%M:%S',
                    'timedelta': {'hours': 5},
                },
            ),
            (
                '2 hours before noon',
                'UTC',
                {'operator': operator.add, 'strftime': '%Y-%m-[0-9]{2}T', 'timedelta': {}},
            ),
            (
                '2 days from tomorrow',
                'UTC',
                {'operator': operator.add, 'strftime': '%Y-%m-[0-9]{2}T', 'timedelta': {'days': 3}},
            ),
            # ('0', 'US/Eastern', None),
        ],
    )
    def test_utils_datetime_human_date_to_datetime(self, tcex, date, tz, results):
        """Test **human_date_to_datetime** method of TcEx Utils datetime module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            date (str): The input datetime expression.
            tz (str, Optional): The timezone value as a string.
            results (dict,str): The expected results.
        """
        if isinstance(results, dict):
            results = results.get('operator')(
                datetime.now().astimezone(pytz.timezone(tz)), timedelta(**results.get('timedelta'))
            ).strftime(results.get('strftime'))
            results = rf'{results}'

        dt = tcex.utils.datetime.human_date_to_datetime(time_input=date, tz=tz)
        if results is None:
            assert dt is None
        elif not re.match(results, dt.isoformat()):
            assert False, f'Input: {date}, Output: {dt.isoformat()}, Expected: {results}'

    @staticmethod
    def test_utils_datetime_human_date_to_datetime_with_source(tcex):
        """Test **human_date_to_datetime** method of TcEx Utils datetime module with source.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            date (str): The input datetime expression.
            tz (str, Optional): The timezone value as a string.
            results (dict,str): The expected results.
        """
        # TODO: updated this ...
        source_datetime = datetime.now()
        dt = tcex.utils.datetime.human_date_to_datetime(
            time_input='now', tz='UTC', source_datetime=source_datetime
        )
        if not re.match(
            r'^20[0-9]{2}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$',
            str(dt),
        ):
            assert False, f'Results ({str(dt)}) does not match pattern'

    @staticmethod
    def test_utils_datetime_timedelta(tcex):
        """Test **timedelta** method of TcEx Utils datetime module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        delta = tcex.utils.datetime.timedelta('2018-01-13', '2018-02-14')
        assert delta['days'] == -1
        assert delta['total_days'] == -32
        assert delta['hours'] == 0
        assert delta['total_weeks'] == -4

    @pytest.mark.parametrize(
        'date,tz,results',
        [
            ('1454944545', 'UTC', r'2016-02-08T15:15:45\+00:00'),
            ('1554944545', 'UTC', r'2019-04-11T01:02:25\+00:00'),
            ('1854944545', 'US/Eastern', r'2028-10-12T02:22:25-04:00'),
            ('1954944545.123456', 'US/Eastern', r'2031-12-13T11:09:05.123456-05:00'),
            ('1954944', 'UTC', None),
            ('0', 'UTC', None),
            (0, 'UTC', None),
            ('1556643600', None, r'2019-04-30T17:00:00\+00:00'),
            ('1556643600', None, r'2019-04-30T17:00:00\+00:00'),
            ('15566436001', None, r'2019-04-30T17:00:00.100000\+00:00'),
            ('155664360012', None, r'2019-04-30T17:00:00.120000\+00:00'),
            ('1556643600123', None, r'2019-04-30T17:00:00.123000\+00:00'),
            ('15566436001234', None, r'2019-04-30T17:00:00.123400\+00:00'),
            ('155664360012345', None, r'2019-04-30T17:00:00.123450\+00:00'),
            ('1556643600123456', None, r'2019-04-30T17:00:00.123456\+00:00'),
        ],
    )
    def test_utils_datetime_unix_time_to_datetime(self, tcex, date, tz, results):
        """Test **unix_time_to_datetime** method of TcEx Utils datetime module.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
            date (str): The input datetime expression.
            tz (str, Optional): The timezone value as a string.
            results (dict,str): The expected results.
        """
        if isinstance(results, dict):
            results = results.get('operator')(
                datetime.now().astimezone(pytz.timezone(tz)), timedelta(**results.get('timedelta'))
            ).strftime(results.get('strftime'))
            results = rf'{results}'

        dt = tcex.utils.datetime.unix_time_to_datetime(time_input=date, tz=tz)
        if results is None:
            assert dt is None
        elif not re.match(results, dt.isoformat()):
            assert False, f'Input: {date}, Output: {dt.isoformat()}, Expected: {results}'
