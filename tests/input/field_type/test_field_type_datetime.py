"""TestInputsFieldTypeArrowDateTime for testing DateTime field type functionality.

This module contains comprehensive test cases for the DateTime field type implementation in TcEx,
including validation of various date/time formats, human-readable inputs, and error handling.

Classes:
    TestInputsFieldTypeArrowDateTime: Test class for DateTime field type validation

TcEx Module Tested: tcex.input.field_type.DateTime
"""

# standard library
import math
from collections.abc import Callable
from datetime import timedelta
from operator import add, sub
from typing import Any

# third-party
import arrow
import pytest
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ValidationError

# first-party
from tcex import TcEx  # TYPE-CHECKING
from tcex.input.field_type import DateTime
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestInputsFieldTypeArrowDateTime(InputTest):
    """TestInputsFieldTypeArrowDateTime for comprehensive DateTime field type testing.

    This class provides extensive test coverage for the DateTime field type, including validation
    of standard date formats, timestamps, human-readable date expressions, and error conditions.

    Fixtures:
        playbook_app: Mock application fixture for testing TcEx functionality
    """

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse',
        [
            pytest.param('2020-01-01', id='pass-date-format-dash-full'),
            pytest.param('2020-1-01', id='pass-date-format-dash-month-short'),
            pytest.param('2020-1-1', id='pass-date-format-dash-short'),
            pytest.param('2020/01/01', id='pass-date-format-slash-full'),
            pytest.param('2020/1/01', id='pass-date-format-slash-month-short'),
            pytest.param('2020/1/1', id='pass-date-format-slash-short'),
            pytest.param('2020.01.01', id='pass-date-format-dot-full'),
            pytest.param('2020.1.01', id='pass-date-format-dot-month-short'),
            pytest.param('2020.1.1', id='pass-date-format-dot-short'),
            pytest.param('20200101', id='pass-date-format-compact'),
            pytest.param('2020-001', id='pass-year-day-of-year-dash'),
            pytest.param('2020001', id='pass-year-day-of-year-compact'),
            pytest.param('2020-01', id='pass-year-month-dash'),
            pytest.param('2020/01', id='pass-year-month-slash'),
            pytest.param('2020.01', id='pass-year-month-dot'),
            pytest.param('2020', id='pass-year-only'),
            pytest.param('2020-01-01 00:00:00', id='pass-datetime-space-separated'),
            pytest.param('2020-01-01T00:00:00+00:00', id='pass-iso8601-with-timezone'),
            pytest.param('2020-01-01T00:00:00Z', id='pass-iso8601-zulu-timezone'),
            pytest.param('2020-01-01T00:00:00', id='pass-iso8601-no-timezone'),
        ],
    )
    def test_field_type_datetime_simple(
        playbook_app: Callable[..., MockApp], to_parse: str
    ) -> None:
        """Test parsing of date strings and timestamps for simple formats.

        Tests various simple date formats to ensure they all parse correctly to the expected
        datetime value. All test inputs are expected to parse to '2020-01-01T00:00:00+00:00'.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex: TcEx = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert (
            tcex.inputs.model.my_datetime.isoformat() == '2020-01-01T00:00:00+00:00'  # type: ignore
        )

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse',
        [
            pytest.param('2020-05-27 10:30:35+00:00', id='pass-format-atom'),
            pytest.param(
                'Wednesday, 27-May-2020 10:30:35 UTC', id='pass-format-cookie'
            ),
            pytest.param('Wed, 27 May 2020 10:30:35 +0000', id='pass-format-rss-1'),
            pytest.param('Wed, 27 May 20 10:30:35 +0000', id='pass-format-rfc822'),
            pytest.param('Wednesday, 27-May-20 10:30:35 UTC', id='pass-format-rfc850'),
            pytest.param('Wed, 27 May 20 10:30:35 +0000', id='pass-format-rfc1036'),
            pytest.param('Wed, 27 May 2020 10:30:35 +0000', id='pass-format-rfc1123'),
            pytest.param('Wed, 27 May 2020 10:30:35 +0000', id='pass-format-rfc2822'),
            pytest.param('2020-05-27 10:30:35+00:00', id='pass-format-rfc3339'),
        ],
    )
    def test_field_type_datetime_non_default_formats(
        playbook_app: Callable[..., MockApp], to_parse: str
    ) -> None:
        """Test datetime parsing with various RFC and standard format strings.

        Tests inputs from built-in (non-default) formats section of Arrow documentation including
        ATOM, COOKIE, RSS, RFC822, RFC850, RFC1036, RFC1123, RFC2822, RFC3339, and W3C formats.
        All inputs expected to parse to '2020-05-27T10:30:35+00:00'.

        arrow.FORMAT_ATOM
        '2020-05-27 10:30:35+00:00'

        arrow.FORMAT_COOKIE
        'Wednesday, 27-May-2020 10:30:35 UTC'

        arrow.FORMAT_RSS
        'Wed, 27 May 2020 10:30:35 +0000'

        arrow.FORMAT_RFC822
        'Wed, 27 May 20 10:30:35 +0000'

        arrow.FORMAT_RFC850
        'Wednesday, 27-May-20 10:30:35 UTC'

        arrow.FORMAT_RFC1036
        'Wed, 27 May 20 10:30:35 +0000'

        arrow.FORMAT_RFC1123
        'Wed, 27 May 2020 10:30:35 +0000'

        arrow.FORMAT_RFC2822
        'Wed, 27 May 2020 10:30:35 +0000'

        arrow.FORMAT_RFC3339
        '2020-05-27 10:30:35+00:00'

        arrow.FORMAT_W3C
        '2020-05-27 10:30:35+00:00'

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex: TcEx = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert (
            tcex.inputs.model.my_datetime.isoformat() == '2020-05-27T10:30:35+00:00'  # type: ignore
        )

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse',
        [
            pytest.param(
                '1636415957.728793', id='pass-timestamp-float-microseconds-six'
            ),
            pytest.param(
                '1636415957728.793', id='pass-timestamp-float-microseconds-three'
            ),
            pytest.param('1636415957728793', id='pass-timestamp-int-microseconds'),
        ],
    )
    def test_field_type_datetime_microseconds(
        playbook_app: Callable[..., MockApp], to_parse: str
    ) -> None:
        """Test parsing of timestamp inputs with microsecond precision.

        Tests various timestamp formats with microsecond precision to ensure proper parsing.
        All inputs expected to parse to '2021-11-08T23:59:17.728793+00:00'.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex: TcEx = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert (
            tcex.inputs.model.my_datetime.isoformat()  # type: ignore
            == '2021-11-08T23:59:17.728793+00:00'
        )

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse',
        [
            pytest.param('1636415957.728', id='pass-timestamp-float-milliseconds'),
            pytest.param('1636415957728', id='pass-timestamp-int-milliseconds'),
        ],
    )
    def test_field_type_datetime_milliseconds(
        playbook_app: Callable[..., MockApp], to_parse: str
    ) -> None:
        """Test parsing of timestamp inputs with millisecond precision.

        Tests various timestamp formats with millisecond precision to ensure proper parsing.
        All inputs expected to parse to '2021-11-08T23:59:17.728000+00:00'.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex: TcEx = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert (
            tcex.inputs.model.my_datetime.isoformat()  # type: ignore
            == '2021-11-08T23:59:17.728000+00:00'
        )

    @staticmethod
    def test_field_type_datetime_seconds(playbook_app: Callable[..., MockApp]) -> None:
        """Test parsing of timestamp inputs with second precision.

        Tests parsing of epoch timestamps in seconds to ensure proper conversion to datetime.
        Expected to parse to '2021-11-08T23:59:17+00:00'.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': '1636415957'}
        app = playbook_app(config_data=config_data)
        tcex: TcEx = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert (
            tcex.inputs.model.my_datetime.isoformat() == '2021-11-08T23:59:17+00:00'  # type: ignore
        )

    @staticmethod
    def test_field_type_datetime_timezone_aware_input(
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test parsing of timezone-aware datetime input strings.

        Tests parsing of datetime strings that include timezone information to ensure the timezone
        is preserved in the parsed result.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': '2021-11-15T02:13:57.021291-08:00'}
        app = playbook_app(config_data=config_data)
        tcex: TcEx = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert (
            tcex.inputs.model.my_datetime.isoformat()  # type: ignore
            == '2021-11-15T02:13:57.021291-08:00'
        )

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse,operator,delta',
        [
            pytest.param('now', sub, timedelta(hours=0), id='pass-now-no-delta'),
            pytest.param(
                '1 years ago', sub, relativedelta(years=1), id='pass-years-ago-plural'
            ),
            pytest.param(
                'in 1 years', add, relativedelta(years=1), id='pass-in-years-plural'
            ),
            pytest.param(
                '1 months ago',
                sub,
                relativedelta(months=1),
                id='pass-months-ago-plural',
            ),
            pytest.param(
                'in 1 months', add, relativedelta(months=1), id='pass-in-months-plural'
            ),
            pytest.param(
                '2 weeks ago', sub, timedelta(weeks=2), id='pass-weeks-ago-plural'
            ),
            pytest.param(
                'in 2 weeks', add, timedelta(weeks=2), id='pass-in-weeks-plural'
            ),
            pytest.param(
                '2 days ago', sub, timedelta(days=2), id='pass-days-ago-plural'
            ),
            pytest.param('in 2 days', add, timedelta(days=2), id='pass-in-days-plural'),
            pytest.param(
                '1 hours ago', sub, timedelta(hours=1), id='pass-hours-ago-plural'
            ),
            pytest.param(
                'in 1 hours', add, timedelta(hours=1), id='pass-in-hours-plural'
            ),
            pytest.param(
                '2 minutes ago', sub, timedelta(minutes=2), id='pass-minutes-ago-plural'
            ),
            pytest.param(
                'in 2 minutes', add, timedelta(minutes=2), id='pass-in-minutes-plural'
            ),
            pytest.param(
                '2 seconds ago', sub, timedelta(seconds=2), id='pass-seconds-ago-plural'
            ),
            pytest.param(
                'in 2 seconds', add, timedelta(seconds=2), id='pass-in-seconds-plural'
            ),
            pytest.param(
                '1 year ago', sub, relativedelta(years=1), id='pass-year-ago-singular'
            ),
            pytest.param(
                '1 Year ago',
                sub,
                relativedelta(years=1),
                id='pass-year-ago-capitalized',
            ),
            pytest.param(
                'in 1 year', add, relativedelta(years=1), id='pass-in-year-singular'
            ),
            pytest.param(
                '1 month ago',
                sub,
                relativedelta(months=1),
                id='pass-month-ago-singular',
            ),
            pytest.param(
                'in 1 month', add, relativedelta(months=1), id='pass-in-month-singular'
            ),
            pytest.param(
                '2 week ago', sub, timedelta(weeks=2), id='pass-week-ago-singular'
            ),
            pytest.param(
                'in 2 week', add, timedelta(weeks=2), id='pass-in-week-singular'
            ),
            pytest.param(
                '2 day ago', sub, timedelta(days=2), id='pass-day-ago-singular'
            ),
            pytest.param('in 2 day', add, timedelta(days=2), id='pass-in-day-singular'),
            pytest.param(
                '1 hour ago', sub, timedelta(hours=1), id='pass-hour-ago-singular'
            ),
            pytest.param(
                'in 1 hour', add, timedelta(hours=1), id='pass-in-hour-singular'
            ),
            pytest.param(
                '2 minute ago', sub, timedelta(minutes=2), id='pass-minute-ago-singular'
            ),
            pytest.param(
                'in 2 minute', add, timedelta(minutes=2), id='pass-in-minute-singular'
            ),
            pytest.param(
                '1 second ago', sub, timedelta(seconds=1), id='pass-second-ago-singular'
            ),
            pytest.param(
                'in 1 second', add, timedelta(seconds=1), id='pass-in-second-singular'
            ),
            pytest.param(
                '120 Days Ago', sub, timedelta(days=120), id='pass-days-ago-capitalized'
            ),
        ],
    )
    def test_field_type_datetime_human_input(
        playbook_app: Callable[..., MockApp],
        to_parse: str,
        operator: Callable,
        delta: timedelta | relativedelta,
    ) -> None:
        """Test parsing of human-readable datetime expressions.

        Tests parsing of human-readable datetime inputs like '2 days ago', 'in 1 hour', etc.
        Inputs are parsed relative to 'now' in UTC and compared to calculated expected values.
        Small amount of time variance is allowed for seconds and minutes to account for execution time.

        Args:
            to_parse: The human date time expression to parse
            operator: Either add or subtract operator for calculating expected value
            delta: The time delta object for calculating the approximate expected result

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        now = arrow.utcnow()

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex: TcEx = app.tcex
        tcex.inputs.add_model(PytestModel)

        expected_parse_result = operator(now, delta)
        result = tcex.inputs.model.my_datetime  # type: ignore

        assert expected_parse_result.year == result.year
        assert expected_parse_result.month == result.month
        assert expected_parse_result.day == result.day
        assert expected_parse_result.hour == result.hour
        assert expected_parse_result.tzinfo == result.tzinfo

        # As minutes and seconds could change in the middle of execution, minutes and seconds
        # are validated by taking the difference in seconds of the result and the expected result
        # this essentially validates the above assertions as well, but leaving the above assertions
        # in place for completeness (especially the tzinfo assertion).
        #
        # Get time delta between expected result and result and calculate difference in seconds
        second_difference = abs(
            math.floor((expected_parse_result - result).total_seconds())
        )
        assert 0 <= second_difference <= 3

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse',
        [
            pytest.param('in one hour', id='fail-in-one-hour'),
            pytest.param('1 hour from now', id='fail-1-hour-from-now'),
            pytest.param('bad input', id='fail-bad-input-string'),
            pytest.param('', id='fail-empty-string'),
            pytest.param([], id='fail-empty-list'),
            pytest.param({}, id='fail-empty-dict'),
        ],
    )
    def test_field_type_datetime_bad_input(
        playbook_app: Callable[..., MockApp], to_parse: Any
    ) -> None:
        """Test validation of invalid datetime input values.

        Tests that invalid input values raise appropriate ValidationError exceptions with
        meaningful error messages.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex: TcEx = app.tcex
        with pytest.raises(ValidationError) as ex:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(ex.value)

        assert f'{to_parse}' in err_msg
        assert 'could not be parsed as a date time object' in err_msg

    @staticmethod
    def test_field_type_datetime_none_not_allowed(
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test that None values are rejected when not explicitly allowed.

        Tests that None values raise ValidationError when the field type does not allow None.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': None}
        app = playbook_app(config_data=config_data)
        tcex: TcEx = app.tcex
        with pytest.raises(ValidationError) as ex:
            tcex.inputs.add_model(PytestModel)

        assert 'could not be parsed as a date time object' in str(ex.value)

    @staticmethod
    def test_field_type_datetime_none_allowed(
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test that None values are accepted when explicitly allowed.

        Tests that None values are properly handled when the field type allows None values
        using union type syntax.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime | None

        config_data = {'my_datetime': None}
        app = playbook_app(config_data=config_data)
        tcex: TcEx = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime is None  # type: ignore
