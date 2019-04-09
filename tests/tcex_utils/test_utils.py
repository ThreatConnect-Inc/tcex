# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""

import pytest

from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestUtils:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""
        # self.tcex = test()

    @pytest.mark.parametrize(
        'date,tz,results',
        [
            (1229084481, 'US/Eastern', '2008-12-12T07:21:21-05:00'),
            ('1229084481', 'US/Central', '2008-12-12T06:21:21-06:00'),
            (1229084481.298753, 'America/New_York', '2008-12-12T07:21:21.298753-05:00'),
            ('2017 11 08', 'UTC', '2017-11-08T05:51:00+00:00'),
            ('2017-11-08T16:52:42Z', None, '2017-11-08T16:52:42+00:00'),
            ('2017-11-08 12:52:42-04:00', 'US/Eastern', '2017-11-08T11:52:42-05:00'),
            ('in 1 month', 'US/Central', '2019-05'),
        ],
    )
    def test_any_to_datetime(self, date, tz, results):
        """Test any to datetime"""
        dt = tcex.utils.any_to_datetime(date, tz)
        assert dt.isoformat().startswith(results)

    @pytest.mark.parametrize(
        'date,tz,date_format,results',
        [
            (1229084481, 'US/Eastern', '%s', 1229066481),
            ('1229084481', 'US/Central', None, '2008-12-12T06:21:21-06:00'),
            (1229084481.298753, 'America/New_York', '%Y-%m-%dT%H:%M:%SZ', '2008-12-12T07:21:21Z'),
            ('2017 11 08', 'UTC', '%Y-%m-%dT%H:%M:%S.%fZ', '2017-11-08T05:51:00.000000Z'),
            ('2017-11-08T16:52:42Z', None, None, '2017-11-08T16:52:42+00:00'),
            ('2017-11-08 12:52:42-04:00', 'US/Eastern', '%s', 1510141962),
            ('in 1 month', 'US/Central', '%Y-%m-%d', '2019-05'),
        ],
    )
    def test_format_datetime(self, date, tz, date_format, results):
        """Test format datetime"""
        dt = tcex.utils.format_datetime(time_input=date, tz=tz, date_format=date_format)
        assert dt.startswith(results)

    def test_timedelta(self):
        """Test timedelta module"""
        delta = tcex.utils.timedelta('2018-01-13', '2018-02-14')
        assert delta['days'] == -1
        assert delta['total_days'] == -32
        assert delta['hours'] == 0
        assert delta['total_weeks'] == -4
