"""TcEx Framework Module"""

# standard library
import json
import logging
import os
import re
from base64 import b64decode
from pathlib import Path

# third-party
from pydantic import ValidationError  # TYPE-CHECKING
from pydantic import BaseModel, Extra

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.input.field_type import Sensitive
from tcex.input.model.advanced_request_model import AdvancedRequestModel
from tcex.input.model.app_external_model import AppExternalModel
from tcex.input.model.common_advanced_model import CommonAdvancedModel
from tcex.input.model.common_model import CommonModel
from tcex.input.model.model_map import feature_map, runtime_level_map, tc_action_map
from tcex.input.model.module_app_model import ModuleAppModel
from tcex.input.model.module_requests_session_model import ModuleRequestsSessionModel
from tcex.input.model.path_model import PathModel
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property
from tcex.registry import registry
from tcex.util import Util

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore

# define JSON encoders
json_encoders = {Sensitive: lambda v: str(v)}  # pylint: disable=unnecessary-lambda


def input_model(models: list) -> CommonModel | CommonAdvancedModel:
    """Return Input Model."""

    class InputModel(*models):
        """Input Model"""

        # [legacy] if True, the App should get it's inputs from secure params (redis)
        # supported runtimeLevel: [Organization, Playbook]
        tc_secure_params: bool = False

        # the user id of the one executing the App
        # supported runtimeLevel: [Organization, Playbook]
        tc_user_id: int | None

        class Config:
            """DataModel Config"""

            extra = Extra.allow
            validate_assignment = True
            json_encoders = json_encoders

    return InputModel


class Input:
    """Module to handle inputs for all App types."""

    def __init__(self, config: dict | None = None, config_file: str | None = None):
        """Initialize instance properties."""

        self.config = config
        self.config_file = config_file

        # properties
        self._models = []
        self.ij = InstallJson()
        self.log = _logger
        self.util = Util()

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
        if tc_app_param_file and tc_app_param_key:
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
                    self.util.decrypt_aes_cbc(tc_app_param_key, encrypted_contents).decode()
                )

                # delete file
                fqfn.unlink()
            except Exception:  # pragma: no cover
                self.log.error(
                    f'feature=inputs, event=config-decryption-failure, filename={fqfn.name}'
                )

        return file_content

    def add_model(self, model: type[BaseModel]):
        """Add additional input model."""
        if model:
            self._models.insert(0, model)

        # clear cache for data property
        if 'model' in self.__dict__:
            del self.__dict__['model']

        # add App level model based on special "tc_action" input. this field
        # doesn't exist on the common model, but can be added by the App.
        # the tc_action can never be a variable (choice input).
        if tc_action := self.contents.get('tc_action'):
            self._models.extend(tc_action_map.get(tc_action, []))

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
                # for services, tc_playbook_out_variables contains the name of the expected outputs.
                # If we don't skip this, we'll try to resolve the value (e.g.
                # #Trigger:334:example.service_input!String)
                # 1. this won't work for services
                # 2. service configs will never have playbook variables
                continue

            if self.util.is_tc_variable(value):  # only matches threatconnect variables
                value = self.resolve_variable(variable=value)
            elif self.ij.model.is_playbook_app:
                if isinstance(value, list):
                    # list could contain playbook variables, try to resolve the value
                    updated_value_array = []
                    for v in value:
                        if isinstance(v, str):
                            v = registry.playbook.read.variable(v)
                        # TODO: [high] does resolve variable need to be added here
                        updated_value_array.append(v)
                    value = updated_value_array
                elif self.util.is_playbook_variable(value):  # only matches playbook variables
                    # when using Bytes | String in App input model the value
                    # can be coerced to the wrong type. the BinaryVariable and
                    # StringVariable custom types allows for the validator in Binary
                    # and String types to raise a value error.
                    value = registry.playbook.read.variable(value)
                elif isinstance(value, str):
                    value = registry.playbook.read._read_embedded(value)
            else:
                for match in re.finditer(self.util.variable_tc_pattern, str(value)):
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
        """Update inputs provided by core to be of the proper value and type."""
        for name, value in inputs.items():
            # ThreatConnect params could be updated in the future to proper JSON format.
            # MultiChoice data should be represented as JSON array and Boolean values should be a
            # JSON boolean and not a string.
            param = self.ij.model.get_param(name)
            if param is None:
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
    def model(self) -> CommonAdvancedModel:
        """Return the Input Model."""
        return input_model(self.models)(**self.contents_resolved)  # type: ignore

    @cached_property
    def model_advanced_request(self) -> AdvancedRequestModel:
        """Return the Requests Session Model."""

        class _AdvancedRequestModel(AdvancedRequestModel, extra=Extra.ignore):
            """Model Definition for AdvancedRequestModel inputs ONLY."""

        return _AdvancedRequestModel(**self.contents)

    @cached_property
    def model_organization_unresolved(self) -> CommonModel:
        """Return the Input Model using contents (no resolved values)."""
        return input_model(self.models)(**self.contents)  # type: ignore

    @cached_property
    def model_path(self) -> PathModel:
        """Return the Requests Session Model."""

        class _PathModel(PathModel, extra=Extra.ignore):
            """Model Definition for PathModel inputs ONLY."""

        return _PathModel(**self.contents)

    @cached_property
    def model_unresolved(self) -> CommonAdvancedModel:
        """Return full data model with no resolved values.

        This model has all inputs, including App inputs (e.g., tc_action), but
        any pb/tc variables will not be resolved in the model. The model is
        useful getting and process keyvalue variables that have mixed types.
        """
        return input_model(self.models)(**self.contents)  # type: ignore

    @cached_property
    def model_tc(self) -> CommonAdvancedModel:
        """Return data model for ThreatConnect specific inputs.

        This model does not have any App inputs (e.g., tc_action) and
        should only be used for accessing ThreatConnect specific inputs.
        """

        class _CommonAdvancedModel(CommonAdvancedModel, extra=Extra.ignore):
            """Model Definition for CommonAdvancedModel inputs ONLY."""

        return _CommonAdvancedModel(**self.contents)

    @cached_property
    def models(self) -> list:
        """Return all model for inputs."""
        # support external Apps that don't have an install.json
        if not self.ij.fqfn.is_file():
            return [AppExternalModel]

        # add all model for any supported features of the App
        for feature in self.ij.model.features:
            self._models.extend(feature_map.get(feature, []))

        # add all model based on the runtime level of the App
        rlm = runtime_level_map.get(self.ij.model.runtime_level.lower())
        if rlm is not None:
            self._models.append(rlm)

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
    def module_app_model(self) -> ModuleAppModel:
        """Return the Module App Model."""
        return ModuleAppModel(**self.contents)

    @cached_property
    def module_requests_session_model(self) -> ModuleRequestsSessionModel:
        """Return the Module Requests Session Model."""
        return ModuleRequestsSessionModel(**self.contents)

    def resolve_variable(self, variable: str) -> bytes | str | Sensitive:
        """Resolve FILE/KEYCHAIN/TEXT variables.

        Feature: PLAT-2688

        Data Format:
        {
                "data": "value"
        }
        """
        match = re.match(Util().variable_tc_match, variable)
        if not match:
            raise RuntimeError(f'Could not parse variable: {variable}')

        key = match.group('key')
        provider = match.group('provider')
        type_ = match.group('type')

        # retrieve value from API
        data = None
        r = registry.session_tc.get(f'/internal/variable/runtime/{provider}/{key}')
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
    def validation_exit_message(ex: ValidationError):
        """Format and return validation error message."""
        _exit_message = {}
        for err in ex.errors():
            # deduplicate error messages
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
