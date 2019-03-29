#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Library Builder."""
import os
import re
import platform
import shutil
import subprocess
import sys
from distutils.version import StrictVersion  # pylint: disable=E0611

try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3

import colorama as c

from .tcex_bin import TcExBin


class TcExLib(TcExBin):
    """Install Required Modules for App.

    Args:
        _args (namespace): The argparser args Namespace.
    """

    def __init__(self, _args):
        """Initialize Class properties.

        Args:
            _args (namespace): The argparser args Namespace.
        """
        super(TcExLib, self).__init__(_args)

        # properties
        self.latest_version = None
        self.lib_directory = 'lib_{}.{}.{}'.format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro
        )
        self.requirements_file = 'requirements.txt'
        self.static_lib_dir = 'lib_latest'
        self.use_temp_requirements_file = False

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
                proxy_url = '{}:{}@{}:{}'.format(
                    proxy_user, proxy_pass, self.args.proxy_host, self.args.proxy_port
                )
            else:
                # proxy url without auth
                proxy_url = '{}:{}'.format(self.args.proxy_host, self.args.proxy_port)

            os.putenv('HTTP_PROXY', 'http://{}'.format(proxy_url))
            os.putenv('HTTPS_PROXY', 'https://{}'.format(proxy_url))

            print(
                'Using Proxy Server: {}{}:{}.'.format(
                    c.Fore.CYAN, self.args.proxy_host, self.args.proxy_port
                )
            )
            proxy_enabled = True
        return proxy_enabled

    def _create_lib_latest(self):
        """Create the lib_latest symlink for App Builder."""
        # TODO: Update this method to copy latest lib directory on Windows.
        if platform.system() != 'Windows':
            if os.path.islink(self.static_lib_dir):
                os.unlink(self.static_lib_dir)
            os.symlink('lib_{}'.format(self.latest_version), self.static_lib_dir)

    def _create_temp_requirements(self):
        """Create a temporary requirements.txt.

        This allows testing again a git branch instead of pulling from pypi.
        """
        self.use_temp_requirements_file = True
        # Replace tcex version with develop branch of tcex
        with open(self.requirements_file, 'r') as fh:
            current_requirements = fh.read().strip().split('\n')

        self.requirements_file = 'temp-{}'.format(self.requirements_file)
        with open(self.requirements_file, 'w') as fh:
            new_requirements = ''
            for line in current_requirements:
                if not line:
                    continue
                if line.startswith('tcex'):
                    line = 'git+https://github.com/ThreatConnect-Inc/tcex.git@{}#egg=tcex'
                    line = line.format(self.args.branch)
                # print('line', line)
                new_requirements += '{}\n'.format(line)
            fh.write(new_requirements)

    def install_libs(self):
        """Install Required Libraries using pip."""
        # default or current python version
        lib_data = [{'python_executable': sys.executable, 'lib_dir': self.lib_directory}]

        # check for requirements.txt
        if not os.path.isfile(self.requirements_file):
            self.handle_error('A requirements.txt file is required to install modules.')

        # if branch arg is provide use git branch instead of pypi
        if self.args.branch is not None:
            self._create_temp_requirements()

        # overwrite default with config data
        if self.tcex_json.get('lib_versions'):
            lib_data = self.tcex_json.get('lib_versions')
            print('{}Using "lib" directories defined in tcex.json file.'.format(c.Style.BRIGHT))

        # configure proxy settings
        proxy_enabled = self._configure_proxy()

        # install all requested lib directories
        for data in lib_data:
            # pattern to match env vars in data
            env_var = re.compile(r'\$env\.([a-zA-Z0-9]+)')

            lib_dir = data.get('lib_dir')
            # replace env vars with env val in the lib dir
            matches = re.findall(env_var, lib_dir)
            if matches:
                env_val = os.environ.get(matches[0])
                if env_val is None:
                    self.handle_error(
                        '"{}" env variable set in tcex.json, but could not be resolved.'.format(
                            matches[0]
                        )
                    )
                lib_dir = re.sub(env_var, env_val, lib_dir)
            lib_dir_fq = os.path.join(self.app_path, lib_dir)

            if os.access(lib_dir_fq, os.W_OK):
                # remove lib directory from previous runs
                shutil.rmtree(lib_dir_fq)

            # replace env vars with env val in the python executable
            python_executable = data.get('python_executable')
            matches = re.findall(env_var, python_executable)
            if matches:
                env_val = os.environ.get(matches[0])
                python_executable = re.sub(env_var, env_val, python_executable)

            print('Building Lib Dir: {}{}{}'.format(c.Style.BRIGHT, c.Fore.CYAN, lib_dir_fq))
            exe_command = self._build_command(python_executable, lib_dir_fq, proxy_enabled)

            print('Running: {}{}{}'.format(c.Style.BRIGHT, c.Fore.GREEN, ' '.join(exe_command)))
            p = subprocess.Popen(
                exe_command,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            out, err = p.communicate()  # pylint: disable=W0612

            if p.returncode != 0:
                print('{}{}FAIL'.format(c.Style.BRIGHT, c.Fore.RED))
                print('{}{}{}'.format(c.Style.BRIGHT, c.Fore.RED, err.decode('utf-8')))
                sys.exit('ERROR: {}'.format(err.decode('utf-8')))

            # version comparison
            try:
                python_version = lib_dir.split('_', 1)[1]
            except IndexError:
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
