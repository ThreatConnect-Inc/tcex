"""Exception that can be raised during input validation."""


class ValidationError(Exception):
    """Exception that can be raised during input validation."""

    def __init__(self, message: str):
        """Initialize a ValidationError.

        Args:
            message: A context-specific message explaining the input validation failure.
        """
        super().__init__()
        self.message = message
