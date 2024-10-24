"""TcEx Framework Module"""

# pylint: disable=no-self-argument
# standard library
from typing import Any

# third-party
from pydantic import BaseModel, Extra, root_validator, validator

# first-party
from tcex.app.config import InstallJson

# get instance of InstallJson
ij = InstallJson()


class CreateConfigModel(BaseModel):
    """Create Config Model"""

    tc_playbook_out_variables: list[str]
    trigger_id: int

    @validator('tc_playbook_out_variables', pre=True)
    def _tc_playbook_out_variables(cls, v) -> list[str]:
        """Convert tc_playbook_out_variables into a list of strings.

        This value comes-in as a comma-separated list.
        """
        return v.split(',') if v else []

    # TODO: [low] workaround for PLAT-4393
    @root_validator(pre=True)
    def _update_inputs(cls, values: dict[str, Any]):
        """Convert empty strings to None.

        Workarounds for core issues:
            - Core sends '' for field that are not populated instead of sending a null value.
            - Core sends a string for multi-value inputs instead of an array.
        """
        for field, value in values.items():
            param = ij.model.get_param(field)
            if param is not None and (param.type.lower() == 'multichoice' or param.allow_multiple):
                if value is not None and not isinstance(value, list):
                    values[field] = value.split(ij.model.list_delimiter or '|')

            if value == '':
                values[field] = None

        return values

    class Config:
        """Model Config"""

        extra = Extra.allow
