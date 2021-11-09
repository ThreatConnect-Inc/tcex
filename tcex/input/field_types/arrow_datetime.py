"""Arrow Datetime Field"""
# standard library
from typing import Any, Callable

# third-party
import arrow

# first-party
from tcex.utils import Utils


class ArrowDateTime(arrow.Arrow):
    """Arrow Datetime Field Type"""

    @classmethod
    def _validate(cls, value: Any) -> 'arrow.Arrow':
        """Pydantic validate method."""
        try:
            return Utils.any_to_arrow(value)
        except RuntimeError as ex:
            raise ValueError(str(ex)) from ex

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Define one or more validators for Pydantic custom type."""
        yield cls._validate
