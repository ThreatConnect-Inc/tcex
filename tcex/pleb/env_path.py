"""ENV Str"""
# standard library
import os
import re
from pathlib import Path
from typing import Any, Dict, Union


class _EnvPath(type(Path()), Path):  # pylint: disable=E0241
    """A stub of Path with additional attribute."""

    # store for the original value passed to EnvPath
    original_value = None


class EnvPath(Path):
    """EnvPath custom pydantic model type."""

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]):
        """."""
        field_schema.update(format='file-path')

    @classmethod
    def __get_validators__(cls) -> 'CallableGenerator':  # noqa: F821
        """."""
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, 'Path']) -> 'Path':
        """Replace any environment variables in the tcex.json file."""
        if isinstance(value, Path):
            return value

        string = str(value)
        for m in re.finditer(r'\${(env|envs|local|remote):(.*?)}', string):
            try:
                full_match = m.group(0)
                env_type = m.group(1)
                env_key = m.group(2)

                if env_type != 'env':
                    raise ValueError(f'Invalid environment type found ({env_type})')
                env_value = os.getenv(env_key)
                if env_value is not None:
                    string = string.replace(full_match, env_value)
            except IndexError:
                return string

        # convert value to Path and return original value
        p = _EnvPath(os.path.expanduser(string))
        p.original_value = value
        return p
