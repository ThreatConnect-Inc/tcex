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
from typing import List, Optional
from urllib.parse import quote

# third-party
import typer

# first-party
from tcex.app_config.models.tcex_json_model import LibVersionModel
from tcex.backports import cached_property
from tcex.bin.bin_abc import BinABC


class Dep(BinABC):
    """Install dependencies for App."""

    def __init__(
        self,
        branch: str,
        dev: bool,
        no_cache_dir: bool,
        pre: bool,
        proxy_host: str,
        proxy_port: int,
        proxy_user: str,
        proxy_pass: str,
    ):
        """Initialize Class properties."""
        super().__init__()
        self.branch = branch
        self.dev = dev
        self.no_cache_dir = no_cache_dir
        self.pre = pre
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
        ci_token = os.getenv('CI_JOB_TOKEN')
        self.proxy_env = {'CI_JOB_TOKEN': ci_token} if ci_token else {}
        self.requirements_fqfn_branch = None
        self.static_lib_dir = 'lib_latest'

        # update tcex.json
        self.tj.update.multiple()

    @property
    def has_requirements_lock(self):
        """Return True if requirements.lock exists."""
        return Path('requirements.lock').exists()

    def _build_command(self, python_executable: Path, lib_dir: Path) -> List[str]:
        """Build the pip command for installing dependencies.

        Args:
            python_executable: The fully qualified path of the Python executable.
            lib_dir: The fully qualified path of the lib directory.

        Returns:
            list: The Python pip command with all required args.
        """
        # support temp (branch) requirements.txt file
        _requirements_fqfn = str(self.requirements_fqfn)
        if self.requirements_fqfn_branch:
            _requirements_fqfn = str(self.requirements_fqfn_branch)

        exe_command = [
            str(python_executable),
            '-m',
            'pip',
            'install',
            '-r',
            _requirements_fqfn,
            '--ignore-installed',
            '--quiet',
            '--target',
            lib_dir.name,
        ]
        if self.no_cache_dir:
            exe_command.append('--no-cache-dir')
        if self.pre:
            exe_command.append('--pre')
        if self.proxy_enabled:
            # trust the pypi hosts to avoid ssl errors
            trusted_hosts = ['pypi.org', 'pypi.python.org', 'files.pythonhosted.org']

            for host in trusted_hosts:
                exe_command.append('--trusted-host')
                exe_command.append(host)

        return exe_command

    def _create_lib_latest(self):
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
    def _remove_previous(fqpn: Path):
        """Remove previous lib directory recursively."""
        if os.access(fqpn, os.W_OK):
            shutil.rmtree(fqpn)

    def configure_proxy(self):
        """Configure proxy settings using environment variables."""
        if os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY'):
            # don't change proxy settings if the OS already has them configured.
            return

        if self.proxy_host is not None and self.proxy_port is not None:
            # proxy url without auth
            proxy_url = f'{self.proxy_host}:{self.proxy_port}'
            if self.proxy_user is not None and self.proxy_pass is not None:
                proxy_user = quote(self.proxy_user, safe='~')
                proxy_pass = quote(self.proxy_pass, safe='~')

                # proxy url with auth
                proxy_url = f'{proxy_user}:{proxy_pass}@{proxy_url}'

            # update proxy properties
            self.proxy_enabled = True
            self.proxy_env.update(
                {
                    'HTTP_PROXY': f'http://{proxy_url}',
                    'HTTPS_PROXY': f'http://{proxy_url}',
                }
            )

            # display proxy setting
            self.print_setting('Using Proxy Server', f'{self.proxy_host}:{self.proxy_port}')

    def create_requirements_lock(self):
        """Create the requirements.lock file."""
        with Path('requirements.lock').open(mode='w') as fh:
            self.print_setting('Lock File Created', 'requirements.lock')
            fh.write(self.requirements_lock)
            fh.write('')

    def create_temp_requirements(self):
        """Create a temporary requirements.txt.

        This allows testing against a git branch instead of pulling from pypi.
        """
        _requirements_fqfn = Path('requirements.txt')
        if self.has_requirements_lock:
            _requirements_fqfn = Path('requirements.lock')

        # Replace tcex version with develop branch of tcex
        with _requirements_fqfn.open() as fh:
            current_requirements = fh.read().strip().split('\n')

        self.requirements_fqfn_branch = Path(f'temp-{_requirements_fqfn}')
        with self.requirements_fqfn_branch.open(mode='w') as fh:
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

        # display branch setting
        self.print_setting('Using Branch', self.branch)

    def install_deps(self):
        """Install Required Libraries using pip."""
        # check for requirements.txt
        if not self.requirements_fqfn.is_file():
            self.handle_error(
                f'A {str(self.requirements_fqfn)} file is required to install modules.'
            )

        # update requirements_dev.txt file
        self.update_requirements_dev_txt()

        # install all requested lib directories
        for lib_version in self.lib_versions:
            # remove lib directory from previous runs
            self._remove_previous(lib_version.lib_dir)

            if (
                not lib_version.python_executable.is_file()
                and not lib_version.python_executable.is_symlink()
            ):

                # display error
                typer.secho(
                    f'The Python executable ({lib_version.python_executable}) could not be found. '
                    'Skipping building lib directory for this Python version.',
                    fg=typer.colors.YELLOW,
                )
                continue

            # display lib dir setting
            self.print_setting('Lib Dir', f'{lib_version.lib_dir.name}')

            # build the sub process command
            exe_command = self._build_command(lib_version.python_executable, lib_version.lib_dir)

            # display command setting
            self.print_setting('Running', f'''{' '.join(exe_command)}''', fg_color='GREEN')

            # recommended -> https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
            p = subprocess.Popen(  # pylint: disable=consider-using-with
                exe_command,
                shell=False,  # nosec
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=self.proxy_env,
            )
            _, err = p.communicate()  # pylint: disable=unused-variable

            if p.returncode != 0:
                # display error
                err = err.decode('utf-8')
                failure_display = typer.style(
                    f'Failure: {err}', fg=typer.colors.WHITE, bg=typer.colors.RED
                )
                typer.echo(f'{failure_display}')
                sys.exit(1)

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

        if self.requirements_fqfn_branch:
            # remove temp requirements.txt file
            self.requirements_fqfn_branch.unlink()

        # create lib_latest directory
        self._create_lib_latest()

        if self.has_requirements_lock is False:
            self.create_requirements_lock()

    @property
    def lib_versions(self) -> List[LibVersionModel]:
        """Return the lib_version data required to build lib directories."""
        if self.tj.model.lib_versions:
            self.print_setting('Python Version', 'using version(s) defined in tcex.json')

            # return the python versions defined in the tcex.json file
            return self.tj.model.lib_versions

        # return the current python version
        return [
            LibVersionModel(**{'python_executable': sys.executable, 'lib_dir': self.lib_directory})
        ]

    @cached_property
    def requirements_fqfn(self):
        """Return the appropriate requirements.txt file."""
        if self.dev:
            _requirements_file = Path('requirements_dev.txt')
        elif self.has_requirements_lock:
            _requirements_file = Path('requirements.lock')
        else:
            _requirements_file = Path('requirements.txt')

        self.print_setting('Requirements File', str(_requirements_file))
        return _requirements_file

    @property
    def requirements_lock(self) -> str:
        """Return python packages for requirements.txt."""
        lib_directories = [lib_model.lib_dir for lib_model in self.lib_versions]

        # if we only have one current Python version building the requirements.txt file
        # is straight forward, just include all packages pinned to the current version.
        if len(lib_directories) == 1:
            _requirements = self.requirements_lock_data(lib_directories[0])
            # sort packages alphabetically
            return '\n'.join(sorted(_requirements.splitlines()))

        requirements = {}
        source_requirements = set()
        for lib_dir in lib_directories:
            # extract python major.minor
            python_version = str(lib_dir).replace('lib_', '')
            python_version_major = python_version.split('.', 1)[0]
            python_version_minor = python_version.split('.', 2)[1]

            for requirement in self.requirements_lock_data(lib_dir).splitlines():
                if not requirement:
                    # skip empty lines
                    continue

                try:
                    if ' @ ' in requirement:
                        source_requirements.add(requirement)
                    else:
                        package_name = requirement.split('==')[0]
                        package_version = requirement.split('==')[1]
                        requirements.setdefault(package_name, {})
                        requirements[package_name][
                            f'{python_version_major}.{python_version_minor}'
                        ] = package_version
                except Exception as ex:
                    self.log.error(
                        f'event=get-requirements-txt, requirement={requirement}, error="{ex}"'
                    )
        _requirements = self.requirements_lock_diff(requirements, len(lib_directories))
        _requirements.extend(source_requirements)
        return '\n'.join(sorted(_requirements))

    def requirements_lock_data(self, lib_dir: str) -> str:
        """Return the Python packages for the provided directory."""
        lib_dir_path = os.path.join(self.app_path, lib_dir)
        cmd = f'pip freeze --path "{lib_dir_path}"'
        self.log.debug(f'event=get-requirements-lock-data, cmd={cmd}')
        try:
            output = subprocess.run(  # pylint: disable=subprocess-run-check
                cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE  # nosec
            )
        except Exception as ex:
            self.log.error(f'event=pip-freeze, error="{ex}"')
            typer.echo('Failure: could not get requirements lock data.')
            sys.exit(1)

        if output.returncode != 0:
            self.log.error(f'event=pip-freeze, stderr="{output.stderr}"')

        return output.stdout.decode('utf-8')

    def requirements_lock_diff(self, package_data: dict, python_version_count: int) -> List[str]:
        """Diff the package data, returning the appropriate requirements.lock data."""
        requirements_lock = []
        for package_name, package_version_data in package_data.items():
            if len(package_version_data) < python_version_count:
                # if the package is defined for less than the total number of python versions
                # supported then the package is not required for one or more python versions
                # and must be pinned with the applicable python version defined.
                for python_version, package_version in package_version_data.items():
                    requirements_lock.append(
                        self.requirements_lock_line(package_name, package_version, python_version)
                    )
            elif all(
                x == list(package_version_data.values())[0] for x in package_version_data.values()
            ):
                # if the package version is the same for all python versions then
                # it only needs to be defined once in the requirements.txt file.
                for python_version, package_version in package_version_data.items():
                    requirements_lock.append(
                        self.requirements_lock_line(package_name, package_version)
                    )

                    # only add once
                    break
            else:
                # if the package version is different for one or more versions of python then the
                # python_version must be specified in the requirements.txt file.
                for python_version, package_version in package_version_data.items():
                    requirements_lock.append(
                        self.requirements_lock_line(package_name, package_version, python_version)
                    )
        return requirements_lock

    @staticmethod
    def requirements_lock_line(
        package_name: str, package_version: str, python_version: Optional[str] = None
    ) -> str:
        """Return a string to insert into the requirements.txt file."""
        if python_version is None:
            return f'{package_name}=={package_version}'
        return f'{package_name}=={package_version}; python_version == \'{python_version}\''

    @staticmethod
    def update_requirements_dev_txt():
        """Update the requirements_dev.txt file to support lock file."""
        if os.path.isfile('requirements_dev.txt'):
            with open('requirements_dev.txt', mode='r+') as fh:
                _lines = ''
                for line in fh.readlines():
                    _lines += line.replace('requirements.txt', 'requirements.lock')

                # write back
                fh.seek(0)
                fh.write(_lines)
                fh.truncate()
