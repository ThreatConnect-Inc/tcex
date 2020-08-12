# -*- coding: utf-8 -*-
"""TcEx Datetime Utilities Module"""
# standard library
import calendar
import math
import re
import time
from datetime import datetime

# third-party
import parsedatetime as pdt
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta
from tzlocal import get_localzone


class DatetimeUtils:
    """TcEx framework Datetime Utils module"""

    @staticmethod
    def _replace_timezone(dateutil_parser):
        """Replace the timezone on a datetime object."""
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

    def any_to_datetime(self, time_input, tz=None):
        """Return datetime object from multiple formats.

            Formats:

            #. Human Input (e.g 30 days ago, last friday)
            #. ISO 8601 (e.g. 2017-11-08T16:52:42Z)
            #. Loose Date format (e.g. 2017 12 25)
            #. Unix Time/Posix Time/Epoch Time (e.g. 1510686617 or 1510686617.298753)

        Args:
            time_input (string): The time input string (see formats above).
            tz (string): The time zone for the returned data.

        Returns:
            (datetime.datetime): Python datetime.datetime object.
        """
        # handle timestamp (e.g. 1510686617 or 1510686617.298753)
        dt_value = self.unix_time_to_datetime(time_input, tz)

        # handle ISO or other formatted date (e.g. 2017-11-08T16:52:42Z,
        # 2017-11-08T16:52:42.400306+00:00)
        if dt_value is None:
            dt_value = self.date_to_datetime(time_input, tz)

        # handle human readable relative time (e.g. 30 days ago, last friday)
        if dt_value is None:
            dt_value = self.human_date_to_datetime(time_input, tz)

        # if all attempt to convert fail raise an error
        if dt_value is None:
            raise RuntimeError(f'Could not format input ({time_input}) to datetime string.')

        return dt_value

    def date_to_datetime(self, time_input, tz=None):
        """Convert ISO 8601 and other date strings to datetime.datetime type.

        Args:
            time_input (string): The time input string (see formats above).
            tz (string): The time zone for the returned data.

        Returns:
            (datetime.datetime): Python datetime.datetime object.
        """
        dt = None
        try:
            # dt = parser.parse(time_input, fuzzy_with_tokens=True)[0]
            dt = parser.parse(time_input)
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

    def format_datetime(self, time_input, tz=None, date_format=None):
        """Return timestamp from multiple input formats.

            Formats:

            #. Human Input (e.g 30 days ago, last friday)
            #. ISO 8601 (e.g. 2017-11-08T16:52:42Z)
            #. Loose Date format (e.g. 2017 12 25)
            #. Unix Time/Posix Time/Epoch Time (e.g. 1510686617 or 1510686617.298753)

        .. note:: To get a unix timestamp format use the strftime format **%s**. Python
                  does not natively support **%s**, however this method has support.

        Args:
            time_input (string): The time input string (see formats above).
            tz (string): The time zone for the returned data.
            date_format (string): The strftime format to use, ISO by default.

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

    def human_date_to_datetime(self, time_input, tz=None, source_datetime=None):
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
            time_input (string): The time input string (see formats above).
            tz (string): The time zone for the returned datetime.
            source_datetime (datetime.datetime): The reference or source datetime.

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

    def timedelta(self, time_input1, time_input2):
        """Calculate the time delta between two time expressions.

        Args:
            time_input1 (string): The time input string (see formats above).
            time_input2 (string): The time input string (see formats above).

        Returns:
            (dict): Dict with delta values.
        """
        time_input1 = self.any_to_datetime(time_input1)
        time_input2 = self.any_to_datetime(time_input2)

        diff = time_input1 - time_input2  # timedelta
        delta = relativedelta(time_input1, time_input2)  # relativedelta

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
    def unix_time_to_datetime(time_input, tz=None):
        """Convert timestamp into datetime.

        Convert (unix time|epoch time|posix time) in format of 1510686617
        or 1510686617.298753 to datetime.datetime type.

        .. note:: This method assumes UTC for all inputs.

        .. note:: This method only accepts a 9-10 character time_input.

        Args:
            time_input (string): The time input string (see formats above).
            tz (string): The time zone for the returned datetime (e.g. UTC).

        Returns:
            (datetime.datetime): Python datetime.datetime object.
        """
        dt = None
        if re.compile(r'^[0-9]{11,16}$').findall(str(time_input)):
            # handle timestamp with milliseconds and no "."
            time_input_length = len(str(time_input)) - 10
            dec = math.pow(10, time_input_length)
            time_input = float(time_input) / dec

        if re.compile(r'^[0-9]{9,10}(?:\.[0-9]{0,6})?$').findall(str(time_input)):
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
