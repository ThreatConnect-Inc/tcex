"""Testing TcEx Input module field types."""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import IndicatorArray, IndicatorArrayOptional

from ..mock_app import MockApp


class TestInputsFieldTypeIndicatorArray:
    """Test TcEx Inputs Config."""

    @staticmethod
    def test_field_type_indicator_array_input_string(playbook_app: 'MockApp'):
        """Test BinaryArray field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        config_data = {'my_indicator': '1.1.1.1'}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert isinstance(tcex.inputs.data.my_indicator, list)

    @staticmethod
    def test_field_type_indicator_array_input_array(playbook_app: 'MockApp'):
        """Test IndicatorArray field type with array input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        config_data = {'my_indicator': ['1.1.1.1', '2.2.2.2']}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert isinstance(tcex.inputs.data.my_indicator, list)

    @staticmethod
    def test_field_type_indicator_array_input_tcentity_single(playbook_app: 'MockApp'):
        """Test BinaryArray field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        config_data = {'my_indicator': {'id': 1, 'type': 'Address', 'value': '1.1.1.1'}}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert isinstance(tcex.inputs.data.my_indicator, list)

    @staticmethod
    def test_field_type_indicator_array_input_tcentity_array(playbook_app: 'MockApp'):
        """Test BinaryArray field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        config_data = {
            'my_indicator': [
                {'id': 1, 'type': 'Address', 'value': '1.1.1.1'},
                {'id': 2, 'type': 'Host', 'value': 'www.badguys.com'},
                {'id': 3, 'type': 'URL', 'value': 'https://www.badguys.com'},
                {'id': 4, 'type': 'Address', 'value': '2.2.2.2'},
                {'id': 666, 'type': 'Adversary', 'value': 'NotAnIndicator'},
            ]
        }
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert isinstance(tcex.inputs.data.my_indicator, list)
        assert len(list(tcex.inputs.data.my_indicator.filter('type', 'Address'))) == 2
        assert len(list(tcex.inputs.data.my_indicator.filter('type', ['Address']))) == 2
        assert len(list(tcex.inputs.data.my_indicator.filter_type(['Address']))) == 2
        assert list(tcex.inputs.data.my_indicator.values(['Address'])) == [
            '1.1.1.1',
            '2.2.2.2',
        ]

    @staticmethod
    def test_field_type_indicator_array_input_empty(playbook_app: 'MockApp'):
        """Test IndicatorArray field type with empty input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArray]

        config_data = {'my_indicator': []}
        tcex = playbook_app(config_data=config_data).tcex
        try:
            tcex.inputs.add_model(PytestModel)
            assert False  # this should not hit due to the ValidationError
        except ValidationError:
            assert True  # test should fail on empty ([]) array

    @staticmethod
    def test_field_type_indicator_array_null(playbook_app: 'MockApp'):
        """Test IndicatorArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        config_data = {'my_indicator': None}
        tcex = playbook_app(config_data=config_data).tcex
        try:
            tcex.inputs.add_model(PytestModel)
            assert False  # this should not hit due to the ValidationError
        except ValidationError:
            assert True  # test should fail on empty ([]) array

    @staticmethod
    def test_field_type_indicator_array_input_groups(playbook_app: 'MockApp'):
        """Test IndicatorArray field type with optional input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        config_data = {
            'my_indicator': [
                {'id': 1, 'type': 'Adversary', 'value': 'AdversaryNotAnIndicator'},
                {'id': 2, 'type': 'Campaign', 'value': 'CampaignNotAnIndicator'},
                {'id': 3, 'type': 'Threat', 'value': 'ThreatNotAnIndicator'},
            ]
        }
        tcex = playbook_app(config_data=config_data).tcex
        try:
            tcex.inputs.add_model(PytestModel)
            assert False  # this should not hit due to the ValidationError
        except ValidationError:
            assert True  # test should fail on empty ([]) array

    # IndicatorArrayOptional

    @staticmethod
    def test_field_type_indicator_array_optional_input_null(playbook_app: 'MockApp'):
        """Test IndicatorArray field type with optional input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArrayOptional]

        config_data = {'my_indicator': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert tcex.inputs.data.my_indicator is None

    @staticmethod
    def test_field_type_indicator_array_optional_input_groups(playbook_app: 'MockApp'):
        """Test IndicatorArray field type with optional input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArrayOptional]

        config_data = {
            'my_indicator': [
                {'id': 1, 'type': 'Adversary', 'value': 'AdversaryNotAnIndicator'},
                {'id': 2, 'type': 'Campaign', 'value': 'CampaignNotAnIndicator'},
                {'id': 3, 'type': 'Threat', 'value': 'ThreatNotAnIndicator'},
            ]
        }
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert tcex.inputs.data.my_indicator == []
