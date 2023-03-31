"""TcEx Framework Module"""
# standard library
import re

# third-party
import pytest
from arrow import Arrow

# first-party
from tcex.util.datetime_operation import DatetimeOperation


class TestDatetimeOperation:
    """Test Suite"""

    datetime_operations = DatetimeOperation()

    @pytest.mark.parametrize(
        'datetime_expression,tz,expected',
        [
            (1229084481, 'US/Eastern', r'2008-12-12T07:21:21-05:00'),
            ('1229084481', 'US/Central', r'2008-12-12T06:21:21-06:00'),
            (1229084481.298753, 'America/New_York', r'2008-12-12T07:21:21.298753-05:00'),
            ('2017 11 08', 'UTC', r'2017-11-08T00:00:00\+00:00'),
            ('2017-11-08T16:52:42Z', None, r'2017-11-08T16:52:42\+00:00'),
            ('2017-11-08 12:52:42-04:00', 'US/Eastern', r'2017-11-08T11:52:42-05:00'),
            (1556643600000, None, r'2019-04-30T17:00:00\+00:00'),
        ],
    )
    def test_any_to_datetime(self, datetime_expression: int | str, tz: str, expected: str):
        """Test Case"""
        dt = self.datetime_operations.any_to_datetime(datetime_expression, tz)
        if not re.match(expected, dt.isoformat()):
            assert False, (
                f'output: {dt.isoformat()} <-> expected: {expected} | '
                f'input-expression: {datetime_expression}, input-tz: {tz}, '
            )

    def test_arrow(self):
        """Test Case - coverage testing"""
        assert self.datetime_operations.arrow is not None

    @pytest.mark.parametrize(
        'start_date,end_date,chunk_size,chunk_unit,date_format,expected',
        [
            (
                1229084481,
                1229184481,
                1,
                'days',
                '%Y-%m-%dT%H:%M:%S.%f%z',
                [
                    ('2008-12-12T12:21:21.000000+0000', '2008-12-13T12:21:21.000000+0000'),
                    ('2008-12-13T12:21:21.000000+0000', '2008-12-13T16:08:01.000000+0000'),
                ],
            ),
        ],
    )
    def test_chunk_date_range(
        self,
        start_date: int | str,
        end_date: int | str,
        chunk_size: int,
        chunk_unit: str,
        date_format: str | None,
        expected: str,
    ):
        """Test Case"""
        chunked_dates: list[tuple[Arrow | str, Arrow | str]] = list(
            self.datetime_operations.chunk_date_range(
                start_date, end_date, chunk_size, chunk_unit, date_format
            )
        )
        assert chunked_dates == expected

    @pytest.mark.parametrize(
        'time_input1,time_input2,expected',
        [
            (
                1329084481,
                1229084481,
                {
                    'datetime_1': '2012-02-12T22:08:01+00:00',
                    'datetime_2': '2008-12-12T12:21:21+00:00',
                    'years': 3,
                    'months': 2,
                    'weeks': 0,
                    'days': 0,
                    'hours': 9,
                    'minutes': 46,
                    'seconds': 40,
                    'microseconds': 0,
                    'total_months': 38,
                    'total_weeks': 308,
                    'total_days': 1157,
                    'total_hours': 27777,
                    'total_minutes': 1666666,
                    'total_seconds': 100000000,
                    'total_microseconds': 100000000000,
                },
            ),
        ],
    )
    def test_timedelta(self, time_input1: int | str, time_input2: int | str, expected: str):
        """Test Case"""
        td = self.datetime_operations.timedelta(time_input1, time_input2)
        assert td == expected

    @pytest.mark.parametrize(
        'arrow_dt,tz,expected',
        [('2023-03-05T13:44:44.194792+00:00', 'US/Eastern', '2023-03-05T08:44:44.194792-05:00')],
    )
    def test__convert_timezone(self, arrow_dt: str, tz: str, expected: str):
        """Test Case - coverage testing"""
        dt = self.datetime_operations.arrow.get(arrow_dt)
        dt_expected = self.datetime_operations.arrow.get(expected)

        dt1 = self.datetime_operations._convert_timezone(dt, tz)
        assert dt1 == dt_expected

    def test___parse_humanized_input(self):
        """Test Case - coverage testing"""
        # TODO: [low] - fix this test
        dt = self.datetime_operations._parse_humanized_input('now')
        assert dt is not None
