#!/usr/bin/env python
"""TcEx Dependencies Command"""
# standard library
import os
import platform
import shutil
import subprocess  # nosec
import sys
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module
from pathlib import Path
from typing import List
from urllib.parse import quote

# third-party
import colorama as c

# first-party
from tcex.app_config.models.tcex_json_model import LibVersionModel

from .bin import Bin


class Dep(Bin):
    """Install dependencies for App."""

    def __init__(
        self,
        branch: str,
        no_cache_dir: bool,
        proxy_host: str,
        proxy_port: int,
        proxy_user: str,
        proxy_pass: str,
    ):
        """Initialize Class properties."""
        super().__init__()
        self.branch = branch
        self.no_cache_dir = no_cache_dir
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_user = proxy_user
        self.proxy_pass = proxy_pass

        # properties
        self.latest_version = None
        self.lib_directory = (
            f'lib_{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
        )
        self.proxy_enabled = False
        self.requirements_fqfn = Path('requirements.txt')
        self.static_lib_dir = 'lib_latest'

        # update tcex.json
        self.tj.update.multiple()

    def _build_command(self, python_executable: Path, lib_dir: Path) -> str:
        """Build the pip command for installing dependencies.

        Args:
            python_executable: The fully qualified path of the Python executable.
            lib_dir: The fully qualified path of the lib directory.

        Returns:
            list: The Python pip command with all required args.
        """
        exe_command = [
            str(python_executable),
            '-m',
            'pip',
            'install',
            '-r',
            str(self.requirements_fqfn),
            '--ignore-installed',
            '--quiet',
            '--target',
            lib_dir.name,
        ]
        if self.no_cache_dir:
            exe_command.append('--no-cache-dir')

        if self.proxy_enabled:
            # trust the pypi hosts to avoid ssl errors
            trusted_hosts = ['pypi.org', 'pypi.python.org', 'files.pythonhosted.org']

            for host in trusted_hosts:
                exe_command.append('--trusted-host')
                exe_command.append(host)

        return exe_command

    def _create_lib_latest(self) -> None:
        """Create the lib_latest symlink for App Builder."""
        if platform.system() == 'Windows':
            shutil.copytree(f'lib_{self.latest_version}', self.static_lib_dir)
        else:
            if os.path.islink(self.static_lib_dir):
                os.unlink(self.static_lib_dir)
            elif os.path.isfile(self.static_lib_dir):
                os.rmdir(self.static_lib_dir)
            os.symlink(f'lib_{self.latest_version}', self.static_lib_dir)

    @staticmethod
    def _remove_previous(fqpn: Path) -> None:
        """Remove previous lib directory recursively."""
        if os.access(fqpn, os.W_OK):
            shutil.rmtree(fqpn)

    def configure_proxy(self) -> None:
        """Configure proxy settings using environment variables."""
        if os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY'):
            # don't change proxy settings if the OS already has them configured.
            return

        if self.proxy_host is not None and self.proxy_port is not None:
            if self.proxy_user is not None and self.proxy_pass is not None:
                proxy_user = quote(self.proxy_user, safe='~')
                proxy_pass = quote(self.proxy_pass, safe='~')

                # proxy url with auth
                proxy_url = f'{proxy_user}:{proxy_pass}@{self.proxy_host}:{self.proxy_port}'
            else:
                # proxy url without auth
                proxy_url = f'{self.proxy_host}:{self.proxy_port}'

            os.putenv('HTTP_PROXY', f'http://{proxy_url}')
            os.putenv('HTTPS_PROXY', f'https://{proxy_url}')

            print(f'Using Proxy Server: {c.Fore.CYAN}{self.proxy_host}:{self.proxy_port}.')
            self.proxy_enabled = True

    def create_temp_requirements(self) -> None:
        """Create a temporary requirements.txt.

        This allows testing again a git branch instead of pulling from pypi.
        """
        # Replace tcex version with develop branch of tcex
        with self.requirements_fqfn.open() as fh:
            current_requirements = fh.read().strip().split('\n')

        self.requirements_fqfn = Path(f'temp-{self.requirements_fqfn}')
        with self.requirements_fqfn.open(mode='w') as fh:
            requirements = []
            for line in current_requirements:
                if not line:
                    continue
                if line.startswith('tcex'):
                    line = (
                        'git+https://github.com/ThreatConnect-Inc/tcex.git@'
                        f'{self.branch}#egg=tcex'
                    )
                requirements.append(line)
            fh.write('\n'.join(requirements))

    def install_deps(self) -> None:
        """Install Required Libraries using pip."""
        # check for requirements.txt
        if not self.requirements_fqfn.is_file():
            self.handle_error('A requirements.txt file is required to install modules.')

        # install all requested lib directories
        for lib_version in self.lib_versions:
            # remove lib directory from previous runs
            self._remove_previous(lib_version.lib_dir)

            if (
                not lib_version.python_executable.is_file()
                and not lib_version.python_executable.is_symlink()
            ):
                print(
                    f'{c.Style.BRIGHT}{c.Fore.RED}The Python executable '
                    f'({lib_version.python_executable}) could not be found. '
                    'Skipping building lib directory for this Python version.'
                )
                continue

            print(f'Building Lib Dir: {c.Style.BRIGHT}{c.Fore.CYAN}{lib_version.lib_dir.name}')
            exe_command = self._build_command(lib_version.python_executable, lib_version.lib_dir)

            print(f'''Running: {c.Style.BRIGHT}{c.Fore.GREEN}{' '.join(exe_command)}''')
            # recommended -> https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
            p = subprocess.Popen(
                exe_command,
                shell=False,  # nosec
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _, err = p.communicate()  # pylint: disable=unused-variable

            if p.returncode != 0:
                print(f'{c.Style.BRIGHT}{c.Fore.RED}FAIL')
                print(f'''{c.Style.BRIGHT}{c.Fore.RED}{err.decode('utf-8')}''')
                sys.exit(f'''ERROR: {err.decode('utf-8')}''')

            # TODO: [low] can this be updated to use version from model?
            # version comparison
            try:
                python_version = lib_version.lib_dir.name.split('_', 1)[1]
            except IndexError:
                python_version = None
                self.handle_error('Could not determine version from lib string.')

            # TODO: [low] investigate using sematic_version package
            # track the latest Python version
            if self.latest_version is None or StrictVersion(python_version) > StrictVersion(
                self.latest_version
            ):
                self.latest_version = python_version

        if self.branch != 'master':
            # remove temp requirements.txt file
            self.requirements_fqfn.unlink()

        # create lib_latest directory
        self._create_lib_latest()

    @property
    def lib_versions(self) -> List[LibVersionModel]:
        """Return the lib_version data required to build lib directories."""
        if self.tj.data.lib_versions:
            print(f'{c.Style.BRIGHT}Using "lib" directories defined in tcex.json file.')
            # return the python versions defined in the tcex.json file
            return self.tj.data.lib_versions

        # return the current python version
        return [
            LibVersionModel(**{'python_executable': sys.executable, 'lib_dir': self.lib_directory})
        ]
