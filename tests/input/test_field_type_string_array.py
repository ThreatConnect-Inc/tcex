"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import StringArray, StringArrayOptional
from tcex.input.field_types.customizable import custom_string_array

from .utils import InputTest

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeStringArray(InputTest):
    """Test TcEx StringArray and StringArrayOptional Inputs"""

    def test_field_type_string_array_input_string_staged(self, playbook_app: 'MockApp'):
        """Test StringArray field type with string input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': '#App:1234:my_string!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!String', 'string', tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string == ['string']

    def test_field_type_string_array_input_string_array_staged(self, playbook_app: 'MockApp'):
        """Test StringArray field type with string array input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': '#App:1234:my_string!StringArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!StringArray', ['string'], tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string == ['string']

    @staticmethod
    def test_field_type_string_array_input_invalid(playbook_app: 'MockApp'):
        """Test StringArray field type with non-string input.

        Exception expected, as value is not a string value

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': {}}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)
        assert 'Value "{}"' in err_msg and "not of Array's type" in err_msg

    @staticmethod
    def test_field_type_string_array_input_invalid_array(playbook_app: 'MockApp'):
        """Test StringArray field type with array that contains non-string member.

        Exception expected, as value is not a string array

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': [{}]}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)
        assert 'Value "{}"' in err_msg and "not of Array's type" in err_msg

    @staticmethod
    def test_field_type_string_array_input_empty_array(playbook_app: 'MockApp'):
        """Test StringArray field type with empty array input.

        This test is expected to fail, as StringArrayOptional type is not used when
        defining my_string.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArray]

        config_data = {'my_string': []}
        tcex = playbook_app(config_data=config_data).tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Array must have at least one element' in str(exc_info.value)

    @staticmethod
    def test_field_type_string_array_optional_input_empty_array(playbook_app: 'MockApp'):
        """Test StringArray field type with empty array input.

        No Exception is expected, as StringArrayOptional type is used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArrayOptional]

        config_data = {'my_string': []}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string == []

    def test_field_type_string_array_input_empty_string(self, playbook_app: 'MockApp'):
        """Test StringArray field type with empty input.

        Exception expected, as value is empty and StringArrayOptional type is not used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArray]

        config_data = {'my_string': '#App:1234:my_string!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!String', '', tcex)

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Value "" may not be empty' in str(exc_info.value)

    def test_field_type_string_array_optional_input_empty_string(self, playbook_app: 'MockApp'):
        """Test StringArray field type with empty input.

        No Exception is expected, as StringArrayOptional type is used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArrayOptional]

        config_data = {'my_string': '#App:1234:my_string!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!String', '', tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string == ['']

    @staticmethod
    def test_field_type_string_array_input_null(playbook_app: 'MockApp'):
        """Test StringArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_string_array_optional_input_null(playbook_app: 'MockApp'):
        """Test StringArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArrayOptional

        config_data = {'my_string': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_optional_field_type_string_array(playbook_app: 'MockApp'):
        """Test StringArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of StringArray with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArray]

        config_data = {'my_string': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string is None

    @staticmethod
    def test_optional_field_type_string_array_optional(playbook_app: 'MockApp'):
        """Test StringArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of StringArrayOptional with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArrayOptional]

        config_data = {'my_string': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string is None

    def test_field_type_string_array_input_array_with_empty_and_null_members(
        self, playbook_app: 'MockApp'
    ):
        """Test StringArray field type with Array input that contains empty and null members.

        An empty member of StringArray is considered to be ''.
        A null member of StringArray is considered to be None.

        By default, StringArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default, so no error expected.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': '#App:1234:my_string!StringArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!StringArray', ['', None], tcex)
        tcex.inputs.add_model(PytestModel)

        # empty and null members are ok
        assert tcex.inputs.data.my_string == ['', None]

    def test_field_type_string_array_input_array_with_empty_and_null_members_empty_not_allowed(
        self, playbook_app: 'MockApp'
    ):
        """Test StringArray field type with Array input that contains empty and null members.

        An empty member of StringArray is considered to be ''.
        A null member of StringArray is considered to be None.

        By default, StringArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default.

        StringArray is configured to not accept empty members, so an error is expected due to
        '' being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: custom_string_array(allow_empty_members=False)

        config_data = {'my_string': '#App:1234:my_string!StringArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!StringArray', ['', None], tcex)
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # assert None did not cause the issue
        assert 'None' not in err_msg
        # error due to empty members being in input
        assert 'may not be empty' in err_msg

    def test_field_type_string_array_input_array_with_empty_and_null_members_null_not_allowed(
        self, playbook_app: 'MockApp'
    ):
        """Test StringArray field type with Array input that contains empty and/or null members.

        An empty member of StringArray is considered to be ''.
        A null member of StringArray is considered to be None.

        By default, StringArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default.

        StringArray is configured to not accept null members, so an error is expected due to
        None being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: custom_string_array(allow_null_members=False)

        config_data = {'my_string': '#App:1234:my_string!StringArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!StringArray', ['', None], tcex)
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # error due to None being in input
        assert 'None' in err_msg
        assert 'may not be null' in err_msg

    def test_field_type_string_array_opt_input_array_with_empty_and_null_members_empty_not_allowed(
        self, playbook_app: 'MockApp'
    ):
        """Test StringArrayOptional field type with Array input that has empty and null members.

        By passing optional=True to custom_string_array, we receive a customized version of
        StringArrayOptional instead of a customized version of StringArray.

        An empty member of StringArray is considered to be ''.
        A null member of StringArray is considered to be None.

        By default, StringArrayOptional allows empty/null values to be in the array.

        StringArrayOptional is configured to not accept empty members, so an error is expected due
        to '' being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: custom_string_array(allow_empty_members=False, optional=True)

        config_data = {'my_string': '#App:1234:my_string!StringArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!StringArray', ['', None], tcex)
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # assert None did not cause the issue
        assert 'None' not in err_msg
        # error due to empty members being in input
        assert 'may not be empty' in err_msg

    def test_field_type_string_array_opt_input_array_with_empty_and_null_members_null_not_allowed(
        self, playbook_app: 'MockApp'
    ):
        """Test StringArrayOptional field type with Array input that has empty and/or null members.

        By passing optional=True to custom_string_array, we receive a customized version of
        StringArrayOptional instead of a customized version of StringArray.

        An empty member of StringArray is considered to be ''.
        A null member of StringArray is considered to be None.

        By default, StringArrayOptional allows empty/null values to be in the array.

        StringArrayOptional is configured to not accept null members, so an error is expected due to
        None being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: custom_string_array(allow_null_members=False, optional=True)

        config_data = {'my_string': '#App:1234:my_string!StringArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!StringArray', ['', None], tcex)
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # error due to None being in input
        assert 'None' in err_msg
        assert 'may not be null' in err_msg

    def test_field_type_string_array_optional_customization_with_good_values(
        self, playbook_app: 'MockApp'
    ):
        """Test StringArrayOptional field type with input that is empty string.

        By passing optional=True to custom_string_array, we receive a customized version of
        StringArrayOptional instead of a customized version of StringArray.

        This test simply asserts that passing the optional kwarg to custom_string_array indeed
        returns StringArrayOptional.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: custom_string_array(optional=True)

        config_data = {'my_string': '#App:1234:my_string!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!String', '', tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string == ['']
        assert type(tcex.inputs.data.my_string).__name__ == 'StringArrayOptionalCustom'

    def test_field_type_string_array_customization_that_handles_csv_string(
        self, playbook_app: 'MockApp'
    ):
        """Test customized StringArray field type with input that is CSV string.

        StringArray is customized to handle CSV strings, and will split the string on comma.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: custom_string_array(split_on=',')  # noqa: F722

        config_data = {'my_string': '#App:1234:my_string!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!String', 'one, two,three , ', tcex)
        tcex.inputs.add_model(PytestModel)

        # note that since strip_on_split is True (the default), any empty values that are empty
        # after the split operation are filtered out.
        assert tcex.inputs.data.my_string == ['one', 'two', 'three']

    def test_field_type_string_array_customization_that_handles_csv_string_no_split(
        self, playbook_app: 'MockApp'
    ):
        """Test customized StringArray field type with input that is CSV string.

        StringArray is customized to handle CSV strings, and will split the string on comma.
        strip_on_split is False
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: custom_string_array(split_on=',', strip_on_split=False)  # noqa: F722

        config_data = {'my_string': '#App:1234:my_string!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!String', 'one, two,three , ', tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string == ['one', ' two', 'three ', ' ']

    def test_field_type_string_array_split_oncustomization_no_effect_on_array_input(
        self, playbook_app: 'MockApp'
    ):
        """Test customized StringArray field type with input that is Array.

        StringArray is customized to handle CSV strings. No effect since input is Array.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: custom_string_array(split_on=',', strip_on_split=True)  # noqa: F722

        config_data = {'my_string': '#App:1234:my_string!StringArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value(
            'my_string', '#App:1234:my_string!StringArray', [' one, two,three , '], tcex
        )
        tcex.inputs.add_model(PytestModel)

        # input simply wrapped in list, no split operation since input is a StringArray
        assert tcex.inputs.data.my_string == [' one, two,three , ']

    @staticmethod
    def test_optional_field_type_custom_string_array(playbook_app: 'MockApp'):
        """Test custom_string_array field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.

        This test asserts that the return value of custom_string_array can also be wrapped
        with Optional[]

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[custom_string_array()]

        config_data = {'my_string': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string is None
