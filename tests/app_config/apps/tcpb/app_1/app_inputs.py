"""App Inputs"""
# pylint: disable=no-self-argument, no-self-use
# standard library
from typing import Any, List, Optional, Union

# third-party
from pydantic import BaseModel, validator

# first-party
from tcex.input.field_types import (
    Choice,
    KeyValue,
    Sensitive,
    String,
    TCEntity,
    always_array,
    binary,
    entity_input,
    sensitive,
    string,
)


class AppBaseModel(BaseModel):
    """Base model for the App containing any common inputs."""

    # pbd: String, vv: ${FILE}|${KEYCHAIN}
    password: sensitive(allow_empty=False)
    # pbd: Binary|BinaryArray|KeyValue|KeyValueArray|String|StringArray|TCEntity|
    # TCEntityArray, vv: ${KEYCHAIN}|${TEXT}
    string_advanced: sensitive(allow_empty=False) = 'advanced'
    # pbd: String, vv: ${TEXT}
    string_hidden: Optional[String]
    # vv: Action 1|Action 2|Action 3|Action 4
    tc_action: Choice = 'Action 1'
    # pbd: String, vv: ${TEXT}
    username: string(allow_empty=False)

    # ensure inputs that take single and array types always return an array
    _always_array = validator('string_advanced', allow_reuse=True)(always_array())

    # add entity_input validator for supported types
    _entity_input = validator('string_advanced', allow_reuse=True)(entity_input(only_value=True))


class Action1Model(AppBaseModel):
    """Action Model"""

    boolean_input_required: bool = False
    # vv: Option 1|Option 2|Option 3
    choice_required: Choice
    # pbd: String, vv: ${TEXT}
    key_value_list_required: List[KeyValue]
    # vv: Option 1|Option 2|Option 3
    multi_choice_required: List[Choice]
    # pbd: Binary|BinaryArray|KeyValue|KeyValueArray|String|StringArray|TCEntity|
    # TCEntityArray, vv: ${TEXT}
    string_required: Union[
        binary(allow_empty=False),
        List[binary(allow_empty=False)],
        KeyValue,
        List[KeyValue],
        string(allow_empty=False),
        List[string(allow_empty=False)],
        TCEntity,
        List[TCEntity],
    ]

    # ensure inputs that take single and array types always return an array
    _always_array = validator('string_required', allow_reuse=True)(always_array())

    # add entity_input validator for supported types
    _entity_input = validator('string_required', allow_reuse=True)(entity_input(only_value=True))


class Action2Model(AppBaseModel):
    """Action Model"""

    boolean_input_optional: bool = False
    # vv: Option 1|Option 2|Option 3
    choice_optional: Optional[Choice]
    # pbd: String, vv: ${TEXT}
    key_value_list_optional: Optional[List[KeyValue]]
    # vv: Option 1|Option 2|Option 3
    multi_choice_optional: Optional[List[Choice]]
    # pbd: Any
    string_optional: Optional[Any]


class Action3Model(AppBaseModel):
    """Action Model"""

    boolean_input_default: bool = False
    # vv: Option 1|Option 2|Option 3
    choice_default: Optional[Choice] = 'Option 1'
    # pbd: String, vv: ${TEXT}
    key_value_list_default: Optional[List[KeyValue]]
    # vv: Option 1|Option 2|Option 3
    multi_choice_default: Optional[List[Choice]]
    # pbd: Any
    string_default: Optional[Any] = 'default string'


class Action4Model(AppBaseModel):
    """Action Model"""

    # pbd: String, vv: ${TEXT}
    key_value_list_expose_playbook_key_as_string: Optional[List[KeyValue]]
    # pbd: String|StringArray, vv: ${TEXT}
    string_allow_multiple: Optional[Union[String, List[String]]]
    # pbd: String, vv: ${FILE}|${KEYCHAIN}
    string_encrypt: Optional[Sensitive]
    # pbd: String, vv: ${TEXT}
    string_intel_type: Optional[String]

    # ensure inputs that take single and array types always return an array
    _always_array = validator('string_allow_multiple', allow_reuse=True)(always_array())


class AppInputs:
    """App Inputs"""

    def __init__(self, inputs: 'BaseModel') -> None:
        """Initialize class properties."""
        self.inputs = inputs

    def get_model(self, tc_action: Optional[str] = None) -> 'BaseModel':
        """Return the model based on the current action."""
        tc_action = tc_action or self.inputs.model_unresolved.tc_action
        action_model_map = {
            'Action 1': Action1Model,
            'Action 2': Action2Model,
            'Action 3': Action3Model,
            'Action 4': Action4Model,
        }
        return action_model_map.get(tc_action)

    def update_inputs(self) -> None:
        """Add custom App models to inputs.

        Input will be validate when the model is added an any exceptions will
        cause the App to exit with a status code of 1.
        """
        self.inputs.add_model(self.get_model())
