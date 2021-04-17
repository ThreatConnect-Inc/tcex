"""TcEx JSON Model"""
# standard library
from typing import List, Optional

# third-party
from pydantic import BaseModel, validator

__all__ = ['TcexJsonModel']


class LibVersionModel(BaseModel):
    """Model for tcex_json.lib_version"""

    lib_dir: str
    python_executable: str


class PackageModel(BaseModel):
    """Model for tcex_json.package"""

    app_name: str
    app_version: Optional[str]
    excludes: list

    @validator('excludes')
    def sorted(cls, v):  # pylint: disable=E0213,R0201
        """Change value for excludes field."""
        # the requirements.txt file is required for App Builder
        v = [e for e in v if e != 'requirements.txt']
        return list(sorted(set(v)))


class TcexJsonModel(BaseModel):
    """TcEx JSON Model"""

    lib_versions: Optional[List[LibVersionModel]]
    package: PackageModel
    template: str
    # deprecated
    profile_include_dirs: Optional[list]
