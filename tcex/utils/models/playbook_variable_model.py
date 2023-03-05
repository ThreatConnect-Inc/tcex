"""Playbook Variable Model"""
# third-party
from pydantic import BaseModel, Field


class PlaybookVariableModel(BaseModel):
    """Playbook Variable Model

    Model for the individual parts of a playbook variable -> #App:1234:output!String.
    """

    app_type: str = Field(
        ...,
        description='The application type (e.g., App|Trigger).',
    )
    job_id: str = Field(
        ...,
        description='The job id.',
    )
    key: str = Field(
        ...,
        description='The variable key (e.g., app.api_token).',
    )
    type: str = Field(
        ...,
        description='The specific variable type (e.g., String, StringArray etc).',
    )
