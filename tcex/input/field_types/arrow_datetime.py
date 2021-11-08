"""Arrow Datetime Field"""
import arrow

from typing import Any, Callable


class ArrowDateTime(arrow.Arrow):
    """Arrow Datetime Field Type"""

    @classmethod
    def _parse_default_arrow_formats(cls, value: Any) -> 'arrow.Arrow':
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

    @classmethod
    def _parse_human_time(cls, value: Any) -> 'arrow.Arrow':
        """Parse human dates, like '1 hour ago'."""
        now = arrow.utcnow()
        return now.dehumanize(value)


    @classmethod
    def _parse_non_default_arrow_formats(cls, value: Any) -> 'arrow.Arrow':
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
            ]
        )

    @classmethod
    def _parse_timestamp(cls, value: Any) -> 'arrow.Arrow':
        """Attempt to parse epoch timestamp in seconds, milliseconds, or nanoseconds.

        Note: passing formats to test against overrides the default formats. Defaults are not used.
        """
        # note: order matters. Must try to parse as milliseconds/nanoseconds first (x)
        # before trying to parse as seconds (X), else error occurs if passing a ms/ns value
        return arrow.get(value, ['x', 'X'])

    @classmethod
    def _validate(cls, value: Any) -> 'arrow.Arrow':
        """Pydantic validate method."""
        if isinstance(value, cls):
            return value

        value = str(value)

        # note: order matters. For example, the timestamp could parse inputs that would have
        # been meant for one of the default parser formats
        parser_methods = [
            cls._parse_default_arrow_formats,
            cls._parse_non_default_arrow_formats,
            cls._parse_timestamp,
        ]
        for method in parser_methods:
            try:
                return method(value)
            except (arrow.parser.ParserError, ValueError) as ex:
                # value could not be parsed by current method.
                pass

        raise ValueError(
            f'Value "{value}" of type "{type(value)}" could not be parsed as a date time object.'
        )

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Define one or more validators for Pydantic custom type."""
        yield cls._validate
