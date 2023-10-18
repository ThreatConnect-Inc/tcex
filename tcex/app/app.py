"""TcEx Framework Module"""

# standard library
import os
import threading
from typing import TYPE_CHECKING

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.app.key_value_store.key_value_store import KeyValueStore
from tcex.app.playbook.playbook import Playbook
from tcex.app.token import Token
from tcex.input.model.module_app_model import ModuleAppModel
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tcex.registry import registry
from tcex.util.file_operation import FileOperation

if TYPE_CHECKING:
    # first-party
    from tcex.app.service import ApiService, CommonServiceTrigger, WebhookTriggerService


class App:
    """TcEx Module"""

    def __init__(self, model: ModuleAppModel, proxies: dict[str, str]):
        """Initialize instance properties."""
        self.model = model
        self.proxies = proxies

    @cached_property
    def file_operation(self) -> FileOperation:
        """Include the Utils module."""
        return FileOperation(
            out_path=self.model.tc_out_path,
            temp_path=self.model.tc_temp_path,
        )

    def get_playbook(
        self, context: str | None = None, output_variables: list | None = None
    ) -> Playbook:
        """Return a new instance of playbook module.

        Args:
            context: The KV Store context/session_id. For PB Apps the context is provided on
                startup, but for service Apps each request gets a different context.
            output_variables: The requested output variables. For PB Apps outputs are provided on
                startup, but for service Apps each request gets different outputs.
        """
        return Playbook(self.key_value_store, context, output_variables)

    @scoped_property
    def key_value_store(self) -> KeyValueStore:
        """Return the correct KV store for this execution.

        The TCKeyValueAPI KV store is limited to two operations (create and read),
        while the Redis kvstore wraps a few other Redis methods.
        """
        return KeyValueStore(
            registry.session_tc,
            self.model.tc_kvstore_host,
            self.model.tc_kvstore_port,
            self.model.tc_kvstore_type,
            self.model.tc_playbook_kvstore_id,
            self.model.tc_kvstore_pass,
            self.model.tc_kvstore_user,
            self.model.tc_kvstore_tls_enabled,
            self.model.tc_kvstore_tls_port,
            self.model.tc_svc_broker_cacert_file,
            self.model.tc_svc_broker_cert_file,
            self.model.tc_svc_broker_key_file,
        )

    @cached_property
    def ij(self) -> InstallJson:
        """Return the install.json file as a dict."""
        return self.install_json

    @cached_property
    def install_json(self) -> InstallJson:
        """Return the install.json file as a dict."""
        return InstallJson()

    @scoped_property
    def playbook(self) -> Playbook:
        """Return an instance of Playbooks module.

        This property defaults context and output variables to arg values.
        """
        return self.get_playbook(
            context=self.model.tc_playbook_kvstore_context,
            output_variables=self.model.tc_playbook_out_variables,
        )

    def results_tc(self, key: str, value: str):
        """Write data to results_tc file in TcEX specified directory.

        The TcEx platform support persistent values between executions of the App.  This
        method will store the values for TC to read and put into the Database.

        Args:
            key: The data key to be stored.
            value: The data value to be stored.
        """
        if os.access(self.model.tc_out_path, os.W_OK):
            results_file = f'{self.model.tc_out_path}/results.tc'
        else:
            results_file = 'results.tc'

        new = True
        # ensure file exists
        open(results_file, 'a').close()  # pylint: disable=consider-using-with
        with open(results_file, 'r+') as fh:
            results = ''
            for line in fh.read().strip().split('\n'):
                if not line:
                    continue
                try:
                    k, v = line.split(' = ')
                except ValueError:
                    # handle null/empty value (e.g., "name =")
                    k, v = line.split(' =')
                if k == key:
                    v = value
                    new = False
                if v is not None:
                    results += f'{k} = {v}\n'
            if new and value is not None:  # indicates the key/value pair didn't already exist
                results += f'{key} = {value}\n'
            fh.seek(0)
            fh.write(results)
            fh.truncate()

    @cached_property
    def service(self) -> 'ApiService | CommonServiceTrigger | WebhookTriggerService':
        """Include the Service Module."""
        if self.install_json.model.is_api_service_app:
            # first-party
            from tcex.app.service import ApiService as Service
        elif self.ij.model.is_webhook_trigger_app:
            # first-party
            from tcex.app.service import WebhookTriggerService as Service
        elif self.ij.model.is_trigger_app:
            # first-party
            from tcex.app.service import CommonServiceTrigger as Service
        else:
            raise RuntimeError('Could not determine the service type.')

        return Service(self.key_value_store, registry.logger, self.model, self.token)

    @cached_property
    def token(self) -> Token:
        """Return token object."""
        _proxies = None
        if self.model.tc_proxy_tc is True:
            _proxies = self.proxies

        _tokens = Token(
            self.model.tc_api_path,
            self.model.tc_verify,
            _proxies,
        )

        # register token for Apps that pass token on start
        if all([self.model.tc_token, self.model.tc_token_expires]):
            _tokens.register_token(
                key=threading.current_thread().name,
                token=self.model.tc_token,
                expires=self.model.tc_token_expires,
            )
        return _tokens

    @cached_property
    def user_agent(self) -> dict[str, str]:
        """Return a User-Agent string."""
        return {
            'User-Agent': (
                f'TcEx/{__import__(__name__).__version__}, '
                f'{self.ij.model.display_name}/{self.ij.model.program_version}'
            )
        }
