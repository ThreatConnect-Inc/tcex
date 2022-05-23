"""TcEx Utilities Datetime Operations Module"""
# standard library
from datetime import datetime
from typing import Any, Optional, Tuple, Union

# third-party
import arrow as _arrow
from dateutil import parser
from dateutil.relativedelta import relativedelta


class DatetimeOperations:
    """TcEx Utilities Datetime Operations Class"""

    @classmethod
    def any_to_datetime(cls, datetime_expression: str, tz: Optional[str] = None) -> '_arrow.Arrow':
        """Return a arrow object from datetime expression.

        Args:
            datetime_expression: the datetime expression to parse into an Arrow datetime object.

            tz: if provided, the parsed Arrow datetime object will be converted to the timezone
            resulting from this timezone expression. Accepts values like 'US/Pacific', '-07:00',
            'UTC'.
            When this parameter is None, the returned Arrow datetime object will retain
            its timezone information if datetime_expression is timezone-aware. If
            datetime_expression is not timezone-aware, then the returned Arrow datetime object
            will have UTC timezone info.
        """
        value = str(datetime_expression)

        # note: order matters. For example, _parse_timestamp could parse inputs that would have
        # been meant for one of the default parser formats
        parser_methods = [
            cls._parse_default_arrow_formats,
            cls._parse_non_default_arrow_formats,
            cls._parse_timestamp,
            cls._parse_humanized_input,
            cls._parse_date_utils,
        ]

        for method in parser_methods:
            try:
                parsed = method(value)
            except Exception:  # nosec
                # value could not be parsed by current method.
                pass
            else:
                # convert timezone if tz arg provided, else return parsed object
                return cls._convert_timezone(parsed, tz) if tz is not None else parsed

        raise RuntimeError(
            f'Value "{value}" of type "{type(datetime_expression)}" '
            'could not be parsed as a date time object.'
        )

    @property
    def arrow(self):
        """Return arrow for use in Apps."""
        return _arrow

    def chunk_date_range(
        self,
        start_date: Union[int, str, datetime, '_arrow.Arrow'],
        end_date: Union[int, str, datetime, '_arrow.Arrow'],
        chunk_size: int,
        chunk_unit: Optional[str] = 'months',
        date_format: Optional[str] = None,
    ) -> Tuple[Union['_arrow.Arrow', str], Union['_arrow.Arrow', str]]:
        """Chunk a date range based on unit and size

        Args:
            start_date: Date time expression or datetime object.
            end_date: Date time expression or datetime object.
            chunk_size: Chunk size for the provided units.
            chunk_unit: A value of year, quarter, month, day, week, hour, minute, second (plural
            versions of valid values also acceptable)
            date_format: If None datetime object will be returned. Any other value
                must be a valid strftime format (%s for epoch seconds).

        Returns:
            Tuple[Union[arrow.Arrow, str], Union[arrow.Arrow, str]]: Either a datetime object
                or a string representation of the date.
        """
        start_date = self.any_to_datetime(start_date)
        end_date = self.any_to_datetime(end_date)
        interval_args = {
            'frame': chunk_unit,
            'start': start_date,
            'end': end_date,
            'interval': chunk_size,
            'bounds': '[]',
            'exact': True,
        }

        try:
            for range_tuple in _arrow.Arrow.interval(**interval_args):
                if date_format is not None:
                    yield range_tuple[0].strftime(date_format), range_tuple[1].strftime(date_format)
                else:
                    yield range_tuple
        except Exception as ex:
            raise RuntimeError(
                'Could not generate date range. Please verify that chunk_size, chunk_unit, '
                'and date_format values are valid.'
            ) from ex

    def timedelta(self, time_input1: str, time_input2: str) -> dict:
        """Calculate the time delta between two time expressions.

        Args:
            time_input1: The time input string (see formats above).
            time_input2: The time input string (see formats above).

        Returns:
            (dict): Dict with delta values.
        """
        time_input1: datetime = self.any_to_datetime(time_input1).datetime
        time_input2: datetime = self.any_to_datetime(time_input2).datetime

        diff = time_input1 - time_input2  # timedelta
        delta: object = relativedelta(time_input1, time_input2)  # relativedelta

        # totals
        total_months = (delta.years * 12) + delta.months
        total_weeks = (delta.years * 52) + (total_months * 4) + delta.weeks
        total_days = diff.days  # handles leap days
        total_hours = (total_days * 24) + delta.hours
        total_minutes = (total_hours * 60) + delta.minutes
        total_seconds = (total_minutes * 60) + delta.seconds
        total_microseconds = (total_seconds * 1000) + delta.microseconds
        return {
            'datetime_1': time_input1.isoformat(),
            'datetime_2': time_input2.isoformat(),
            'years': delta.years,
            'months': delta.months,
            'weeks': delta.weeks,
            'days': delta.days,
            'hours': delta.hours,
            'minutes': delta.minutes,
            'seconds': delta.seconds,
            'microseconds': delta.microseconds,
            'total_months': total_months,
            'total_weeks': total_weeks,
            'total_days': total_days,
            'total_hours': total_hours,
            'total_minutes': total_minutes,
            'total_seconds': total_seconds,
            'total_microseconds': total_microseconds,
        }

    @classmethod
    def _convert_timezone(cls, arrow_dt: '_arrow.Arrow', tz: str):
        """Convert Arrow datetime's timezone

        Args:
            arrow_dt: Arrow datetime object that will have its timezone converted
            tz: timezone expression. Accepts values like 'US/Pacific', '-07:00', 'UTC'.
        """
        try:
            return arrow_dt.to(tz)
        except Exception as ex:
            raise RuntimeError(
                f'Could not convert datetime to timezone "{tz}". Please verify timezone input.'
            ) from ex

    @staticmethod
    def _parse_default_arrow_formats(value: Any) -> '_arrow.Arrow':
        """Attempt to parse value using default Arrow formats.

        The value is simply passed into Arrow's "get" method. The following are the default
        date formats (found in arrow.parser.DateTimeParser.parse_iso):

        "YYYY-MM-DD",
        "YYYY-M-DD",
        "YYYY-M-D",
        "YYYY/MM/DD",
        "YYYY/M/DD",
        "YYYY/M/D",
        "YYYY.MM.DD",
        "YYYY.M.DD",
        "YYYY.M.D",
        "YYYYMMDD",
        # Year-Day-of-year: 2020-364 == 2020-12-29T00:00:00+00:00
        "YYYY-DDDD",
        # same as above, but without separating dash
        "YYYYDDDD",
        "YYYY-MM",
        "YYYY/MM",
        "YYYY.MM",
        "YYYY",
        # ISO week date: 2011-W05-4, 2019-W17
        "W"
        """
        return _arrow.get(value)

    @staticmethod
    def _parse_humanized_input(value: Any) -> '_arrow.Arrow':
        """Attempt to dehumanize time inputs. Example: 'Two hours ago'."""
        now = _arrow.utcnow()
        plurals = {
            'second': 'seconds',
            'minute': 'minutes',
            'hour': 'hours',
            'day': 'days',
            'week': 'weeks',
            'month': 'months',
            'year': 'years',
        }

        value = value.lower().strip()
        if value == 'now':
            return now

        # pluralize singular time terms as applicable. Arrow does not support singular terms
        terms = [plurals.get(term, term) for term in value.split()]
        value = ' '.join(terms)

        return now.dehumanize(value)

    @staticmethod
    def _parse_non_default_arrow_formats(value: Any) -> '_arrow.Arrow':
        """Attempt to parse value using non-default Arrow formats

        These are formats that Arrow provides constants for but are not used in the "get"
        method (Arrow method that parses values into datetimes) by default.

        Note: passing formats to test against overrides the default formats. Defaults are not used.
        """
        return _arrow.get(
            value,
            [
                _arrow.FORMAT_ATOM,
                _arrow.FORMAT_COOKIE,
                _arrow.FORMAT_RFC822,
                _arrow.FORMAT_RFC850,
                _arrow.FORMAT_RFC1036,
                _arrow.FORMAT_RFC1123,
                _arrow.FORMAT_RFC2822,
                _arrow.FORMAT_RFC3339,
                _arrow.FORMAT_RSS,
                _arrow.FORMAT_W3C,
            ],
        )

    @staticmethod
    def _parse_timestamp(value: Any) -> '_arrow.Arrow':
        """Attempt to parse epoch timestamp in seconds, milliseconds, or microseconds.

        Note: passing formats to test against overrides the default formats. Defaults are not used.
        """
        # note: order matters. Must try to parse as milliseconds/microseconds first (x)
        # before trying to parse as seconds (X), else error occurs if passing a ms/ns value
        try:
            # attempt to parse as string first using microsecond/millisecond and second specifiers
            return _arrow.get(value, ['x', 'X'])
        except (_arrow.parser.ParserError, ValueError):
            # could not parse as string, try to parse as float
            return _arrow.get(float(value))

    @staticmethod
    def _parse_date_utils(value: Any) -> '_arrow.Arrow':
        """Attempt to supplement arrows parsing ability with dateutils.

        Arrow doesn't support RFC_5322 used in HTTP 409 headers
        """
        return _arrow.get(parser.parse(value))
