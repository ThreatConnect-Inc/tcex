"""TcEx Datetime Utilities Module"""
# standard library
import calendar
import math
import re
import time
from datetime import datetime
from typing import Optional, Tuple, Union

# third-party
import parsedatetime as pdt
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta
from tzlocal import get_localzone


class DatetimeUtils:
    """TcEx framework Datetime Utils module"""

    @staticmethod
    def _replace_timezone(dateutil_parser: object) -> datetime:
        """Replace the timezone on a datetime object.

        Args:
            dateutil_parser: The dateutil object.

        Returns:
            object: Update dateutils object.
        """
        try:
            # try to get the timezone from tzlocal
            tzinfo = pytz.timezone(get_localzone().zone)
        except pytz.exceptions.UnknownTimeZoneError:  # pragma: no cover
            try:
                # try to get the timezone from python's time package
                tzinfo = pytz.timezone(time.tzname[0])
            except pytz.exceptions.UnknownTimeZoneError:
                # seeing as all else has failed: use UTC as the timezone
                tzinfo = pytz.timezone('UTC')
        return tzinfo.localize(dateutil_parser)

    def any_to_datetime(self, time_input: str, tz: Optional[str] = None) -> datetime:
        """Return datetime object from multiple formats.

            Formats:

            #. Human Input (e.g 30 days ago, last friday)
            #. ISO 8601 (e.g. 2017-11-08T16:52:42Z)
            #. Loose Date format (e.g. 2017 12 25)
            #. Unix Time/Posix Time/Epoch Time (e.g. 1510686617 or 1510686617.298753)

        Args:
            time_input: The time input string (see formats above).
            tz): The time zone for the returned data.

        Returns:
            (datetime.datetime): Python datetime.datetime object.
        """
        # handle timestamp (e.g. 1510686617 or 1510686617.298753)
        dt_value: Optional[object] = self.unix_time_to_datetime(time_input, tz)

        # handle ISO or other formatted date (e.g. 2017-11-08T16:52:42Z,
        # 2017-11-08T16:52:42.400306+00:00)
        if dt_value is None:
            dt_value: Optional[object] = self.date_to_datetime(time_input, tz)

        # handle human readable relative time (e.g. 30 days ago, last friday)
        if dt_value is None:
            dt_value: Optional[object] = self.human_date_to_datetime(time_input, tz)

        # if all attempt to convert fail raise an error
        if dt_value is None:
            raise RuntimeError(f'Could not format input ({time_input}) to datetime string.')

        return dt_value

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
            start_date = self.any_to_datetime(start_date, 'UTC')
        if isinstance(end_date, (int, str)):
            end_date = self.any_to_datetime(end_date, 'UTC')

        # set sd value for iteration
        sd = start_date
        # set ed value the the smaller of end_date or relative date
        ed = min(end_date, start_date + relativedelta(**relative_delta_settings))

        while 1:
            sdf = sd
            edf = ed
            if date_format is not None:
                # format the response data to a date formatted string
                sdf = self.format_datetime(sd.isoformat(), 'UTC', date_format)
                edf = self.format_datetime(ed.isoformat(), 'UTC', date_format)

            # yield chunked data
            yield sdf, edf

            # break iteration once chunked ed is gte to provided end_date
            if ed >= end_date:
                break

            # update sd and ed values for next iteration
            sd = ed
            ed = min(end_date, sd + relativedelta(**relative_delta_settings))

    def date_to_datetime(self, time_input: str, tz: Optional[str] = None) -> datetime:
        """Convert ISO 8601 and other date strings to datetime.datetime type.

        Args:
            time_input: The time input string (see formats above).
            tz: The time zone for the returned data.

        Returns:
            (datetime.datetime): Python datetime.datetime object.
        """
        dt = None
        try:
            # dt = parser.parse(time_input, fuzzy_with_tokens=True)[0]
            dt: object = parser.parse(time_input)
            # don't convert timezone if dt timezone already in the correct timezone
            if tz is not None and tz != dt.tzname():
                if dt.tzinfo is None:
                    dt = self._replace_timezone(dt)
                dt = dt.astimezone(pytz.timezone(tz))
        except IndexError:  # pragma: no cover
            pass
        except TypeError:  # pragma: no cover
            pass
        except ValueError:
            pass
        return dt

    def format_datetime(
        self, time_input: str, tz: Optional[str] = None, date_format: Optional[str] = None
    ) -> str:
        """Return timestamp from multiple input formats.

            Formats:

            #. Human Input (e.g 30 days ago, last friday)
            #. ISO 8601 (e.g. 2017-11-08T16:52:42Z)
            #. Loose Date format (e.g. 2017 12 25)
            #. Unix Time/Posix Time/Epoch Time (e.g. 1510686617 or 1510686617.298753)

        .. note:: To get a unix timestamp format use the strftime format **%s**. Python
                  does not natively support **%s**, however this method has support.

        Args:
            time_input: The time input string (see formats above).
            tz: The time zone for the returned data.
            date_format: The strftime format to use, ISO by default.

        Returns:
            (string): Formatted datetime string.
        """

        # handle timestamp (e.g. 1510686617 or 1510686617.298753)
        dt_value = self.any_to_datetime(time_input, tz)

        # format date
        if date_format == '%s':
            dt_value = calendar.timegm(dt_value.timetuple())
        elif date_format:
            dt_value = dt_value.strftime(date_format)
        else:
            dt_value = dt_value.isoformat()

        return dt_value

    def human_date_to_datetime(
        self, time_input: str, tz: Optional[str] = None, source_datetime: Optional[datetime] = None
    ) -> datetime:
        """Convert human readable date (e.g. 30 days ago) to datetime.datetime.

        Examples:
        * August 25th, 2008
        * 25 Aug 2008
        * Aug 25 5pm
        * 5pm August 25
        * next saturday
        * tomorrow
        * next thursday at 4pm
        * at 4pm
        * eod
        * tomorrow eod
        * eod tuesday
        * eoy
        * eom
        * in 5 minutes
        * 5 minutes from now
        * 5 hours before now
        * 2 hours before noon
        * 2 days from tomorrow

        Args:
            time_input: The time input string (see formats above).
            tz: The time zone for the returned datetime.
            source_datetime: The reference or source datetime.

        Returns:
            (datetime.datetime): Python datetime.datetime object.
        """

        c = pdt.Constants('en')
        cal = pdt.Calendar(c, version=2)
        tzinfo = None
        src_tzname = None
        if source_datetime is not None:
            tzinfo = source_datetime.tzinfo
            src_tzname = source_datetime.tzname()
        try:
            dt, status = cal.parseDT(time_input, sourceTime=source_datetime, tzinfo=tzinfo)
            if tz is not None:  # don't add tz if no tz value is passed
                if dt.tzinfo is None:
                    dt = self._replace_timezone(dt)
                # don't covert timezone if source timezone already in the correct timezone
                if tz != src_tzname:
                    dt = dt.astimezone(pytz.timezone(tz))
            if status.accuracy == 0:
                dt = None
        except TypeError:  # pragma: no cover
            dt = None

        return dt

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
    def unix_time_to_datetime(time_input: str, tz: Optional[str] = None):
        """Convert timestamp into datetime.

        Convert (unix time|epoch time|posix time) in format of 1510686617
        or 1510686617.298753 to datetime.datetime type.

        .. note:: This method assumes UTC for all inputs.

        .. note:: This method only accepts a 9-10 character time_input.

        Args:
            time_input: The time input string (see formats above).
            tz: The time zone for the returned datetime (e.g. UTC).

        Returns:
            (datetime.datetime): Python datetime.datetime object.
        """
        dt = None
        if re.compile(r'^[0-9]{11,16}$').findall(str(time_input)):
            # handle timestamp with milliseconds and no "."
            time_input_length = len(str(time_input)) - 10
            dec = math.pow(10, time_input_length)
            time_input = float(time_input) / dec

        if re.compile(r'^[0-9]{9,10}(?:\.[0-9]{0,7})?$').findall(str(time_input)):
            dt = datetime.fromtimestamp(float(time_input), tz=pytz.timezone('UTC'))
            # don't covert timezone if dt timezone already in the correct timezone
            if tz is not None and tz != dt.tzname():
                dt = dt.astimezone(pytz.timezone(tz))

        return dt


# >>> from pytz import timezone
# >>> from datetime import datetime
# >>> time_input = 1229084481
# >>> dt = datetime.fromtimestamp(float(time_input), tz=timezone('UTC'))
# >>> dt.isoformat()
# '2008-12-12T12:21:21+00:00'
# >>> tz.normalize(dt).isoformat()
# '2008-12-12T06:21:21-06:00'
# >>> dt.astimezone(timezone('US/Central'))
# datetime.datetime(2008, 12, 12, 6, 21, 21,
#   tzinfo=<DstTzInfo 'US/Central' CST-1 day, 18:00:00 STD>)
# >>> dt.astimezone(timezone('US/Central')).isoformat()
# '2008-12-12T06:21:21-06:00'
