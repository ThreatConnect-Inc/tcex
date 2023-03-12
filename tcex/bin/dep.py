"""TcEx Dependencies Command"""
# standard library
import os
import shutil
import subprocess  # nosec
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit

# third-party
import typer

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.backport import cached_property
from tcex.bin.bin_abc import BinABC


class Dep(BinABC):
    """Install dependencies for App."""

    def __init__(
        self,
        branch: str,
        dev: bool,
        no_cache_dir: bool,
        pre: bool,
        proxy_host: str | None,
        proxy_port: int | None,
        proxy_user: str | None,
        proxy_pass: str | None,
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

        if not self.proxy_host and os.environ.get('https_proxy'):
            parsed_proxy_url = urlsplit(os.environ.get('https_proxy'))
            self.proxy_host = parsed_proxy_url.hostname
            self.proxy_port = parsed_proxy_url.port
            self.proxy_user = parsed_proxy_url.username
            self.proxy_pass = parsed_proxy_url.password

        # properties
        self.env = self._env
        self.latest_version = None
        self.proxy_enabled = False
        self.requirements_fqfn_branch = None

        # update tcex.json
        self.tj.update.multiple()

    def _build_command(self) -> list[str]:
        """Build the pip command for installing dependencies."""
        # support temp (branch) requirements.txt file
        _requirements_fqfn = str(self.requirements_fqfn)
        if self.requirements_fqfn_branch:
            _requirements_fqfn = str(self.requirements_fqfn_branch)

        exe_command = [
            str(self.python_executable),
            '-m',
            'pip',
            'install',
            '-r',
            _requirements_fqfn,
            '--ignore-installed',
            '--quiet',
            '--target',
            self.deps_dir.name,
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

    @property
    def _env(self):
        """Return the environment variables."""
        _env = os.environ.copy()

        # add ci env
        ci_token = os.getenv('CI_JOB_TOKEN')
        if ci_token:
            _env.update({'CI_JOB_TOKEN': ci_token})

        return _env

    @staticmethod
    def _remove_previous():
        """Remove previous deps directory recursively."""
        if os.access('deps', os.W_OK):
            shutil.rmtree('deps')

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
            self.env.update(
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

    @cached_property
    def deps_dir(self) -> Path:
        """Return the deps directory."""
        return Path('deps')

    @property
    def has_requirements_lock(self):
        """Return True if requirements.lock exists."""
        return Path('requirements.lock').exists()

    def install_deps(self):
        """Install Required Libraries using pip."""
        error = False  # track if any errors have occurred and if so, don't create lock file.

        # check for requirements.txt
        if not self.requirements_fqfn.is_file():
            self.handle_error(
                f'A {str(self.requirements_fqfn)} file is required to install modules.'
            )

        # update requirements_dev.txt file
        self.update_requirements_dev_txt()

        # remove deps directory from previous runs
        self._remove_previous()

        # build the sub process command
        exe_command = self._build_command()

        # display command setting
        self.print_setting('Running', f'''{' '.join(exe_command)}''', fg_color='GREEN')

        # recommended -> https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
        p = subprocess.Popen(  # pylint: disable=consider-using-with
            exe_command,
            shell=False,  # nosec
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
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

        if self.requirements_fqfn_branch:
            # remove temp requirements.txt file
            self.requirements_fqfn_branch.unlink()

        if self.has_requirements_lock is False:
            if error:
                typer.secho(
                    'Not creating requirements.lock file due to errors.',
                    fg=typer.colors.YELLOW,
                )
            else:
                self.create_requirements_lock()

    @cached_property
    def python_executable(self) -> Path:
        """Return the python executable."""
        return Path(sys.executable)

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
        _requirements = self.requirements_lock_data()
        # sort packages alphabetically
        return '\n'.join(sorted(_requirements.splitlines()))

    def requirements_lock_data(self) -> str:
        """Return the Python packages for the provided directory."""
        deps_dir_path = self.app_path / self.deps_dir
        cmd = f'pip freeze --path "{deps_dir_path}"'
        self.log.debug(f'event=get-requirements-lock-data, cmd={cmd}')
        try:
            output = subprocess.run(  # pylint: disable=subprocess-run-check
                cmd, shell=True, capture_output=True  # nosec
            )
        except Exception as ex:
            self.log.error(f'event=pip-freeze, error="{ex}"')
            typer.echo('Failure: could not get requirements lock data.')
            sys.exit(1)

        if output.returncode != 0:
            self.log.error(f'event=pip-freeze, stderr="{output.stderr}"')

        return output.stdout.decode('utf-8')

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

    def validate_python_version(self):
        """Validate the python version."""
        major_minor = f'{sys.version_info.major}.{sys.version_info.minor}'
        ij_language_version = InstallJson().model.language_version
        if major_minor != ij_language_version:
            typer.secho(
                (
                    'The App languageVersion defined in the install.json '
                    'file does not match the current Python version.'
                    f'\n\nij-version={ij_language_version} != current-version={major_minor}.'
                ),
                err=True,
                color=True,
                fg=typer.colors.YELLOW,
            )
            sys.exit(1)
