""" TcEx Utilities Class """
from datetime import datetime
import calendar
import re

from pytz import timezone
from dateutil import parser
from tzlocal import get_localzone
import parsedatetime as pdt


class TcExUtils():
    """TcEx framework utilities."""

    def __init__(self, tcex):
        """Initialize class data

        Initialize parent class for default values and logging method.
        """
        self._tcex = tcex

    def format_datetime(self, time_input, tz='UTC', date_format=None):
        """Return timestamp from multiple input formats.

            Formats:

            #. Human Input (e.g 30 days ago, last friday)
            #. ISO 8601 (e.g. 2017-11-08T16:52:42Z)
            #. Loose Date format (e.g. 2017 12 25)
            #. Unix Time/Posix Time/Epoch Time (e.g. 1510686617 or 1510686617.298753)

        .. note:: To get a unix timestamp format use the strftime format **%s**. While Python
                  does not properly support this the method has functionality to handle this
                  use case.

        Args:
            time_input (string): The time input string (see formats above).
            tz (string): The time zone for the returned data.
            date_format (string): The strftime format to use, ISO by default.

        Returns:
            (string): Formatted datetime string.
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
            raise RuntimeError('Could not format input ({}) to datetime string.'.format(time_input))

        # format date
        if date_format == '%s':
            dt_value = calendar.timegm(dt_value.timetuple())
        elif date_format:
            dt_value = dt_value.strftime(date_format)
        else:
            dt_value = dt_value.isoformat()

        return dt_value

    @staticmethod
    def date_to_datetime(time_input, tz=None):
        """ Convert ISO 8601 and other date strings to datetime.datetime type.

        Args:
            time_input (string): The time input string (see formats above).
            tz (string): The time zone for the returned data.

        Returns:
            (datetime.datetime): Python datetime.datetime object.
        """
        dt = None
        if tz is not None:
            tz = timezone(tz)
        try:
            dt = parser.parse(time_input)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone(get_localzone().zone))
            if tz is not None:
                dt = dt.astimezone(tz)
        except ValueError:
            pass

        return dt

    @staticmethod
    def human_date_to_datetime(time_input, tz='UTC'):
        """ Convert human readable date (e.g. 30 days ago) to datetime.datetime using
            parsedatetime module.

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
            tz (string): The time zone for the returned data.

        Returns:
            (datetime.datetime): Python datetime.datetime object.
        """
        dt = None
        cal = pdt.Calendar()
        local_tz = timezone(get_localzone().zone)
        dt, status = cal.parseDT(time_input, tzinfo=local_tz)
        dt = dt.astimezone(timezone(tz))
        if status == 0:
            dt = None

        return dt

    @staticmethod
    def unix_time_to_datetime(time_input, tz='UTC'):
        """ Convert (unix time|epoch time|posix time) in format of 1510686617 or 1510686617.298753
            to datetime.datetime type.

        Args:
            time_input (string): The time input string (see formats above).
            tz (string): The time zone for the returned data.

        Returns:
            (datetime.datetime): Python datetime.datetime object.
        """
        dt = None
        tz = timezone(tz)
        if re.compile(r'^[0-9]{10}(?:\.[0-9]{0,10})?$').findall(str(time_input)):
            dt = datetime.fromtimestamp(float(time_input), tz)

        return dt
