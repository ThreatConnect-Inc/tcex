"""TcEx Framework Module"""

# standard library
import logging

# first-party
from tcex.logger.trace_logger import TraceLogger

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class BaseValueError(ValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, message: str):
        """Customize the exception message."""
        # when a union of types are provided, this logs for each type that's doesn't match
        _logger.trace(f'Checking value for field {field_name}: {message}')
        super().__init__(message)


class BaseTypeError(TypeError):
    """Raise customized exception."""

    def __init__(self, field_name: str, message: str):
        """Customize the exception message."""
        # when a union of types are provided, this logs for each type that's doesn't match
        _logger.trace(f'Checking type for field {field_name}: {message}')
        super().__init__(message)


class InvalidEmptyValue(BaseValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str):
        """Customize the exception message."""
        super().__init__(field_name, 'an empty value is not allowed for this field')


class InvalidEntityType(BaseTypeError):
    """Raise customized exception."""

    def __init__(self, field_name: str, entity_type: str, value: str):
        """Customize the exception message."""
        super().__init__(field_name, f'{value} is not a {entity_type} type')


class InvalidInput(BaseValueError):
    """Raise customized exception."""

    # pylint: disable=useless-super-delegation
    def __init__(self, field_name: str, error: str):
        """Customize the exception message."""
        super().__init__(field_name, error)


class InvalidIntegerValue(BaseValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, constraint: int, operation: str):
        """Customize the exception message."""
        super().__init__(field_name, f'value must be {operation} {constraint}')


class InvalidLengthValue(BaseValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, constraint: int, operation: str):
        """Customize the exception message."""
        super().__init__(field_name, f'value must have a {operation} length of {constraint}')


class InvalidPatternValue(BaseValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, pattern: str):
        """Customize the exception message."""
        super().__init__(field_name, f'value did not match pattern "{pattern}"')


class InvalidType(BaseTypeError):
    """Raise customized exception."""

    def __init__(self, field_name: str, expected_types: str, provided_type: str):
        """Customize the exception message."""
        super().__init__(field_name, f'{provided_type} is not a {expected_types} type')


class InvalidVariableType(BaseTypeError):
    """Raise customized exception."""

    def __init__(self, field_name: str, expected_type: str, provided_type: str):
        """Customize the exception message."""
        super().__init__(field_name, f'{provided_type} is not a {expected_type} type')
