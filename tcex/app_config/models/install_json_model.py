"""Install JSON Model"""
# pylint: disable=no-self-argument,no-self-use; noqa: N805
# standard library
import os
import re
import uuid
from enum import Enum
from typing import Dict, List, Optional, Union

# third-party
from pydantic import BaseModel, Field, validator
from pydantic.types import UUID4, UUID5, constr
from semantic_version import Version

# first-party
from tcex.pleb.none_model import NoneModel

__all__ = ['InstallJsonModel']


def snake_to_camel(snake_string: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


# define JSON encoders
json_encoders = {Version: str}  # pylint: disable=unnecessary-lambda


class DeprecationModel(BaseModel):
    """Model for install_json.deprecation"""

    indicator_type: Optional[str] = Field(
        None,
        description='The indicator type for the deprecation rule.',
    )
    interval_days: Optional[int] = Field(
        None,
        description='The frequency the deprecation rule should run.',
    )
    confidence_amount: Optional[int] = Field(
        None,
        description='The amount the confidence should be reduced by.',
    )
    delete_at_minimum: bool = Field(
        False,
        description='If true, the indicator will be deleted at the minimum confidence.',
    )
    percentage: bool = Field(
        False,
        description='If true, use percentage instead of point value when reducing the confidence.',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class FirstRunParamsModel(BaseModel):
    """Model for install_json.deprecation"""

    param: Optional[str] = Field(
        None,
        description='The parameter to set to the first run value.',
    )
    value: Optional[Union[int, str]] = Field(
        None,
        description='The value to set the parameter to.',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class FeedsModel(BaseModel):
    """Model for install_json.feeds"""

    attributes_file: Optional[str] = Field(
        None,
        description=(
            'Optional property that provides the name of the CSV file with any custom '
            'Attributes required for the feed (e.g., attribute.json).'
        ),
    )
    deprecation: Optional[List[DeprecationModel]] = Field(
        None,
        description='The deprecation rules for the feed.',
    )
    document_storage_limit_mb: int = Field(
        ...,
        description='Optional property that sets the Document storage limit.',
    )
    enable_bulk_json: bool = Field(
        False,
        description='Optional property that enables or disables the bulk JSON capability.',
    )
    first_run_params: Optional[List[FirstRunParamsModel]] = Field(
        None,
        description='Param overrides for the first run of the feed.',
    )
    indicator_limit: int = Field(
        ...,
        description='Optional property that sets the Indicator limit.',
    )
    job_file: str = Field(
        ...,
        description=(
            'Optional property that provides the name of the JSON file that is used to '
            'set up and run the Job that pulls in content from the feed.'
        ),
    )
    source_category: str = Field(
        ...,
        description='Optional property that specifies how the source should be categorized.',
    )
    source_description: str = Field(
        ...,
        description=(
            '''Optional property that provides the source's description as it will be '''
            '''displayed in the ThreatConnect platform.'''
        ),
    )
    source_name: str = Field(
        ...,
        description=(
            '''Optional property that provides the name of the source in which the feed's '''
            '''content will be created.'''
        ),
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class ExposePlaybookKeyAsEnum(str, Enum):
    """Enum for install_json.params[].exposePlaybookAs"""

    Binary = 'Binary'
    BinaryArray = 'BinaryArray'
    KeyValue = 'KeyValue'
    KeyValueArray = 'KeyValueArray'
    String = 'String'
    StringArray = 'StringArray'
    TCEntity = 'TCEntity'
    TCEntityArray = 'TCEntityArray'


class TypeEnum(str, Enum):
    """Enum for install_json.params[].type"""

    Boolean = 'Boolean'
    Choice = 'Choice'
    EditChoice = 'EditChoice'
    KeyValueList = 'KeyValueList'
    MultiChoice = 'MultiChoice'
    String = 'String'
    StringMixed = 'StringMixed'


class ParamsModel(BaseModel):
    """Model for install_json.params"""

    allow_multiple: bool = Field(
        False,
        description=(
            'The value of this optional property is automatically set to true if the '
            'MultiChoice type is used. If a String type is used, this flag allows the '
            'user to define multiple values in a single input field delimited by a pipe '
            '("|") character.'
        ),
    )
    allow_nested: bool = Field(
        False,
        description='',
    )
    default: Optional[Union[bool, str]] = Field(
        None,
        description='Optional property that is the default value for an App input parameter.',
    )
    encrypt: bool = Field(
        False,
        description=(
            'Optional property that designates a parameter as an encrypted value. '
            'Parameters defined as encrypted will be managed by the Keychain feature '
            'that encrypts password while at rest. This flag should be used with the '
            'String type and will render a password input text box in the App '
            'configuration.'
        ),
    )
    expose_playbook_key_as: Optional[ExposePlaybookKeyAsEnum] = Field(
        None,
        description='',
    )
    feed_deployer: bool = Field(
        False,
        description='',
    )
    hidden: bool = Field(
        False,
        description=(
            'If this optional property is set to true, this parameter will be hidden '
            'from the Job Wizard. Hidden parameters allow the developer to persist '
            'parameters between Job executions without the need to render the values in '
            'the Job Wizard. This option is valid only for Python and Java Apps. Further '
            'details on persisting parameters directly from the app are beyond the scope '
            'of this documentation.'
        ),
    )
    intel_type: Optional[List[str]] = Field(
        None,
        description='',
    )
    label: str = Field(
        ...,
        description=(
            'Required property providing a description of the parameter displayed in the '
            'Job Wizard or Spaces Configuration dialog box within the ThreatConnect '
            'platform.'
        ),
    )
    name: str = Field(
        ...,
        description=(
            'Required property that is the internal parameter name taken from the Job '
            'Wizard and passed to the App at runtime. It is the effective command-line '
            'argument name passed to the App.'
        ),
    )
    note: Optional[str] = Field(
        None,
        description=(
            'Optional parameter-description field available in Playbook Apps under the ? '
            'tooltip when the App parameters are being edited. Use this field to '
            'describe the purpose of the parameter in two to three sentences.'
        ),
    )
    playbook_data_type: Optional[List[str]] = Field(
        [],
        description=(
            'Optional property restricting the data type of incoming Playbook variables. '
            'This is different than the type property that controls the UI input type. '
            'The playbookDataType can be any standard or custom type and is expected to '
            'be an array of strings.'
        ),
    )
    required: bool = Field(
        False,
        description=(
            'Optional property designating this parameter as a required field that must '
            'be populated to save the Job or Playbook App.'
        ),
    )
    sequence: Optional[int] = Field(
        None,
        description=(
            'Optional number used to control the ordering of the parameters in the Job '
            'Wizard or Spaces Configuration dialog box. If it is not defined, the order '
            'of the parameters in the install.json file will be used.'
        ),
    )
    service_config: bool = Field(
        False,
        description='',
    )
    setup: bool = Field(
        False,
        description='',
    )
    type: TypeEnum = Field(
        ...,
        description=(
            'Required property to enable the UI to display relevant components and allow '
            'the Job Executor to adapt how parameters are passed to an App at runtime. '
            'The table below lists the available types and how they affect elements '
            'within the platform.'
        ),
    )
    valid_values: Optional[List[str]] = Field(
        [],
        description=(
            'Optional property to be used with the Choice, MultiChoice, and String input '
            'types to provide pre-defined inputs for the user selection.'
        ),
    )
    view_rows: Optional[int] = Field(
        None,
        description=(
            'Optional property for Playbook Apps to control the height of the display in '
            'the input parameter, and it expects an integer value. A value of 1 is '
            'default (and will show a text input element) and anything greater than 1 '
            'displays a textarea input when editing the Playbook App in ThreatConnect.'
        ),
    )

    @validator('name')
    def _name(cls, v):
        """Return the transformed "name" field.

        Used to replace labels for fields non-alphanumeric chars (migrate label to name).
        """
        if v is not None:
            v = v.lower().replace(' ', '_')

            # remove all non-alphanumeric characters and underscores
            v = re.sub(r'[^a-zA-Z0-9_]', '', v)
        return v

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        smart_union = True
        use_enum_values = True
        validate_assignment = True


class OutputVariablesModel(BaseModel):
    """Model for install_json.playbook.outputVariables"""

    # sensitive value
    encrypt: bool = Field(
        False,
        description='',
    )
    intel_type: Optional[List] = Field(
        None,
        description='',
    )
    name: str = Field(
        ...,
        description='',
    )
    note: Optional[str] = Field(
        None,
        description='',
    )
    type: str = Field(
        ..., description='Required property that specifies the type of the output variable.'
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class RetryModel(BaseModel):
    """Model for install_json.playbook.retry"""

    actions: Optional[List[str]] = Field(
        None,
        description='A list of tc_actions that support retry.',
    )
    allowed: bool = Field(
        False,
        description=(
            'Optional property that specifies whether the Playbook App can retry its ' 'execution.'
        ),
    )
    default_delay_minutes: int = Field(
        ...,
        description=(
            'Optional property that specifies the number of minutes between each new '
            'retry in case of failure. This property assumes that the allowed property '
            'is set to true to allow the App to retry.'
        ),
    )
    default_max_retries: int = Field(
        ...,
        description=(
            'Optional property that specifies the maximum number of times the Playbook '
            'App can retry in case of failure. This property assumes that the allowed '
            'property is set to true to allow the app to retry.'
        ),
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class PlaybookModel(BaseModel):
    """Model for install_json.playbook"""

    output_prefix: Optional[str] = Field(None, description='')
    output_variables: Optional[List[OutputVariablesModel]] = Field(
        [],
        description=(
            'Optional outputVariables property that specifies the variables that a '
            'Playbook App will provide for downstream Playbooks.'
        ),
    )
    retry: Optional[RetryModel] = Field(
        None,
        description=(
            'Optional retry property that can be used to allow a Playbook to retry its '
            'execution in case of failure.'
        ),
    )
    type: str = Field(
        ...,
        description='The App category (e.g., Endpoint Detection and Response).',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class ServiceModel(BaseModel):
    """Model for install_json.service"""

    discovery_types: Optional[List[str]] = Field(
        None,
        description='Service App discovery types (e.g., TaxiiApi).',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


def get_commit_hash() -> Optional[str]:
    """Return the current commit hash if available.

    This is not a required task so best effort is fine. In other words this is not guaranteed
    to work 100% of the time.
    """
    commit_hash = None
    branch = None
    branch_file = '.git/HEAD'  # ref: refs/heads/develop

    # get current branch
    if os.path.isfile(branch_file):
        with open(branch_file) as f:
            try:
                branch = '/'.join(f.read().strip().split('/')[2:])
            except IndexError:  # pragma: no cover
                pass

        # get commit hash
        if branch:
            hash_file = f'.git/refs/heads/{branch}'
            if os.path.isfile(hash_file):
                with open(hash_file) as f:
                    commit_hash = f.read().strip()

    if commit_hash is None:
        # gitlab / github CI environment variable
        commit_hash = os.getenv('CI_COMMIT_SHA') or os.getenv('GITHUB_SHA')

    return commit_hash


def gen_app_id() -> str:
    """Return a generate id for the current App."""
    return uuid.uuid5(uuid.NAMESPACE_X500, os.path.basename(os.getcwd()).lower())


class InstallJsonCommonModel(BaseModel):
    """Install JSON Common Model

    This model contains the common fields for the install.json file and
    the app_spec.yaml file.
    """

    allow_on_demand: bool = Field(
        False,
        description=(
            'Required property that allows or disallows an App to be run on demand using '
            'the Run Now button when the App is configured as a Job in the ThreatConnect '
            'platform. This property only applies to Python and Java Apps.'
        ),
    )
    allow_run_as_user: Optional[bool] = Field(
        False,
        description='Controls whether a Playbook App supports run-as-users.',
    )
    api_user_token_param: Optional[bool] = Field(
        True,
        description=(
            '[Deprecated] Optional property that specifies whether or not the App should '
            'use an API user token (which allows access to the DataStore).'
        ),
    )
    app_id: Union[UUID4, UUID5] = Field(
        default_factory=gen_app_id,
        description=(
            '[TcEx 1.1.4+] A unique identifier for the App. This field is not currently '
            'used in the core product, but will be used in other tooling to identify the '
            'App. The appId field with the major version from programVersion make up a '
            'unique Application release. If this field does not exist while packaging '
            'the App via the `tcex package` command, a value will be added using the '
            'project directory name as a seed. Once an App has been released the appId '
            'field should not be changed.'
        ),
    )
    category: str = Field(
        '',
        description='The category of the App. Also playbook.type for playbook Apps.',
    )
    deprecates_apps: Optional[List[str]] = Field(
        None,
        description=(
            'Optional property that provides a list of Apps that should be '
            'deprecated by this App.'
        ),
    )
    display_name: constr(min_length=3, max_length=100) = Field(
        ...,
        description=(
            'Required property providing the name of the App as it will be displayed in '
            'the ThreatConnect platform.'
        ),
    )
    display_path: Optional[constr(min_length=3, max_length=100)] = Field(
        None,
        description='The display path for API service Apps.',
    )
    features: List[str] = Field(
        ...,
        description=(
            'An array of supported features for the App. These feature enable '
            'additional functionality in the Core Platform and/or for the App.'
        ),
    )
    labels: Optional[List[str]] = Field(
        None,
        description='A list of labels for the App.',
    )
    language_version: Optional[str] = Field(
        ...,
        description=(
            'Optional property used solely for tracking purposes. It does not affect '
            'the version of Python or Java used by the Job Execution Engine to run the App.'
        ),
    )
    list_delimiter: str = Field(
        ...,
        description=(
            'Optional property that sets the character used to delimit the values of '
            'an input that support the allowMultiple param option.'
        ),
    )
    min_server_version: str = Field(
        '6.2.0',
        description=(
            'Optional string property restricting the ThreatConnect instance from '
            'installing the App if it does not meet this version requirement '
            '(e.g., 6.5.0).'
        ),
    )
    note: Optional[str] = Field(
        None,
        description=(
            'Optional property available in Playbook Apps while configuring App inputs '
            'in the UI. This is the top level not of the App and should describe the '
            'functionality and use cases of the App.'
        ),
    )
    program_language: str = Field(
        ...,
        description=(
            'Required property describing the language runtime environment used by the '
            'ThreatConnect Job Executor. It is relevant for Apps that run on the Job '
            'Execution Engine (Python and Java Apps) and can be set to NONE for Spaces '
            'Apps.'
        ),
    )
    program_main: str = Field(
        ...,
        description=(
            'Required property providing the entry point into the App. For Python Apps, '
            'it is the name of the .py file (or exclude the extension if running it as a '
            'module). For Java Apps, it is the main class the Job Execution Engine '
            'should use when calling the App using the Java Runtime Environment.'
        ),
    )
    program_version: str = Field(
        ...,
        description=(
            'Required property providing the version number for the App that will be '
            'displayed in the Installed Apps section available to a System '
            'Administrator. ThreatConnect recommends the use of semantic versioning '
            '(e.g., 1.0.1).'
        ),
    )
    runtime_level: Union[List, str] = Field(
        ...,
        description='The type for the App (e.g., Playbook, Organization, etc).',
    )
    service: Optional[ServiceModel] = Field(
        None,
        description='',
    )

    @validator('min_server_version', 'program_version')
    def version(cls, v):
        """Return a version object for "version" fields."""
        if v is not None:
            return Version(v)
        return v  # pragma: no cover

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        arbitrary_types_allowed = True
        json_encoders = json_encoders
        validate_assignment = True


class InstallJsonOrganizationModel(BaseModel):
    """Install JSON Common Model

    This model contains the common fields for the install.json file and
    the app_spec.yaml file.
    """

    feeds: Optional[List[FeedsModel]] = Field(
        None,
        description='A list of features enabled for the App.',
    )
    publish_out_files: Optional[List[str]] = Field(
        None,
        description=(
            'Optional field available for job-style Apps that can be scheduled to serve '
            'files. If this array is populated, the App is responsible for writing the '
            'files to the relative tc_output_path parameter that is passed in. This will '
            'enable HTTP-based file serving of these files as a unique URL available to '
            'the user in ThreatConnect. This parameter accepts an array of strings and '
            'can include file globs.'
        ),
    )
    repeating_minutes: Optional[List[int]] = Field(
        None,
        description=(
            'Optional property that provides a list of minute increments to display in '
            'the Repeat Every… section in the Schedule panel of the Job Wizard. This '
            'property is relevant only for Python and Java Apps for which the developer '
            'wants to control how frequently an App can be executed. If this property is '
            'not defined, the default listing is as follows: [60, 120, 240, 360, 720].'
        ),
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class InstallJsonModel(InstallJsonCommonModel, InstallJsonOrganizationModel):
    """Install JSON Model"""

    commit_hash: Optional[str] = Field(
        default_factory=get_commit_hash,
        description='The git commit hash from when the App was built.',
    )
    docker_image: Optional[str] = Field(
        None,
        description='[unsupported] The docker image to run the App.',
    )
    params: Optional[List[ParamsModel]] = Field(
        None,
        description='',
    )
    playbook: Optional[PlaybookModel] = Field(
        None,
        description='',
    )
    program_icon: Optional[str] = Field(
        None,
        description=(
            'Optional property providing the icon that will be used to represent Central '
            'Spaces Apps.'
        ),
    )
    program_name: Optional[str] = Field(
        None,
        description='',
    )
    runtime_context: Optional[List] = Field(
        None,
        description=(
            'Optional property enabling Spaces Apps to be context aware (i.e., Spaces '
            'Apps that can be added to the Details screen of an object in the '
            'ThreatConnect platform). Because this property is an array of strings, the '
            'App can be displayed in Spaces under multiple contexts within the '
            'ThreatConnect platform, including the Menu and Search screens. This property '
            'is only applicable to Spaces Apps.'
        ),
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        arbitrary_types_allowed = True
        json_encoders = json_encoders
        validate_assignment = True

    @property
    def app_output_var_type(self) -> str:
        """Return the appropriate output var type for the current App."""
        if self.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            return 'Trigger'
        return 'App'

    def filter_params(
        self,
        name: Optional[str] = None,
        hidden: Optional[bool] = None,
        required: Optional[bool] = None,
        service_config: Optional[bool] = None,
        _type: Optional[str] = None,
        input_permutations: Optional[List] = None,
    ) -> Dict[str, 'ParamsModel']:
        """Return params as name/data dict.

        Args:
            name: The name of the input to return.
            hidden: If set the inputs will be filtered based on hidden field.
            required: If set the inputs will be filtered based on required field.
            service_config: If set the inputs will be filtered based on serviceConfig field.
            _type: The type of input to return.
            input_permutations: A list of valid input names for provided permutation.

        Returns:
            dict: All valid inputs for current filter.
        """
        params = {}
        for p in self.params:

            if name is not None:
                if p.name != name:
                    continue

            if hidden is not None:
                if p.hidden is not hidden:
                    continue

            if required is not None:
                if p.required is not required:
                    continue

            if service_config is not None:
                if p.service_config is not service_config:
                    continue

            if _type is not None:
                if p.type != _type:
                    continue

            if input_permutations is not None:
                if p.name not in input_permutations:
                    continue

            params.setdefault(p.name, p)
        return params

    def get_output(self, name: str) -> Union['NoneModel', 'OutputVariablesModel']:
        """Return output for the matching name."""
        return self.playbook_outputs.get(name) or NoneModel()

    def get_param(self, name: str) -> Union['NoneModel', 'ParamsModel']:
        """Return param for the matching name."""
        return self.params_dict.get(name) or NoneModel()

    @property
    def optional_params(self) -> Dict[str, 'ParamsModel']:
        """Return params as name/data model."""
        return {p.name: p for p in self.params if p.required is False}

    @property
    def package_version(self):
        """Return the major version of the App."""
        return f'v{self.program_version.major}'

    @property
    def param_names(self) -> List[str]:
        """Return the "name" field from all params."""
        return [p.name for p in self.params]

    @property
    def params_dict(self) -> Dict[str, 'ParamsModel']:
        """Return params as name/data dict."""
        return {p.name: p for p in self.params}

    @property
    def playbook_outputs(self) -> Dict[str, 'OutputVariablesModel']:
        """Return outputs as name/data model."""
        return {o.name: o for o in self.playbook.output_variables}

    @property
    def required_params(self) -> Dict[str, 'ParamsModel']:
        """Return params as name/data dict."""
        return {p.name: p for p in self.params if p.required is True}

    @property
    def service_config_params(self) -> Dict[str, 'ParamsModel']:
        """Return params as name/data dict."""
        return {p.name: p for p in self.params if p.service_config is True}

    @property
    def service_playbook_params(self) -> Dict[str, 'ParamsModel']:
        """Return params as name/data dict."""
        return {p.name: p for p in self.params if p.service_config is False}
