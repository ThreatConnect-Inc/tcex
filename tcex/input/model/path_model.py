"""TcEx Framework Module"""

# standard library
import tempfile
import uuid
from pathlib import Path

# third-party
from pydantic import BaseModel, Field


class PathModel(BaseModel):
    """Path Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * WebhookTriggerService
    * TriggerService
    """

    #
    # ThreatConnect Provided Inputs
    #

    tc_in_path: Path = Field(
        Path(tempfile.gettempdir()),
        description='The path to the Apps "in" directory.',
        inclusion_reason='runtimeLevel',
    )
    tc_log_path: Path = Field(
        Path(tempfile.gettempdir()),
        description='The path to the Apps "log" directory.',
        inclusion_reason='runtimeLevel',
    )
    tc_out_path: Path = Field(
        Path(tempfile.gettempdir()),
        description='The path to the Apps "out" directory.',
        inclusion_reason='runtimeLevel',
    )
    tc_temp_path: Path = Field(
        Path(tempfile.gettempdir()),
        description='The path to the Apps "tmp" directory.',
        inclusion_reason='runtimeLevel',
    )

    @property
    def tc_session_id(self) -> str:
        """Return the current session id."""
        if self.tc_out_path.parent.name:
            return self.tc_in_path.parent.name

        # handle running locally
        session_id_filename = self.tc_out_path / 'tc_session_id'
        if not session_id_filename.exists():
            session_id_filename.write_text(str(uuid.uuid4()))
        return session_id_filename.read_text().strip()
