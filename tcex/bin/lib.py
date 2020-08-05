#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Library Builder."""
# standard library
import os
import platform
import shutil
import subprocess  # nosec
import sys
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module
from urllib.parse import quote

# third-party
import colorama as c

from .bin import Bin


class Lib(Bin):
    """Install Required Modules for App.

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Initialize Class properties.

        Args:
            _args (namespace): The argparser args Namespace.
        """
        super().__init__(_args)

        # properties
        self.latest_version = None
        self.lib_directory = (
            f'lib_{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
        )
        self.requirements_file = 'requirements.txt'
        self.static_lib_dir = 'lib_latest'
        self.use_temp_requirements_file = False

        # update tcex.json
        self.tj.update()

    def _build_command(self, python_executable, lib_dir_fq, proxy_enabled):
        """Build the pip command for installing dependencies.

        Args:
            python_executable (str): The fully qualified path of the Python executable.
            lib_dir_fq (str): The fully qualified path of the lib directory.

        Returns:
            list: The Python pip command with all required args.
        """
        exe_command = [
            os.path.expanduser(python_executable),
            '-m',
            'pip',
            'install',
            '-r',
            self.requirements_file,
            '--ignore-installed',
            '--quiet',
            '--target',
            lib_dir_fq,
        ]
        if self.args.no_cache_dir:
            exe_command.append('--no-cache-dir')

        if proxy_enabled:
            # trust the pypi hosts to avoid ssl errors
            trusted_hosts = ['pypi.org', 'pypi.python.org', 'files.pythonhosted.org']

            for host in trusted_hosts:
                exe_command.append('--trusted-host')
                exe_command.append(host)

        return exe_command

    def _configure_proxy(self):
        """Configure proxy settings using environment variables."""
        if os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY'):
            # TODO: is this appropriate?
            # don't change proxy settings if the OS already has them configured.
            return True

        proxy_enabled = False
        if self.args.proxy_host is not None and self.args.proxy_port is not None:
            if self.args.proxy_user is not None and self.args.proxy_pass is not None:
                proxy_user = quote(self.args.proxy_user, safe='~')
                proxy_pass = quote(self.args.proxy_pass, safe='~')

                # proxy url with auth
                proxy_url = (
                    f'{proxy_user}:{proxy_pass}@{self.args.proxy_host}:{self.args.proxy_port}'
                )
            else:
                # proxy url without auth
                proxy_url = f'{self.args.proxy_host}:{self.args.proxy_port}'

            os.putenv('HTTP_PROXY', f'http://{proxy_url}')
            os.putenv('HTTPS_PROXY', f'https://{proxy_url}')

            print(
                f'Using Proxy Server: {c.Fore.CYAN}{self.args.proxy_host}:{self.args.proxy_port}.'
            )
            proxy_enabled = True
        return proxy_enabled

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

    def _create_temp_requirements(self):
        """Create a temporary requirements.txt.

        This allows testing again a git branch instead of pulling from pypi.
        """
        self.use_temp_requirements_file = True
        # Replace tcex version with develop branch of tcex
        with open(self.requirements_file, 'r') as fh:
            current_requirements = fh.read().strip().split('\n')

        self.requirements_file = f'temp-{self.requirements_file}'
        with open(self.requirements_file, 'w') as fh:
            new_requirements = ''
            for line in current_requirements:
                if not line:
                    continue
                if line.startswith('tcex'):
                    line = (
                        'git+https://github.com/ThreatConnect-Inc/tcex.git@'
                        f'{self.args.branch}#egg=tcex'
                    )
                # print('line', line)
                new_requirements += f'{line}\n'
            fh.write(new_requirements)

    def install_libs(self):
        """Install Required Libraries using pip."""
        # check for requirements.txt
        if not os.path.isfile(self.requirements_file):
            self.handle_error('A requirements.txt file is required to install modules.')

        # if branch arg is provide use git branch instead of pypi
        if self.args.branch is not None:
            self._create_temp_requirements()

        # default or current python version
        lib_data = [{'python_executable': sys.executable, 'lib_dir': self.lib_directory}]
        if self.tj.lib_versions:
            # overwrite default with config data
            lib_data = self.tj.lib_versions
            print(f'{c.Style.BRIGHT}Using "lib" directories defined in tcex.json file.')

        # configure proxy settings
        proxy_enabled = self._configure_proxy()

        # install all requested lib directories
        for data in lib_data:
            lib_dir = data.get('lib_dir')
            lib_dir_fq = os.path.join(self.app_path, lib_dir)

            if os.access(lib_dir_fq, os.W_OK):
                # remove lib directory from previous runs
                shutil.rmtree(lib_dir_fq)

            # replace env vars with env val in the python executable
            python_executable = os.path.expanduser(data.get('python_executable'))

            if not os.path.isfile(python_executable) and not os.path.islink(python_executable):
                print(
                    f'{c.Style.BRIGHT}{c.Fore.RED}The link Python executable ({python_executable}) '
                    f'could not be found. Skipping building lib directory for this Python version.'
                )
                continue

            print(f'Building Lib Dir: {c.Style.BRIGHT}{c.Fore.CYAN}{lib_dir_fq}')
            exe_command = self._build_command(python_executable, lib_dir_fq, proxy_enabled)

            print(f"Running: {c.Style.BRIGHT}{c.Fore.GREEN}{' '.join(exe_command)}")
            p = subprocess.Popen(
                exe_command,
                shell=False,  # nosec
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            out, err = p.communicate()  # pylint: disable=unused-variable

            if p.returncode != 0:
                print(f'{c.Style.BRIGHT}{c.Fore.RED}FAIL')
                print(f"{c.Style.BRIGHT}{c.Fore.RED}{err.decode('utf-8')}")
                sys.exit(f"ERROR: {err.decode('utf-8')}")

            # version comparison
            try:
                python_version = lib_dir.split('_', 1)[1]
            except IndexError:
                python_version = None
                self.handle_error('Could not determine version from lib string.')

            # track the latest Python version
            if self.latest_version is None:
                self.latest_version = python_version
            elif StrictVersion(python_version) > StrictVersion(self.latest_version):
                self.latest_version = python_version

        # cleanup temp file if required
        if self.use_temp_requirements_file:
            os.remove(self.requirements_file)

        # create lib_latest
        self._create_lib_latest()
