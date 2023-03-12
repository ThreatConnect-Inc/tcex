"""App Inputs"""
# pylint: disable=no-self-argument
# standard library
from typing import Any

# third-party
from pydantic import BaseModel, validator

# first-party
from tcex.input.field_type import (
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
from tcex.input.input import Input


class AppBaseModel(BaseModel):
    """Base model for the App containing any common inputs."""

    # pbd: String, vv: ${FILE}|${KEYCHAIN}
    password: sensitive(allow_empty=False)  # type: ignore
    # pbd: Binary|BinaryArray|KeyValue|KeyValueArray|String|StringArray|TCEntity|
    # TCEntityArray, vv: ${KEYCHAIN}|${TEXT}
    string_advanced: sensitive(allow_empty=False) = 'advanced'  # type: ignore
    # pbd: String, vv: ${TEXT}
    string_hidden: String | None
    # vv: Action 1|Action 2|Action 3|Action 4
    tc_action = 'Action 1'
    # pbd: String, vv: ${TEXT}
    username: string(allow_empty=False)  # type: ignore

    # ensure inputs that take single and array types always return an array
    _always_array = validator('string_advanced', allow_reuse=True)(always_array())

    # add entity_input validator for supported types
    _entity_input = validator('string_advanced', allow_reuse=True)(
        entity_input(only_field='value')  # type: ignore
    )


class Action1Model(AppBaseModel):
    """Action Model"""

    boolean_input_required: bool = False
    # vv: Option 1|Option 2|Option 3
    choice_required: Choice
    # pbd: String, vv: ${TEXT}
    key_value_list_required: list[KeyValue]
    # vv: Option 1|Option 2|Option 3
    multi_choice_required: list[Choice]
    # pbd: Binary|BinaryArray|KeyValue|KeyValueArray|String|StringArray|TCEntity|
    # TCEntityArray, vv: ${TEXT}
    string_required: (
        binary(allow_empty=False)  # type: ignore
        | list[binary(allow_empty=False)]  # type: ignore
        | KeyValue
        | list[KeyValue]
        | string(allow_empty=False)  # type: ignore
        | list[string(allow_empty=False)]  # type: ignore
        | TCEntity
        | list[TCEntity]
    )

    # ensure inputs that take single and array types always return an array
    _always_array = validator('string_required', allow_reuse=True)(always_array())

    # add entity_input validator for supported types
    _entity_input = validator('string_required', allow_reuse=True)(
        entity_input(only_field='value')  # type: ignore
    )


class Action2Model(AppBaseModel):
    """Action Model"""

    boolean_input_optional: bool = False
    # vv: Option 1|Option 2|Option 3
    choice_optional: Choice | None
    # pbd: String, vv: ${TEXT}
    key_value_list_optional: list[KeyValue] | None
    # vv: Option 1|Option 2|Option 3
    multi_choice_optional: list[Choice] | None
    # pbd: Any
    string_optional: Any | None


class Action3Model(AppBaseModel):
    """Action Model"""

    boolean_input_default: bool = False
    # vv: Option 1|Option 2|Option 3
    choice_default: Choice | None = 'Option 1'  # type: ignore
    # pbd: String, vv: ${TEXT}
    key_value_list_default: list[KeyValue] | None
    # vv: Option 1|Option 2|Option 3
    multi_choice_default: list[Choice] | None
    # pbd: Any
    string_default: Any | None = 'default string'


class Action4Model(AppBaseModel):
    """Action Model"""

    # pbd: String, vv: ${TEXT}
    key_value_list_expose_playbook_key_as_string: list[KeyValue] | None
    # pbd: String|StringArray, vv: ${TEXT}
    string_allow_multiple: String | list[String] | None
    # pbd: String, vv: ${FILE}|${KEYCHAIN}
    string_encrypt: Sensitive | None
    # pbd: String, vv: ${TEXT}
    string_intel_type: String | None

    # ensure inputs that take single and array types always return an array
    _always_array = validator('string_allow_multiple', allow_reuse=True)(always_array())


class AppInputs:
    """App Inputs"""

    def __init__(self, inputs: Input):
        """Initialize class properties."""
        self.inputs = inputs

    def get_model(self, tc_action: str | None = None) -> BaseModel:
        """Return the model based on the current action."""
        tc_action = tc_action or self.inputs.model_unresolved.tc_action  # type: ignore
        action_model_map = {
            'Action 1': Action1Model,
            'Action 2': Action2Model,
            'Action 3': Action3Model,
            'Action 4': Action4Model,
        }
        return action_model_map[tc_action]

    def update_inputs(self):
        """Add custom App model to inputs.

        Input will be validate when the model is added an any exceptions will
        cause the App to exit with a status code of 1.
        """
        self.inputs.add_model(self.get_model())  # type: ignore
