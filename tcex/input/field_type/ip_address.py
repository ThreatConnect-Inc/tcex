"""TcEx Framework Module"""

import ipaddress
from typing import Any, ClassVar

from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic_core import core_schema  # TYPE-CHECKING

from tcex.input.field_type.exception import InvalidInput


class IpAddress(str):
    """String Field Type"""

    strip_port: ClassVar[bool] = False

    @classmethod
    def _validate(cls, value: str, info: core_schema.ValidationInfo) -> str:
        """Run validators / modifiers on input."""
        field_name = info.field_name or '--unknown--'
        value = cls.validate_strip_port(value, field_name)
        value = cls.validate_ipaddress(value, field_name)
        return value  # noqa: RET504

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.AfterValidatorFunctionSchema:
        """Run validators / modifiers on input."""
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            field_name=handler.field_name,
        )

    @classmethod
    def validate_strip_port(cls, value: str, field_name: str) -> str:
        """Modify value when requested."""
        if cls.strip_port is True and ':' in value:
            _value, port = value.rsplit(':', 1)

            max_port_number = 65535
            try:
                if int(port) > max_port_number or int(port) < 0:
                    raise ValueError  # noqa: TRY301
            except ValueError as ex:
                raise InvalidInput(field_name, f'Invalid IP Address provided ({value}).') from ex

            value = _value

        return value

    @classmethod
    def validate_ipaddress(cls, value: str, field_name: str) -> str:
        """Raise exception if value is not a String type."""
        try:
            ipaddress.ip_address(value)
        except ValueError as ex:
            raise InvalidInput(field_name, f'Invalid IP Address provided ({value}).') from ex

        return value


def ip_address(
    strip_port: bool = False,
) -> type[IpAddress]:
    """Return configured instance of String."""
    namespace = {
        'strip_port': strip_port,
    }
    return type('ConstrainedIpAddress', (IpAddress,), namespace)
