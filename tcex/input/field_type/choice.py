"""TcEx Framework Module"""

# standard library
from typing import Any

# third-party
from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic.dataclasses import dataclass
from pydantic_core import core_schema

# first-party
from tcex.input.field_type.edit_choice import EditChoice


@dataclass(frozen=True, init=False)
class Choice(EditChoice):
    """Choice Field Type"""

    @classmethod
    def _validate(cls, value: str, info: core_schema.ValidationInfo) -> str | None:
        """Run validators / modifiers on input."""
        if info.field_name is None:
            return value

        field_name = info.field_name

        # First run the parent EditChoice validation
        value = super()._validate(value, info)

        # Then apply the choice-specific modifier
        return cls.modifier_select(value, field_name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.ChainSchema:
        #  ) -> core_schema.AfterValidatorFunctionSchema:
        """Run validators / modifiers on input."""
        _ = core_schema.no_info_before_validator_function(
            function=cls.update_select,
            schema=core_schema.str_schema(),
        )
        fn_schema = core_schema.with_info_plain_validator_function(function=cls.modifier_select)
        return core_schema.chain_schema(
            [
                core_schema.str_schema(),
                fn_schema,
            ]
        )
        # return schema
        # return core_schema.with_info_after_validator_function(
        #     cls._validate,
        #     core_schema.str_schema(),
        #     field_name=handler.field_name,
        # )

    @staticmethod
    def update_select(value: str) -> str | None:
        """."""
        return None if value == '-- Select --' else value

    @classmethod
    # def modifier_select(cls, value: str, field_name: str) -> str | None:
    def modifier_select(cls, value: str, _info: core_schema.ValidationInfo) -> str | None:
        """Modify value if -- Select -- option is selected.

        Job Apps: If not selection None is sent.
        PB Apps: '-- Select --' has to be added to validValues by developer.
        """
        _value = value
        if _value == '-- Select --':
            # TODO: [high] figure out what this did before
            # if cls.model_fields[info.field_name].is_required():
            #     raise InvalidInput(field_name, f'{_value} is not a valid choice.')
            # if field_name.allow_none is False:
            #     raise InvalidInput(field_name, f'{_value} is not a valid choice.')
            _value = None

        return _value


def choice(value_transformations: dict[str, str] | None = None) -> type[Choice]:
    """Return configured instance of String.

    :param value_transformations: dictionary that dictates how a choice should be transformed.
    Dictionary keys should be the field's valid values as defined in the install.json. Example:

    value_transformations: {'my_choice': 'My Choice'}

    If this field were to be initialized with 'my_choice', then the final value found in the input
    model would be 'My Choice'.
    """
    namespace = {'_value_transformations': value_transformations}
    return type('CustomChoice', (Choice,), namespace)
