"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import GroupArray, GroupArrayOptional

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeGroupArray:
    """Test TcEx Inputs Config."""

    @staticmethod
    def test_field_type_group_array_input_string(playbook_app: 'MockApp'):
        """Test BinaryArray field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        config_data = {'my_group': 'adversary_1'}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert isinstance(tcex.inputs.data.my_group, list)

    @staticmethod
    def test_field_type_group_array_input_array(playbook_app: 'MockApp'):
        """Test GroupArray field type with array input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        config_data = {'my_group': ['adversary_1', 'adversary_2']}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert isinstance(tcex.inputs.data.my_group, list)

    @staticmethod
    def test_field_type_group_array_input_tcentity_single(playbook_app: 'MockApp'):
        """Test BinaryArray field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        config_data = {'my_group': {'id': 1, 'type': 'Adversary', 'value': 'adversary_1'}}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert isinstance(tcex.inputs.data.my_group, list)

    @staticmethod
    def test_field_type_group_array_input_tcentity_array(playbook_app: 'MockApp'):
        """Test BinaryArray field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        config_data = {
            'my_group': [
                {'id': 1, 'type': 'Adversary', 'value': 'adversary_1'},
                {'id': 2, 'type': 'Adversary', 'value': 'adversary_2'},
                {'id': 666, 'type': 'Address', 'value': 'AddressNotAGroup'},
            ]
        }
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert isinstance(tcex.inputs.data.my_group, list)
        assert len(list(tcex.inputs.data.my_group.filter('type', 'Adversary'))) == 2
        assert len(list(tcex.inputs.data.my_group.filter('type', ['Adversary']))) == 2
        assert len(list(tcex.inputs.data.my_group.filter_type(['Adversary']))) == 2
        assert list(tcex.inputs.data.my_group.values(['Adversary'])) == [
            'adversary_1',
            'adversary_2',
        ]

    @staticmethod
    def test_field_type_group_array_input_empty(playbook_app: 'MockApp'):
        """Test GroupArray field type with empty input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArray]

        config_data = {'my_group': []}
        tcex = playbook_app(config_data=config_data).tcex
        try:
            tcex.inputs.add_model(PytestModel)
            assert False  # this should not hit due to the ValidationError
        except ValidationError:
            assert True  # test should fail on empty ([]) array

    @staticmethod
    def test_field_type_group_array_null(playbook_app: 'MockApp'):
        """Test GroupArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        config_data = {'my_group': None}
        tcex = playbook_app(config_data=config_data).tcex
        try:
            tcex.inputs.add_model(PytestModel)
            assert False  # this should not hit due to the ValidationError
        except ValidationError:
            assert True  # test should fail on empty ([]) array

    @staticmethod
    def test_field_type_group_array_input_indicators(playbook_app: 'MockApp'):
        """Test GroupArray field type with optional input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        config_data = {
            'my_group': [
                {'id': 1, 'type': 'Address', 'value': '1.1.1.1'},
                {'id': 2, 'type': 'Host', 'value': 'www.badguys.com'},
                {'id': 3, 'type': 'URL', 'value': 'https://www.badguys.com'},
            ]
        }
        tcex = playbook_app(config_data=config_data).tcex
        try:
            tcex.inputs.add_model(PytestModel)
            assert False  # this should not hit due to the ValidationError
        except ValidationError:
            assert True  # test should fail on empty ([]) array

    # GroupArrayOptional

    @staticmethod
    def test_field_type_group_array_optional_input_null(playbook_app: 'MockApp'):
        """Test GroupArray field type with optional input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArrayOptional]

        config_data = {'my_group': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert tcex.inputs.data.my_group is None

    @staticmethod
    def test_field_type_group_array_optional_input_groups(playbook_app: 'MockApp'):
        """Test GroupArray field type with optional input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArrayOptional]

        config_data = {
            'my_group': [
                {'id': 1, 'type': 'Address', 'value': '1.1.1.1'},
                {'id': 2, 'type': 'Host', 'value': 'www.badguys.com'},
                {'id': 3, 'type': 'URL', 'value': 'https://www.badguys.com'},
            ]
        }
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert tcex.inputs.data.my_group == []
