"""Input for Apps"""
# standard library
import json
import logging
import os
import threading
from pathlib import Path
from typing import Optional, Union

# third-party
from pydantic import BaseModel, Extra

# first-party
from tcex.app_config.install_json import InstallJson
from tcex.backports import cached_property
from tcex.input.models import feature_map, runtime_level_map
from tcex.key_value_store import KeyValueApi, KeyValueRedis, RedisClient
from tcex.playbook import Playbook
from tcex.pleb import Event, NoneModel, proxies
from tcex.sessions import TcSession
from tcex.utils import Utils

# get tcex logger
logger = logging.getLogger('tcex')


def input_model(models: list) -> BaseModel:
    """Return Input Model."""

    class InputModel(*models):
        """Input Model"""

        # [legacy] if True, the App should get it's inputs from secure params (redis)
        # supported runtimeLevel: [Organization, Playbook]
        tc_secure_params: bool = False

        # the user id of the one executing the App
        # supported runtimeLevel: [Organization, Playbook]
        tc_user_id: Optional[int]

        class Config:
            """DataModel Config"""

            extra = Extra.allow
            validate_assignment = True

    return InputModel


class Input:
    """Module to handle inputs for all App types."""

    def __init__(self, config: Optional[dict] = None, config_file: Optional[str] = None) -> None:
        """Initialize class properties."""
        self.config = config
        self.config_file = config_file

        # properties
        self._models = []
        self.event = Event()
        self.ij = InstallJson()
        self.log = logger
        self.utils = Utils()

    def _load_aot_params(
        self,
        tc_aot_enabled: bool,
        tc_kvstore_type: str,
        tc_kvstore_host: str,
        tc_kvstore_port: int,
        tc_action_channel: str,
        tc_terminate_seconds: int,
    ) -> dict[str, any]:
        """Subscribe to AOT action channel."""
        params = {}
        if tc_aot_enabled is not True:
            return params

        if tc_kvstore_type == 'Redis':

            # get an instance of redis client
            redis_client = RedisClient(
                host=tc_kvstore_host,
                port=tc_kvstore_port,
                db=0,
            ).client

            try:
                self.log.info('feature=inputs, event=blocking-for-aot')
                msg_data = redis_client.blpop(
                    keys=tc_action_channel,
                    timeout=tc_terminate_seconds,
                )

                if msg_data is None:  # pragma: no cover
                    # send exit to tcex.exit method
                    self.event.send('exit', code=1, msg='AOT subscription timeout reached.')

                msg_data = json.loads(msg_data[1])
                msg_type = msg_data.get('type', 'terminate')
                if msg_type == 'execute':
                    params = msg_data.get('params', {})
                elif msg_type == 'terminate':
                    # send exit to tcex.exit method
                    self.event.send('exit', code=0, msg='Received AOT terminate message.')
            except Exception as e:  # pragma: no cover
                # send exit to tcex.exit method
                self.event.send('exit', code=1, msg=f'Exception during AOT subscription ({e}).')

        return params

    def _load_file_params(self):
        """Load file params provided by the core platform."""
        # default file contents
        file_content = {}

        tc_app_param_file = os.getenv('TC_APP_PARAM_FILE')
        tc_app_param_key = os.getenv('TC_APP_PARAM_KEY')
        if not all([tc_app_param_file, tc_app_param_key]):
            return file_content

        # tc_app_param_file is a fully qualified file name
        fqfn = Path(tc_app_param_file)
        if not fqfn.is_file():
            self.log.error(
                'feature=inputs, event=load-file-params, '
                f'exception=file-not-found, filename={fqfn.name}'
            )
            return file_content

        # read file contents
        try:
            # read encrypted file from "in" directory
            with fqfn.open(mode='rb') as fh:
                encrypted_contents = fh.read()
        except Exception:  # pragma: no cover
            self.log.error(f'feature=inputs, event=config-parse-failure, filename={fqfn.name}')
            return file_content

        # decrypt file contents
        try:
            file_content = json.loads(
                self.utils.decrypt_aes_cbc(tc_app_param_key, encrypted_contents).decode()
            )

            # delete file
            fqfn.unlink()
        except Exception:  # pragma: no cover
            self.log.error(f'feature=inputs, event=config-decryption-failure, filename={fqfn.name}')

        return file_content

    def _load_config_file(self):
        """Load config file params provided passed to inputs."""
        # default file contents
        file_content = {}
        if self.config_file is None:
            return file_content

        # self.config_file should be a fully qualified file name
        fqfn = Path(self.config_file)
        if not fqfn.is_file():
            self.log.error(
                'feature=inputs, event=load-config-file, '
                f'exception=file-not-found, filename={fqfn.name}'
            )
            return file_content

        # read file contents
        try:
            # read encrypted file from "in" directory
            with fqfn.open(mode='rb') as fh:
                return json.load(fh)
        except Exception:  # pragma: no cover
            self.log.error(f'feature=inputs, event=config-parse-failure, filename={fqfn.name}')
            return file_content

    def add_models(self, models: list) -> None:
        """Add additional input models."""
        self._models.extend(models)

        # clear cache for data property
        del Input.__dict__['data']
        # Input.data.fget.cache_clear()

        # clear cache for models property
        del Input.__dict__['models']
        # Input.models.fget.cache_clear()

    @cached_property
    def contents(self) -> dict:
        """Load configuration data from file."""
        _contents = {}

        # config
        if isinstance(self.config, dict):
            _contents.update(self.config)

        # config file
        _contents.update(self._load_config_file())

        # file params
        _contents.update(self._load_file_params())

        # aot params
        _contents.update(
            self._load_aot_params(
                tc_aot_enabled=_contents.get('tc_aot_enabled', False),
                tc_kvstore_type=_contents.get('tc_kvstore_type'),
                tc_kvstore_host=_contents.get('tc_kvstore_host'),
                tc_kvstore_port=_contents.get('tc_kvstore_port'),
                tc_action_channel=_contents.get('tc_action_channel'),
                tc_terminate_seconds=_contents.get('tc_terminate_seconds'),
            )
        )

        # register token
        self.register_token(_contents.get('tc_token'), _contents.get('tc_token_expires'))

        return _contents

    @cached_property
    def contents_resolved(self) -> dict:
        """Resolve all playbook params."""
        _inputs = self.contents
        if self.ij.data.runtime_level.lower() == 'playbook':
            for name, value in _inputs.items():
                # model properties at this point are the default fields passed by ThreatConnect
                # these should not be playbook variables and will not need to be resolved.
                if name in self.model_properties:
                    continue

                if isinstance(value, list):
                    # list could contain variables, try to resolve the value
                    updated_value_array = []
                    for v in value:
                        if isinstance(v, str):
                            updated_value_array.append(self.playbook.read(v))
                    _inputs[name] = updated_value_array
                elif isinstance(value, str):
                    # strings could be a variable, try to resolve the value
                    _inputs[name] = self.playbook.read(value)

        # update contents
        self.contents_update(_inputs)

        return _inputs

    # TODO: [high] - can this be replaced with a pydantic root validator?
    def contents_update(self, inputs: dict) -> None:
        """Update inputs provided by AOT to be of the proper value and type."""
        for name, value in inputs.items():
            # model properties at this point are the default fields passed by ThreatConnect
            # these should not be playbook variables and will not need to be resolved.
            if name in self.model_properties:
                continue

            # ThreatConnect AOT params could be updated in the future to proper JSON format.
            # MultiChoice data should be represented as JSON array and Boolean values should be a
            # JSON boolean and not a string.
            param = self.ij.data.get_param(name)
            if isinstance(param, NoneModel):
                # skip over "default" inputs not defined in the install.json file
                continue

            if param.type.lower() == 'multichoice' or param.allow_multiple:
                # update delimited value to an array for inputs that have type of MultiChoice
                if value is not None and not isinstance(value, list):
                    inputs[name] = value.split(self.ij.data.list_delimiter or '|')
            elif param.type == 'boolean' and isinstance(value, str):
                # convert boolean input that are passed in as a string ("true" -> True)
                inputs[name] = str(value).lower() == 'true'

    # @staticmethod
    # def custom_model(contents: dict, models: list) -> BaseModel:
    #     """Return a custom model with provided models and data."""
    #     return input_model(models)(**contents)

    @cached_property
    def data(self) -> BaseModel:
        """Return the Input Model."""
        return input_model(self.models)(**self.contents_resolved)

    @cached_property
    def data_unresolved(self) -> BaseModel:
        """Return the Input Model using contents (no resolved values)."""
        return input_model(self.models)(**self.contents)

    @cached_property
    def key_value_store(self) -> Union[KeyValueApi, KeyValueRedis]:
        """Return the correct KV store for this execution."""
        if self.data_unresolved.tc_kvstore_type == 'Redis':
            return KeyValueRedis(self.redis_client)

        if self.data_unresolved.tc_kvstore_type == 'TCKeyValueAPI':
            return KeyValueApi(self.session)

        raise RuntimeError(f'''Invalid KV Store Type: ({self.data_unresolved.tc_kvstore_type})''')

    # @property
    # def model_fields(self) -> list:
    #     """Return all current fields of the model."""
    #     self.data.dict().keys()

    @cached_property
    def models(self) -> list:
        """Return all models for inputs."""
        # add all models for any supported features of the App
        for feature in self.ij.data.features:
            self._models.extend(feature_map.get(feature))

        # add all models based on the runtime level of the App
        self._models.extend(runtime_level_map.get(self.ij.data.runtime_level.lower()))

        return self._models

    # TODO: [low] is this needed or can Field value be set to tc_property=True?
    @cached_property
    def model_properties(self) -> set:
        """Return only defined properties from model (exclude additional)."""
        properties = set()
        for model in self.models:
            properties.update(model.schema().get('properties').keys())

        return properties

    @cached_property
    def playbook(self) -> Playbook:
        """Return instance of Playbook."""
        return Playbook(
            key_value_store=self.key_value_store,
            context=self.data_unresolved.tc_playbook_kvstore_contex,
            output_variables=self.data_unresolved.tc_playbook_out_variables,
        )

    @cached_property
    def redis_client(self) -> RedisClient:
        """Return redis client instance configure for Playbook/Service Apps."""
        return RedisClient(
            host=self.data_unresolved.tc_kvstore_host,
            port=self.data_unresolved.tc_kvstore_port,
            db=self.data_unresolved.tc_playbook_kvstore_id,
        ).client

    def register_token(self, tc_token: str, tc_token_expires: str) -> None:
        """Register token if provided in args (non-service Apps)"""
        if all([tc_token, tc_token_expires]):
            self.event.send(
                channel='register_token',
                # key='MainThread',
                key=threading.current_thread().name,
                token=tc_token,
                expires=tc_token_expires,
            )

    @cached_property
    def session(self) -> TcSession:
        """Return Session configured for ThreatConnect API."""
        _session = TcSession(
            api_access_id=self.data_unresolved.api_access_id,
            api_secret_key=self.data_unresolved.api_secret_key,
            base_url=self.data_unresolved.tc_api_path,
        )

        # set verify
        _session.verify = self.data_unresolved.tc_verify

        # set token - this token will never require renewal
        _session.token = self.data_unresolved.tc_token

        # add proxy support if requested
        if self.data_unresolved.tc_proxy_tc:
            _session.proxies = proxies(
                proxy_host=self.data_unresolved.tc_proxy_host,
                proxy_port=self.data_unresolved.tc_proxy_port,
                proxy_user=self.data_unresolved.tc_proxy_username,
                proxy_pass=self.data_unresolved.tc_proxy_password,
            )

        return _session

    # TODO: [med] once logging is figured out see if this is still needed
    def update_logging(self):
        """."""
        self.log.trace('update_logging')
