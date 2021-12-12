"""Testing TcEx Input module field types."""
# standard library
import math
from datetime import timedelta
from operator import add, sub
from typing import TYPE_CHECKING, Optional

# third-party
import arrow
import pytest
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import DateTime

from .utils import InputTest

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeArrowDateTime(InputTest):
    """Test TcEx ArrowDatetime Input"""

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse',
        [
            '2020-01-01',
            '2020-1-01',
            '2020-1-1',
            '2020/01/01',
            '2020/1/01',
            '2020/1/1',
            '2020.01.01',
            '2020.1.01',
            '2020.1.1',
            '20200101',
            # year-day-of-year
            '2020-001',
            # same as above, but without separating dash
            '2020001',
            '2020-01',
            '2020/01',
            '2020.01',
            '2020',
            '2020-01-01 00:00:00',
            # ISO 8601 still handled by default parser
            '2020-01-01T00:00:00+00:00',
            '2020-01-01T00:00:00Z',
            '2020-01-01T00:00:00',
        ],
    )
    def test_field_type_datetime_simple(playbook_app: 'MockApp', to_parse):
        """Test parsing of date strings and timestamps

        All test inputs are expected to parse to '2020-01-01T00:00:00+00:00'
        Args:
            playbook_app (fixture): An instance of MockApp.
            to_parse: an input that should be converted to a an Arrow Datetime
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime.isoformat() == '2020-01-01T00:00:00+00:00'

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse',
        [
            '2020-05-27 10:30:35+00:00',
            'Wednesday, 27-May-2020 10:30:35 UTC',
            'Wed, 27 May 2020 10:30:35 +0000',
            'Wed, 27 May 20 10:30:35 +0000',
            'Wednesday, 27-May-20 10:30:35 UTC',
            'Wed, 27 May 20 10:30:35 +0000',
            'Wed, 27 May 2020 10:30:35 +0000',
            'Wed, 27 May 2020 10:30:35 +0000',
            '2020-05-27 10:30:35+00:00',
        ],
    )
    def test_field_type_datetime_non_default_formats(playbook_app: 'MockApp', to_parse):
        """Testing inputs directly from built-in (non-default) formats section of docs.

        All inputs expected to parse to '2020-05-27T10:30:35+00:00'

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
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime.isoformat() == '2020-05-27T10:30:35+00:00'

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse',
        [
            '1636415957.728793',
            '1636415957728.793',
            '1636415957728793',
        ],
    )
    def test_field_type_datetime_microseconds(playbook_app: 'MockApp', to_parse):
        """Testing timestamp inputs

        All inputs expected to parse to '2021-11-08T23:59:17.728793+00:00'
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime.isoformat() == '2021-11-08T23:59:17.728793+00:00'

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse',
        [
            '1636415957.728',
            '1636415957728',
        ],
    )
    def test_field_type_datetime_milliseconds(playbook_app: 'MockApp', to_parse):
        """Testing timestamp inputs

        All inputs expected to parse to '2021-11-08T23:59:17.728000+00:00'
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime.isoformat() == '2021-11-08T23:59:17.728000+00:00'

    @staticmethod
    def test_field_type_datetime_seconds(playbook_app: 'MockApp'):
        """Testing timestamp inputs. Parse seconds epoch"""

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': '1636415957'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime.isoformat() == '2021-11-08T23:59:17+00:00'

    @staticmethod
    def test_field_type_datetime_timezone_aware_input(playbook_app: 'MockApp'):
        """Testing timestamp inputs. Parse timezone-aware string"""

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': '2021-11-15T02:13:57.021291-08:00'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime.isoformat() == '2021-11-15T02:13:57.021291-08:00'

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse,operator,delta',
        [
            # operator doesn't matter for 'now', as the time delta is 0
            ('now', sub, timedelta(hours=0)),
            ('1 years ago', sub, relativedelta(years=1)),
            ('in 1 years', add, relativedelta(years=1)),
            ('1 months ago', sub, relativedelta(months=1)),
            ('in 1 months', add, relativedelta(months=1)),
            ('2 weeks ago', sub, timedelta(weeks=2)),
            ('in 2 weeks', add, timedelta(weeks=2)),
            ('2 days ago', sub, timedelta(days=2)),
            ('in 2 days', add, timedelta(days=2)),
            ('1 hours ago', sub, timedelta(hours=1)),
            ('in 1 hours', add, timedelta(hours=1)),
            ('2 minutes ago', sub, timedelta(minutes=2)),
            ('in 2 minutes', add, timedelta(minutes=2)),
            ('2 seconds ago', sub, timedelta(seconds=2)),
            ('in 2 seconds', add, timedelta(seconds=2)),
            # same as above, but with singular terms
            ('1 year ago', sub, relativedelta(years=1)),
            ('in 1 year', add, relativedelta(years=1)),
            ('1 month ago', sub, relativedelta(months=1)),
            ('in 1 month', add, relativedelta(months=1)),
            ('2 week ago', sub, timedelta(weeks=2)),
            ('in 2 week', add, timedelta(weeks=2)),
            ('2 day ago', sub, timedelta(days=2)),
            ('in 2 day', add, timedelta(days=2)),
            ('1 hour ago', sub, timedelta(hours=1)),
            ('in 1 hour', add, timedelta(hours=1)),
            ('2 minute ago', sub, timedelta(minutes=2)),
            ('in 2 minute', add, timedelta(minutes=2)),
            ('1 second ago', sub, timedelta(seconds=1)),
            ('in 1 second', add, timedelta(seconds=1)),
        ],
    )
    def test_field_type_datetime_human_input(playbook_app: 'MockApp', to_parse, operator, delta):
        """Testing timestamp inputs

        Inputs are parsed relative to 'now' in UTC. The parsed input will be compared to a
        datetime object that is calculated outside of TCEX. Note that a small amount of play
        is allowed when comparing minutes in case minutes change between the time the test starts
        and the time the date is parsed. This play is also allowed for seconds.

        :param to_parse: the human date time to parse.
        :param operator: either an add or subtract operator that will be used to calculate
        the expected value
        :param delta: the time delta object to use to calculate the approximate value that should
        result from the parsing of the human date time string.
        """

        now = arrow.utcnow()

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        expected_parse_result = operator(now, delta)
        result = tcex.inputs.model.my_datetime

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
        second_difference = abs(math.floor((expected_parse_result - result).total_seconds()))
        assert 0 <= second_difference <= 2

    @staticmethod
    @pytest.mark.parametrize(
        'to_parse',
        [
            # some unsupported formats for awareness (not inclusive of all unsupported formats)
            'in one hour',
            '1 hour from now',
            # bad inputs
            'bad input',
            '',
            [],
            {},
        ],
    )
    def test_field_type_datetime_bad_input(playbook_app: 'MockApp', to_parse):
        """Test parsing of bad input

        Args:
            playbook_app (fixture): An instance of MockApp.
            to_parse: an input that cannot be parsed
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)
            print('')

        err_msg = str(exc_info.value)

        assert f'{to_parse}' in err_msg
        assert 'could not be parsed as a date time object' in err_msg

    @staticmethod
    def test_field_type_datetime_none_not_allowed(playbook_app: 'MockApp'):
        """Testing timestamp inputs. None not allowed"""

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': None}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_datetime_none_allowed(playbook_app: 'MockApp'):
        """Testing timestamp inputs. None allowed"""

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: Optional[DateTime]

        config_data = {'my_datetime': None}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime is None
