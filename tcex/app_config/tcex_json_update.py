"""TcEx JSON Update"""
# standard library
import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .tcex_json import TcexJson


class TcexJsonUpdate:
    """Update install.json file with current standards and schema."""

    def __init__(self, tj: 'TcexJson'):  # pylint: disable=E0601
        """Initialize class properties."""
        self.tj = tj

    def multiple(self, template: Optional[str] = None):
        """Update the contents of the tcex.json file."""

        # update app_name
        self.update_package_app_name()

        # update deprecated fields
        # self.update_deprecated_fields()

        # update package excludes
        self.update_package_excludes()

        # update package excludes
        self.update_lib_versions()

        # update template
        if template is not None:
            self.tj.template = template

        # write updated profile
        self.tj.write()

    def update_package_app_name(self):
        """Update the package app_name in the tcex.json file."""
        if (
            self.tj.model.package.app_name is None
            or self.tj.model.package.app_name in self.tj.ij.app_prefixes.values()
        ):
            # lower case name and replace prefix if already exists
            _app_name = (
                os.path.basename(os.getcwd()).lower().replace(self.tj.ij.app_prefix.lower(), '')
            )

            # replace spaces and dashes with underscores
            _app_name = _app_name.replace(' ', '_').replace('-', '_').lower()

            # title case app name
            _app_name = '_'.join([a.title() for a in _app_name.split('_')])

            # prepend appropriate App prefix (e.g., TCPB_-_)
            _app_name = f'{self.tj.ij.app_prefix}{_app_name}'

            # update App name
            self.tj.model.package.app_name = _app_name

    # def update_deprecated_fields(self):
    #     """Update deprecated fields in the tcex.json file."""
    #     deprecated_fields = ['profile_include_dirs']
    #     for d in deprecated_fields:
    #         setattr(self.tj.model, d, None)

    def update_package_excludes(self):
        """Update the excludes values in the tcex.json file."""
        for i in [
            '.gitignore',
            '.pre-commit-config.yaml',
            'local-*',
            'pyproject.toml',
            'setup.cfg',
            'tcex.json',
        ]:
            if i not in self.tj.model.package.excludes:
                # TODO: [low] pydantic doesn't seem to allow removing items from list???
                self.tj.model.package.excludes.append(i)

    def update_lib_versions(self):
        """Update the lib_versions array in the tcex.json file."""
        if os.getenv('TCEX_LIB_VERSIONS') and not self.tj.model.lib_versions:
            _lib_versions = []
            for version in os.getenv('TCEX_LIB_VERSIONS').split(','):
                _lib_versions.append(
                    {
                        'lib_dir': f'lib_${{env:{version}}}',
                        'python_executable': f'~/.pyenv/versions/${{env:{version}}}/bin/python',
                    }
                )
            self.tj.model.lib_versions = _lib_versions
