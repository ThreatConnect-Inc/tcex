#!/usr/bin/env python
"""TcEx Dependencies Command"""
# standard library
import os
import sys
from pathlib import Path

# third-party
import typer

# first-party
from tcex.bin.bin_abc import BinABC
from tcex.input.field_types.sensitive import Sensitive
from tcex.pleb.proxies import proxies
from tcex.sessions.auth.hmac_auth import HmacAuth
from tcex.sessions.tc_session import TcSession


class Deploy(BinABC):
    """Install dependencies for App."""

    def __init__(
        self,
        server: str,
        allow_all_orgs: bool,
        allow_distribution: bool,
        app_file: str,
        proxy_host: str,
        proxy_port: int,
        proxy_user: str,
        proxy_pass: str,
    ):
        """Initialize Class properties."""
        super().__init__()
        self._app_file = app_file
        self.allow_all_orgs = allow_all_orgs
        self.allow_distribution = allow_distribution
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_user = proxy_user
        self.proxy_pass = proxy_pass
        self.server = server

    @staticmethod
    def _handle_missing_environment(variable: str):
        """Print error on missing environment variable."""
        typer.secho(
            f'Could not find environment variable: {variable}.',
            fg=typer.colors.RED,
            err=True,
        )
        sys.exit(1)

    def _check_file(self):
        """Return True if file exists."""
        if not os.path.isfile(self._app_file):
            self.print_failure(f'Could not find file: {self._app_file}.')
            sys.exit(1)

    @property
    def app_file(self):
        """Return app file."""
        if self._app_file is None:
            target_fqpn = Path('target')
            app_files = list(target_fqpn.glob('*.tcx'))
            if len(app_files) > 1:
                self.print_failure(
                    '''More than one App file found, can't autodetect the correct file.''',
                )
                sys.exit(1)
            elif not app_files:
                self.print_failure('No App file found.')

            # set app_file to the only file found
            self._app_file = app_files[0]

        # validate the file exists
        self._check_file()

        return Path(self._app_file)

    @property
    def auth(self):
        """Authenticate with TcEx."""
        tc_api_access_id = os.getenv('TC_API_ACCESS_ID')
        tc_api_secret_key = os.getenv('TC_API_SECRET_KEY')
        if tc_api_access_id is None:
            self._handle_missing_environment('TC_API_ACCESS_ID')
        if tc_api_secret_key is None:
            self._handle_missing_environment('TC_API_SECRET_KEY')

        return HmacAuth(tc_api_access_id, Sensitive(tc_api_secret_key))

    @property
    def base_url(self):
        """Authenticate with TcEx."""
        return f'https://{self.server}/api'

    # pylint: disable=consider-using-with
    def deploy_app(self):
        """Deploy the App to ThreatConnect Exchange."""
        self.print_block('\nUploading App ...\n', fg_color='green')
        files = {
            'allowAllOrgs': self.allow_all_orgs,
            'allowAppDistribution': self.allow_distribution,
            'fileData': ('filename', open(self.app_file, 'rb'), 'application/octet-stream'),
        }
        try:
            response = self.session.post('/internal/apps/exchange/install', files=files, timeout=60)
        except Exception as err:
            self.print_title('Failed Deploying App', fg_color='red')
            self.print_block(str(err), max_length=120)
            sys.exit(0)

        if not response.ok:
            reason = response.text or response.reason
            self.print_title('Failed Deploying App', fg_color='red')
            self.print_setting('File Name', os.path.basename(self.app_file))
            self.print_setting('Reason', reason)
            self.print_setting('Status Code', response.status_code)
            self.print_setting('URL', response.request.url)
        else:
            response_data = response.json()[0]
            self.print_title('Successfully Deployed App')
            self.print_setting('File Name', os.path.basename(self.app_file))
            self.print_setting('Display Name', response_data.get('displayName'))
            self.print_setting('Program Name', response_data.get('programName'))
            self.print_setting('Program Version', response_data.get('programVersion'))
            self.print_setting('Allow All Orgs', self.allow_all_orgs)
            self.print_setting('Allow Distribution', self.allow_distribution)
            self.print_setting('Status Code', response.status_code)
            self.print_setting('URL', response.request.url)

    @property
    def session(self):
        """Create a TcEx Session."""
        _proxies = proxies(
            proxy_host=self.proxy_host,
            proxy_port=self.proxy_port,
            proxy_user=self.proxy_user,
            proxy_pass=self.proxy_pass,
        )
        return TcSession(auth=self.auth, base_url=self.base_url, proxies=_proxies)
