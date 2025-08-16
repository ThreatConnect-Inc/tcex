"""TcEx Framework Module"""

# standard library
from dataclasses import dataclass
from typing import Any, ClassVar

# third-party
from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic_core import core_schema

# first-party
from tcex.input.field_type.exception import InvalidType


@dataclass(frozen=True)
class Integer(int):
    """Integer Field Type"""

    ge: ClassVar[int | None] = None
    gt: ClassVar[int | None] = None
    le: ClassVar[int | None] = None
    lt: ClassVar[int | None] = None

    # @classmethod
    # def __modify_schema__(cls, field_schema: dict[str, Any]):
    #     """Modify the field schema."""

    #     def update_not_none(mapping: dict[Any, Any], **update: Any):
    #         mapping.update({k: v for k, v in update.items() if v is not None})

    #     update_not_none(
    #         field_schema,
    #         exclusiveMinimum=cls.gt,
    #         exclusiveMaximum=cls.lt,
    #         minimum=cls.ge,
    #         maximum=cls.le,
    #     )

    @classmethod
    def _validate(cls, value: int | str, info: core_schema.ValidationInfo) -> int:
        """Run validators / modifiers on input."""
        field_name = info.field_name or '--unknown--'
        return cls.validate_type(value, field_name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.AfterValidatorFunctionSchema:
        """Run validators / modifiers on input."""
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.int_schema(ge=cls.ge, gt=cls.gt, le=cls.le, lt=cls.lt),
            field_name=handler.field_name,
        )

    @classmethod
    def validate_type(cls, value: int | str, field_name: str) -> int:
        """Raise exception if value is not a String type."""
        if not isinstance(value, int | str):
            raise InvalidType(
                field_name=field_name, expected_types='(int, str)', provided_type=type(value)
            )
        return int(value)


def integer(
    gt: int | None = None,
    ge: int | None = None,
    lt: int | None = None,
    le: int | None = None,
) -> type[Integer]:
    """Return configured instance of String."""
    namespace = {
        'gt': gt,
        'ge': ge,
        'lt': lt,
        'le': le,
    }
    return type('ConstrainedInteger', (Integer,), namespace)
