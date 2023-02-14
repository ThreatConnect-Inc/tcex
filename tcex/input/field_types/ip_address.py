"""IP Address Field Type"""
# standard library
import ipaddress
from collections.abc import Generator

# third-party
from pydantic.fields import ModelField  # TYPE-CHECKING

# first-party
from tcex.input.field_types.exception import InvalidInput, InvalidVariableType
from tcex.utils.variables import StringVariable  # TYPE-CHECKING


class IpAddress(str):
    """String Field Type"""

    strip_port: bool = False

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Run validators / modifiers on input."""
        yield cls.validate_variable_type
        yield cls.validate_strip_port
        yield cls.validate_ipaddress

    @classmethod
    def validate_strip_port(cls, value: bytes | StringVariable, field: ModelField) -> str:
        """Modify value when requested."""
        if cls.strip_port is True:
            if ':' in value:
                _value, port = value.rsplit(':', 1)

                try:
                    if int(port) > 65535 or int(port) < 0:
                        raise ValueError()
                except ValueError:
                    raise InvalidInput(field.name, f'Invalid IP Address provided ({value}).')

                value = _value

        return value

    @classmethod
    def validate_ipaddress(cls, value: str | StringVariable, field: ModelField) -> str:
        """Raise exception if value is not a String type."""
        try:
            ipaddress.ip_address(value)
        except ValueError as ex:
            raise InvalidInput(field.name, f'Invalid IP Address provided ({value}).') from ex

        return value

    @classmethod
    def validate_variable_type(cls, value: str | StringVariable, field: ModelField) -> str:
        """Raise exception if value is not a String type."""
        if hasattr(value, '_variable_type') and value._variable_type != 'String':
            raise InvalidVariableType(
                field_name=field.name, expected_type='String', provided_type=value._variable_type
            )

        return value


def ip_address(
    strip_port: bool = False,
) -> type:
    """Return configured instance of String."""
    namespace = {
        'strip_port': strip_port,
    }
    return type('ConstrainedIpAddress', (IpAddress,), namespace)
