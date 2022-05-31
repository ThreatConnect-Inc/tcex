"""Input for Apps"""
# standard library
import json
import logging
import os
import re
from base64 import b64decode
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Union

# third-party
from pydantic import BaseModel, Extra

# first-party
from tcex.app_config.install_json import InstallJson
from tcex.backports import cached_property
from tcex.input.field_types import Sensitive
from tcex.input.models import feature_map, runtime_level_map, tc_action_map
from tcex.key_value_store import RedisClient
from tcex.pleb.none_model import NoneModel
from tcex.pleb.registry import registry
from tcex.utils import Utils

if TYPE_CHECKING:
    # third-party
    from pydantic import ValidationError

# get tcex logger
logger = logging.getLogger('tcex')

# define JSON encoders
json_encoders = {Sensitive: lambda v: str(v)}  # pylint: disable=W0108


def input_model(models: list) -> 'BaseModel':
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
            json_encoders = json_encoders

    return InputModel


class Input:
    """Module to handle inputs for all App types."""

    def __init__(self, config: Optional[dict] = None, config_file: Optional[str] = None, **kwargs):
        """Initialize class properties.

        Keyword Args:
            tc_session: pass a tc_session object to use, else will use the one from registry.
        """

        # TODO [HIGH] kwarg - don't add built-in models, supply custom TcSession object
        self.config = config
        self.config_file = config_file

        # properties
        self._models = []
        self.ij = InstallJson()
        self.log = logger
        self.utils = Utils()
        self.tc_session = kwargs.get('tc_session')

    @staticmethod
    def _get_redis_client(host, port, db):
        """Return RedisClient client"""
        return RedisClient(host=host, port=port, db=db).client

    def _load_aot_params(
        self,
        tc_aot_enabled: bool,
        tc_kvstore_type: str,
        tc_kvstore_host: str,
        tc_kvstore_port: int,
        tc_action_channel: str,
        tc_terminate_seconds: int,
    ) -> Dict[str, any]:
        """Subscribe to AOT action channel."""
        params = {}
        if tc_aot_enabled is not True:
            return params

        if tc_kvstore_type == 'Redis':

            # get an instance of redis client
            redis_client = self._get_redis_client(
                host=tc_kvstore_host,
                port=tc_kvstore_port,
                db=0,
            )

            try:
                self.log.info('feature=inputs, event=blocking-for-aot')
                msg_data = redis_client.blpop(
                    keys=tc_action_channel,
                    timeout=int(tc_terminate_seconds),
                )

                if msg_data is None:  # pragma: no cover
                    # send exit to tcex.exit method
                    registry.ExitService.exit_aot_terminate(
                        code=1, msg='AOT subscription timeout reached.'
                    )

                msg_data = json.loads(msg_data[1])
                msg_type = msg_data.get('type', 'terminate')
                if msg_type == 'execute':
                    params = msg_data.get('params', {})
                elif msg_type == 'terminate':
                    # send exit to tcex.exit method
                    registry.ExitService.exit_aot_terminate(
                        code=0, msg='Received AOT terminate message.'
                    )
            except Exception as e:  # pragma: no cover
                # send exit to tcex.exit method
                registry.ExitService.exit_aot_terminate(
                    code=1, msg=f'Exception during AOT subscription ({e}).'
                )

        return params

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
        if not fqfn.is_file():  # pragma: no cover
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

    def add_model(self, model: BaseModel):
        """Add additional input models."""
        if model:
            self._models.insert(0, model)

        # clear cache for data property
        if 'model' in self.__dict__:
            del self.__dict__['model']

        # add App level models based on special "tc_action" input
        if hasattr(self.model_unresolved, 'tc_action'):
            self._models.extend(tc_action_map.get(self.model_unresolved.tc_action, []))

        # force data model to load so that validation is done at this EXACT point
        _ = self.model

    @cached_property
    def contents(self) -> dict:
        """Return contents of inputs from all locations."""
        _contents = {}

        # config
        if isinstance(self.config, dict):
            _contents.update(self.config)

        # config file
        _contents.update(self._load_config_file())

        # file params
        _contents.update(self._load_file_params())

        # aot params - must be loaded last so that it has the kv store channels
        _contents.update(
            self._load_aot_params(
                tc_aot_enabled=self.utils.to_bool(_contents.get('tc_aot_enabled', False)),
                tc_kvstore_type=_contents.get('tc_kvstore_type'),
                tc_kvstore_host=_contents.get('tc_kvstore_host'),
                tc_kvstore_port=_contents.get('tc_kvstore_port'),
                tc_action_channel=_contents.get('tc_action_channel'),
                tc_terminate_seconds=_contents.get('tc_terminate_seconds'),
            )
        )
        return _contents

    @cached_property
    def contents_resolved(self) -> dict:
        """Resolve all file, keychain, playbook, and text variables.

        Job, Playbook, and Service Apps call can have a tc-variable, but only
        Playbook Apps will have a playbook variable.
        """
        _inputs = self.contents.copy()

        # support external Apps that don't have an install.json
        if not self.ij.fqfn.is_file():  # pragma: no cover
            return _inputs

        for name, value in _inputs.items():
            if name == 'tc_playbook_out_variables':
                # for services, this input contains the name of the expected outputs.  If we don't
                # skip this, we'll try to resolve the value (e.g.
                # #Trigger:334:example.service_input!String), but that 1) won't work for services
                # and 2) doesn't make sense.  Service configs will never have playbook variables.
                continue

            if self.utils.is_tc_variable(value):  # only matches playbook variables
                value = self.resolve_variable(variable=value)
            elif self.ij.model.runtime_level.lower() == 'playbook':
                if isinstance(value, list):
                    # list could contain playbook variables, try to resolve the value
                    updated_value_array = []
                    for v in value:
                        if isinstance(v, str):
                            v = registry.playbook.read.variable(v)
                        # TODO: [high] does resolve variable need to be added here
                        updated_value_array.append(v)
                    value = updated_value_array
                elif self.utils.is_playbook_variable(value):  # only matches playbook variables
                    # when using Union[Bytes, String] in App input model the value
                    # can be coerced to the wrong type. the BinaryVariable and
                    # StringVariable custom types allows for the validator in Binary
                    # and String types to raise a value error.
                    value = registry.playbook.read.variable(value)
                elif isinstance(value, str):
                    value = registry.playbook.read._read_embedded(value)
            else:
                for match in re.finditer(self.utils.variable_tc_pattern, str(value)):
                    variable = match.group(0)  # the full variable pattern
                    if match.group('type').lower() == 'file':
                        v = '<file>'
                    else:
                        v = self.resolve_variable(variable=variable)
                    value = value.replace(variable, v)

            _inputs[name] = value

        # update contents
        self.contents_update(_inputs)
        return dict(sorted(_inputs.items()))

    # TODO: [high] - can this be replaced with a pydantic root validator?
    def contents_update(self, inputs: dict):
        """Update inputs provided by AOT to be of the proper value and type."""
        for name, value in inputs.items():
            # ThreatConnect AOT params could be updated in the future to proper JSON format.
            # MultiChoice data should be represented as JSON array and Boolean values should be a
            # JSON boolean and not a string.
            param = self.ij.model.get_param(name)
            if isinstance(param, NoneModel):
                # skip over "default" inputs not defined in the install.json file
                continue

            if param.type.lower() == 'multichoice' or param.allow_multiple:
                # update delimited value to an array for inputs that have type of MultiChoice
                if value is not None and not isinstance(value, list):
                    inputs[name] = value.split(self.ij.model.list_delimiter or '|')
            elif param.type == 'boolean' and isinstance(value, str):
                # convert boolean input that are passed in as a string ("true" -> True)
                inputs[name] = value.lower() == 'true'

    @cached_property
    def model(self) -> 'BaseModel':
        """Return the Input Model."""
        return input_model(self.models)(**self.contents_resolved)

    @cached_property
    def model_unresolved(self) -> 'BaseModel':
        """Return the Input Model using contents (no resolved values)."""
        return input_model(self.models)(**self.contents)

    @cached_property
    def models(self) -> list:
        """Return all models for inputs."""
        # support external Apps that don't have an install.json
        if not self.ij.fqfn.is_file():
            return runtime_level_map.get('external')

        # add all models for any supported features of the App
        for feature in self.ij.model.features:
            self._models.extend(feature_map.get(feature, []))

        # add all models based on the runtime level of the App
        self._models.extend(runtime_level_map.get(self.ij.model.runtime_level.lower()))

        return self._models

    # TODO: [low] is this needed or can Field value be set to tc_property=True?
    @cached_property
    def model_properties(self) -> set:
        """Return only defined properties from model (exclude additional)."""
        properties = set()
        for model in self.models:
            properties.update(model.schema().get('properties').keys())

        return properties

    def resolve_variable(self, variable: str) -> Union[bytes, str]:
        """Resolve FILE/KEYCHAIN/TEXT variables.

        Feature: PLAT-2688

        Data Format:
        {
            "data": "value"
        }
        """
        match = re.match(Utils().variable_tc_match, variable)
        key = match.group('key')
        provider = match.group('provider')
        type_ = match.group('type')

        # retrieve value from API
        data = None
        session = self.tc_session if self.tc_session else registry.session_tc
        r = session.get(f'/internal/variable/runtime/{provider}/{key}')
        if r.ok:
            try:
                data = r.json().get('data')

                if type_.lower() == 'file':
                    data = b64decode(data)  # returns bytes
                elif type_.lower() == 'keychain':
                    data = Sensitive(data)
            except Exception as ex:
                raise RuntimeError(
                    f'Could not retrieve variable: provider={provider}, key={key}, type={type_}.'
                ) from ex
        else:
            raise RuntimeError(
                f'Could not retrieve variable: provider={provider}, key={key}, type={type_}.'
            )

        return data

    @staticmethod
    def validation_exit_message(ex: 'ValidationError'):
        """Format and return validation error message."""
        _exit_message = {}
        for err in ex.errors():
            # deduplicate error messagese
            err_loc = ','.join([str(e) for e in err.get('loc')])
            err_msg = err.get('msg')
            _exit_message.setdefault(err_loc, [])
            if err_msg not in _exit_message[err_loc]:
                _exit_message[err_loc].append(err_msg)

        # format error messages
        _exit_message_list = ['Input validation errors']
        for loc, err_list in _exit_message.items():
            _exit_message_list.append(f'''{loc}: {', '.join(err_list)}''')

        # exit with error message
        return '\n'.join(_exit_message_list)
