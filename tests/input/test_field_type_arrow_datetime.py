"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING

# third-party
import pytest
from pydantic import BaseModel

# first-party
from tcex.input.field_types import ArrowDateTime

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
            # ISO 8601 still handled by default parser
            '2020-01-01T00:00:00+00:00',
            '2020-01-01T00:00:00'
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

            my_datetime: ArrowDateTime

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

            my_datetime: ArrowDateTime

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

            my_datetime: ArrowDateTime

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

            my_datetime: ArrowDateTime

        config_data = {'my_datetime': to_parse}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime.isoformat() == '2021-11-08T23:59:17.728000+00:00'

    def test_field_type_arrow_date_time_seconds(self, playbook_app: 'MockApp'):
        """Testing timestamp inputs. Parse seconds epoch"""

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_datetime: ArrowDateTime

        config_data = {'my_datetime': '1636415957'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_datetime.isoformat() == '2021-11-08T23:59:17+00:00'
