"""Create Config Model"""
# pylint: disable=no-self-argument,no-self-use
# standard library
from typing import Any, Dict, List

# third-party
from pydantic import BaseModel, root_validator, validator


class CreateConfigModel(BaseModel):
    """Create Config Model"""

    tc_playbook_out_variables: List[str]
    trigger_id: int

    @validator('tc_playbook_out_variables', pre=True)
    def listify_tc_playbook_out_variables(cls, v):
        """Convert tc_playbook_out_variables into a list of strings.

        This value comes-in as a comma-seperated list.
        """
        return v.split(',') if v else []

    # TODO: [low] workaround for PLAT-4393
    @root_validator(pre=True)
    def empty_str_to_none(cls, values: Dict[str, Any]):
        """Convert empty strings to None.

        Core sends '' for field that are not populated instead of sending a null value.
        """
        return {k: v if v != '' else None for k, v in values.items()}
