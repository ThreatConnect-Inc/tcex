"""Create Config Model"""
# pylint: disable=no-self-argument,no-self-use
# standard library
from typing import Any, Dict

# third-party
from pydantic import BaseModel, root_validator


class CreateConfigModel(BaseModel):
    """Create Config Model"""

    # TODO: [low] workaround for PLAT-4393
    @root_validator(pre=True)
    def empty_str_to_none(cls, values: Dict[str, Any]):
        """Convert empty strings to None.

        Core sends '' for field that are not populated instead of sending a null value.
        """
        return {k: v if v != '' else None for k, v in values.items()}
