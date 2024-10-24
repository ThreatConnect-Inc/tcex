"""TcEx Framework Module"""

# standard library
import ipaddress
from collections.abc import Generator

# third-party
from pydantic.fields import ModelField  # TYPE-CHECKING

# first-party
from tcex.input.field_type.exception import InvalidInput


class IpAddress(str):
    """String Field Type"""

    strip_port: bool = False

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Run validators / modifiers on input."""
        yield cls.validate_strip_port
        yield cls.validate_ipaddress

    @classmethod
    def validate_strip_port(cls, value: str, field: ModelField) -> str:
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
    def validate_ipaddress(cls, value: str, field: ModelField) -> str:
        """Raise exception if value is not a String type."""
        try:
            ipaddress.ip_address(value)
        except ValueError as ex:
            raise InvalidInput(field.name, f'Invalid IP Address provided ({value}).') from ex

        return value


def ip_address(
    strip_port: bool = False,
) -> type[IpAddress]:
    """Return configured instance of String."""
    namespace = {
        'strip_port': strip_port,
    }
    return type('ConstrainedIpAddress', (IpAddress,), namespace)
