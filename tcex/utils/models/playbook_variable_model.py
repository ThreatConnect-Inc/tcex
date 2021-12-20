"""Playbook Variable Model"""
# third-party
from pydantic import BaseModel, Field


class PlaybookVariableModel(BaseModel):
    """Playbook Variable Model

    Parsing the variable into it individual parts:
    #App:1234:output!String
    """

    app_type: str = Field(
        None,
        description='The application type (e.g., App|Trigger).',
    )
    job_id: str = Field(
        None,
        description='The job id.',
    )
    key: str = Field(
        None,
        description='The variable key (e.g., app.api_token).',
    )
    type: str = Field(
        None,
        description='The specific variable type (e.g., String, StringArray etc).',
    )
