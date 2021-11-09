"""Testing TcEx Input module field types."""
# standard library
from datetime import timedelta
from operator import add, sub
from typing import TYPE_CHECKING

# third-party
import arrow
import pytest
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel

# first-party
from tcex.input.field_types import DateTime

from .utils import InputTest

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeArrowDateTime(InputTest):
    """Test TcEx ArrowDatetime Input"""

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
    def test_field_type_arrow_date_time_simple(self, playbook_app: 'MockApp', to_parse):
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
    def test_field_type_arrow_date_time_non_default_formats(
        self, playbook_app: 'MockApp', to_parse
    ):
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

    @pytest.mark.parametrize(
        'to_parse',
        [
            '1636415957.728793',
            '1636415957728.793',
            '1636415957728793',
        ],
    )
    def test_field_type_arrow_date_time_microseconds(self, playbook_app: 'MockApp', to_parse):
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

    @pytest.mark.parametrize(
        'to_parse',
        [
            '1636415957.728',
            '1636415957728',
        ],
    )
    def test_field_type_arrow_date_time_milliseconds(self, playbook_app: 'MockApp', to_parse):
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

    def test_field_type_arrow_date_time_seconds(self, playbook_app: 'MockApp'):
        """Testing timestamp inputs. Parse seconds epoch"""

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': '1636415957'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime.isoformat() == '2021-11-08T23:59:17+00:00'

    @pytest.mark.parametrize(
        'to_parse,operator,delta',
        [
            # operator doesnt matter for 'now', as the time delta is 0
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
        ],
    )
    def test_field_type_arrow_date_time_human_input(
        self, playbook_app: 'MockApp', to_parse, operator, delta
    ):
        """Testing timestamp inputs

        Inputs are parsed relative to 'now' in UTC. The parsed input will be compared to a
        datetime object that is calculated outside of TCEX. Note that a small amount of play
        is allowed when comparing minutes in case minutes change between the time the test starts
        and the time the date is parsed.

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

        # allow a bit of play in minutes in case the time changes between the time the 'now'
        # variable of this test case is calculated and the time that TCEX parses the human input.
        minute_difference = abs(expected_parse_result.minute - result.minute)
        assert minute_difference == 0 or minute_difference == 1

    @pytest.mark.parametrize(
        'to_parse',
        [
            'Wednesday, 27-May-2020 10:30:35',
            'Wed, 27 May 2020 10:30:35',
            'Wed, 27 May 20 10:30:35',
            'Wednesday, 27-May-20 10:30:35',
            'Wed, 27 May 20 10:30:35',
            'Wed, 27 May 2020 10:30:35',
            'May 27 2020',
            '05 27 2020',
            'in one hour',
            'in 1 hour',
            '1 hour from now',
            '1 hour ago',
        ],
    )
    def test_field_type_arrow_date_time_unsupported_format(self, playbook_app: 'MockApp', to_parse):
        """Testing timestamp inputs

        This test keeps track of date strings that have been found to be unsupported.
        Parsing these date strings will result in failure.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: DateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)
