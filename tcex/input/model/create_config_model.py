"""TcEx Framework Module"""

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from tcex.app.config import InstallJson

# get instance of InstallJson
ij = InstallJson()


class CreateConfigModel(BaseModel):
    """Create Config Model"""

    tc_playbook_out_variables: list[str]
    trigger_id: int

    @field_validator('tc_playbook_out_variables', mode='before')
    @classmethod
    def _tc_playbook_out_variables(cls, v) -> list[str]:
        """Convert tc_playbook_out_variables into a list of strings.

        This value comes-in as a comma-separated list.
        """
        return v.split(',') if v else []

    # TODO: [low] workaround for PLAT-4393
    @model_validator(mode='before')
    @classmethod
    def _update_inputs(cls, values: dict[str, Any]):
        """Convert empty strings to None.

        Workarounds for core issues:
            - Core sends '' for field that are not populated instead of sending a null value.
            - Core sends a string for multi-value inputs instead of an array.
        """
        for field, value in values.items():
            param = ij.model.get_param(field)
            if (
                param is not None
                and (param.type.lower() == 'multichoice' or param.allow_multiple)
                and value is not None
                and not isinstance(value, list)
            ):
                values[field] = value.split(ij.model.list_delimiter or '|')

            if value == '':
                values[field] = None

        return values

    model_config = ConfigDict(extra='allow')
