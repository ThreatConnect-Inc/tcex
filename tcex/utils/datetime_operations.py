"""TcEx Utilities Datetime Operations Module"""
# standard library
from datetime import datetime
from typing import Any, Optional, Tuple, Union

# third-party
import arrow
from dateutil import parser
from dateutil.relativedelta import relativedelta


class DatetimeOperations:
    """TcEx Utilities Datetime Operations Class"""

    @classmethod
    def any_to_datetime(cls, datetime_expression: str) -> 'arrow.Arrow':
        """Return a arrow object from datetime expression."""
        if isinstance(datetime_expression, arrow.Arrow):
            return datetime_expression

        value = str(datetime_expression)

        # note: order matters. For example, the timestamp could parse inputs that would have
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
                return method(value)
            # TypeError should never occur, but adding for completeness in case of improperly
            # overridden str method
            # TODO: [low] @phuerta - any reason not to just catch Exception here? are there
            #    any exception that we would want to raise for?
            except (arrow.parser.ParserError, parser.ParserError, TypeError, ValueError):
                # value could not be parsed by current method.
                pass

        raise RuntimeError(
            f'Value "{value}" of type "{type(datetime_expression)}" '
            'could not be parsed as a date time object.'
        )

    # TODO: [med] @phuerta - can this be done better with arrow
    def chunk_date_range(
        self,
        start_date: Union[int, str, datetime],
        end_date: Union[int, str, datetime],
        chunk_size: int,
        chunk_unit: Optional[str] = 'months',
        date_format: Optional[str] = None,
    ) -> Tuple[Union[datetime, str], Union[datetime, str]]:
        """Chunk a date range based on unit and size

        Args:
            start_date: Date time expression or datetime object.
            end_data: Date time expression or datetime object.
            chunk_size: Chunk size for the provided units.
            chunk_unit: A value of (years, months, days, weeks, hours, minuts, seconds)
            date_format: If None datetime object will be returned. Any other value
                must be a valid strftime format (%s for epoch seconds).

        Returns:
            Tuple[Union[datetime, str], Union[datetime, str]]: Either a datetime object
                or a string representation of the date.
        """
        # define relative delta settings
        relative_delta_settings = {chunk_unit: +chunk_size}

        # normalize inputs into datetime objects
        if isinstance(start_date, (int, str)):
            start_date = self.any_to_datetime(start_date)
        if isinstance(end_date, (int, str)):
            end_date = self.any_to_datetime(end_date)

        # set sd value for iteration
        sd = start_date
        # set ed value the the smaller of end_date or relative date
        ed = min(end_date, start_date + relativedelta(**relative_delta_settings))

        while 1:
            sdf = sd
            edf = ed
            if date_format is not None:
                # TODO:[high] @phuerta - this needs to be changed to arrow format
                # format the response data to a date formatted string
                # sdf = self.format_datetime(sd.isoformat(), 'UTC', date_format)
                # edf = self.format_datetime(ed.isoformat(), 'UTC', date_format)
                sdf = sd.strftime(date_format)
                edf = ed.strftime(date_format)

            # yield chunked data
            yield sdf, edf

            # break iteration once chunked ed is gte to provided end_date
            if ed >= end_date:
                break

            # update sd and ed values for next iteration
            sd = ed
            ed = min(end_date, sd + relativedelta(**relative_delta_settings))

    # TODO: [med] @phuerta - can this be done better with arrow
    def timedelta(self, time_input1: str, time_input2: str) -> dict:
        """Calculate the time delta between two time expressions.

        Args:
            time_input1: The time input string (see formats above).
            time_input2: The time input string (see formats above).

        Returns:
            (dict): Dict with delta values.
        """
        time_input1: datetime = self.any_to_datetime(time_input1)
        time_input2: datetime = self.any_to_datetime(time_input2)

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

    @staticmethod
    def _parse_default_arrow_formats(value: Any) -> 'arrow.Arrow':
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
        return arrow.get(value)

    @staticmethod
    def _parse_humanized_input(value: Any) -> 'arrow.Arrow':
        """Attempt to dehumanize time inputs. Example: 'Two hours ago'."""
        now = arrow.utcnow()
        plurals = {
            'second': 'seconds',
            'minute': 'minutes',
            'hour': 'hours',
            'day': 'days',
            'week': 'weeks',
            'month': 'months',
            'year': 'years',
        }

        if value.strip().lower() == 'now':
            return now

        # pluralize singular time terms as applicable. Arrow does not support singular terms
        terms = [plurals.get(term.lower(), term) for term in value.split()]
        value = ' '.join(terms)

        return now.dehumanize(value)

    @staticmethod
    def _parse_non_default_arrow_formats(value: Any) -> 'arrow.Arrow':
        """Attempt to parse value using non-default Arrow formats

        These are formats that Arrow provides constants for but are not used in the "get"
        method (Arrow method that parses values into datetimes) by default.

        Note: passing formats to test against overrides the default formats. Defaults are not used.
        """
        return arrow.get(
            value,
            [
                arrow.FORMAT_ATOM,
                arrow.FORMAT_COOKIE,
                arrow.FORMAT_RFC822,
                arrow.FORMAT_RFC850,
                arrow.FORMAT_RFC1036,
                arrow.FORMAT_RFC1123,
                arrow.FORMAT_RFC2822,
                arrow.FORMAT_RFC3339,
                arrow.FORMAT_RSS,
                arrow.FORMAT_W3C,
            ],
        )

    @staticmethod
    def _parse_timestamp(value: Any) -> 'arrow.Arrow':
        """Attempt to parse epoch timestamp in seconds, milliseconds, or microseconds.

        Note: passing formats to test against overrides the default formats. Defaults are not used.
        """
        # note: order matters. Must try to parse as milliseconds/microseconds first (x)
        # before trying to parse as seconds (X), else error occurs if passing a ms/ns value
        try:
            # attempt to parse as string first using microsecond/millisecond and second specifiers
            return arrow.get(value, ['x', 'X'])
        except (arrow.parser.ParserError, ValueError):
            # could not parse as string, try to parse as float
            return arrow.get(float(value))

    @staticmethod
    def _parse_date_utils(value: Any) -> 'arrow.Arrow':
        """Attempt to supplement arrows parsing ability with dateutils.

        Arrow doesn't support RFC_5322 used in HTTP 409 headers
        """
        return arrow.get(parser.parse(value))
