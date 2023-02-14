"""TcEx JSON Model"""
# pylint: disable=no-self-argument; noqa: N805
# standard library
from enum import Enum
from pathlib import PosixPath

# third-party
from pydantic import BaseModel, validator

# first-party
from tcex.pleb.env_path import EnvPath

__all__ = ['TcexJsonModel']


class LibVersionModel(BaseModel):
    """Model for tcex_json.lib_version"""

    lib_dir: EnvPath
    python_executable: EnvPath

    class Config:
        """DataModel Config"""

        validate_assignment = True


class PackageModel(BaseModel):
    """Model for tcex_json.package"""

    app_name: str
    app_version: str | None
    excludes: list
    output_dir: str = 'target'

    @validator('excludes')
    def sorted(cls, v):
        """Change value for excludes field."""
        # the requirements.txt file is required for App Builder
        v = [e for e in v if e != 'requirements.txt']
        return list(sorted(set(v)))

    class Config:
        """DataModel Config"""

        validate_assignment = True


class TemplateTypes(str, Enum):
    """Enum for tcex.template_type"""

    api_service = 'api_service'
    external = 'external'
    organization = 'organization'
    playbook = 'playbook'
    trigger_service = 'trigger_service'
    web_api_service = 'web_api_service'
    webhook_trigger_service = 'webhook_trigger_service'


class TcexJsonModel(BaseModel):
    """TcEx JSON Model"""

    lib_versions: list[LibVersionModel] | None
    package: PackageModel
    template_name: str | None = None
    template_repo_hash: str | None = None
    template_type: TemplateTypes | None = None

    class Config:
        """DataModel Config"""

        json_encoders = {PosixPath: lambda v: v.original_value}
        use_enum_values = True
        validate_assignment = True
