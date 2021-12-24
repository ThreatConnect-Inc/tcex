"""Field type exception classes"""


class InvalidEmptyValue(ValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str):
        """Customize the exception message."""
        super().__init__(
            f'Invalid input for field {field_name}: an empty value is not allowed for this field.'
        )


class InvalidEntityType(ValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, entity_type: str, value: str):
        """Customize the exception message."""
        super().__init__(
            f'Invalid input for field {field_name}: {value} is not a {entity_type} type.'
        )


class InvalidInput(ValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, error: str):
        """Customize the exception message."""
        super().__init__(f'Invalid input for field {field_name}: {error}')


class InvalidIntegerValue(ValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, constraint: int, operation: str):
        """Customize the exception message."""
        super().__init__(
            f'Invalid input for field {field_name}: value must be {operation} {constraint}.'
        )


class InvalidLengthValue(ValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, constraint: int, operation: str):
        """Customize the exception message."""
        super().__init__(
            f'Invalid input for field {field_name}: value must '
            f'have a {operation} length of {constraint}.'
        )


class InvalidPatternValue(ValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, pattern: str):
        """Customize the exception message."""
        super().__init__(
            f'Invalid input for field {field_name}: value did not match pattern "{pattern}".'
        )


class InvalidType(ValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, expected_types: str, provided_type: str):
        """Customize the exception message."""
        super().__init__(
            f'Invalid input for field {field_name}: {provided_type} is not a {expected_types} type.'
        )


class InvalidVariableType(ValueError):
    """Raise customized exception."""

    def __init__(self, field_name: str, expected_type: str, provided_type: str):
        """Customize the exception message."""
        super().__init__(
            f'Invalid input for field {field_name}: {provided_type} is not a {expected_type} type.'
        )
