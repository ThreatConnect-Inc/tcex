"""Install JSON App Config"""
# standard library
import json
import logging
import os
from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# first-party
from tcex.app_config.install_json_update import InstallJsonUpdate
from tcex.app_config.install_json_validate import InstallJsonValidate
from tcex.app_config.models import InstallJsonModel
from tcex.backports import cached_property

if TYPE_CHECKING:
    # first-party
    from tcex.app_config.models.install_json_model import ParamsModel

# get tcex logger
tcex_logger = logging.getLogger('tcex')


class InstallJson:
    """Provide a model for the install.json config file.

    This class can't be a Singleton because it's used by the package
    command to create a install.json file in the build directory.
    """

    def __init__(
        self,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize class properties."""
        filename = filename or 'install.json'
        path = path or os.getcwd()
        self.log = logger or tcex_logger

        # properties
        self.fqfn = Path(os.path.join(path, filename))

    @property
    def app_prefix(self) -> str:
        """Return the appropriate output var type for the current App."""
        return self.app_prefixes.get(self.model.runtime_level.lower(), '')

    @property
    def app_prefixes(self) -> str:
        """Return all the current App prefixes."""
        return {
            'organization': 'TC_-_',
            'playbook': 'TCPB_-_',
            'apiservice': 'TCVA_-_',
            'triggerservice': 'TCVC_-_',
            'webhooktriggerservice': 'TCVW_-_',
        }

    @cached_property
    def contents(self) -> dict:
        """Return install.json file contents."""
        contents = {'runtimeLevel': 'external'}
        if self.fqfn.is_file():
            try:
                with self.fqfn.open() as fh:
                    contents = json.load(fh, object_pairs_hook=OrderedDict)
            except (OSError, ValueError):  # pragma: no cover
                self.log.error(
                    f'feature=install-json, exception=failed-reading-file, filename={self.fqfn}'
                )
        else:  # pragma: no cover
            self.log.error(f'feature=install-json, exception=file-not-found, filename={self.fqfn}')
        return contents

    def create_output_variables(self, output_variables: dict, job_id: Optional[int] = 9876) -> list:
        """Create output variables.

        # "#App:9876:app.data.count!String"
        # "#Trigger:9876:app.data.count!String"

        Args:
            output_variables: A dict of the output variables
            job_id: A job id to use in output variable string.
        """
        variables = []
        for p in output_variables:
            variables.append(self.create_variable(p.name, p.type, job_id))
        return variables

    def create_variable(self, var_name: str, var_type: str, job_id: Optional[int] = 1234) -> str:
        """Create output variables.

        # "#App:9876:app.data.count!String"
        # "#Trigger:9876:app.data.count!String"

        Args:
            var_name: The variable name.
            var_type: The variable type.
            job_id: A job id to use in output variable string.
        """
        return f'#{self.model.app_output_var_type}:{job_id}:{var_name}!{var_type}'

    @staticmethod
    def expand_valid_values(valid_values: list) -> List[str]:
        """Expand supported playbook variables to their full list.

        Args:
            valid_values: The list of valid values for Choice or MultiChoice inputs.

        Returns:
            list: An expanded list of valid values for Choice or MultiChoice inputs.
        """
        # expand is typically for Choice inputs and
        # ${FILE} is usually only on String inputs
        # if '${FILE}' in valid_values:
        #     valid_values.remove('${FILE}')

        # valid_values = list(valid_values)
        if '${GROUP_TYPES}' in valid_values:
            valid_values.remove('${GROUP_TYPES}')
            valid_values.extend(
                [
                    'Adversary',
                    'Attack Pattern',
                    'Campaign',
                    'Course of Action',
                    'Document',
                    'Email',
                    'Event',
                    'Incident',
                    'Intrusion Set',
                    'Malware',
                    'Signature',
                    'Tactic',
                    'Task',
                    'Tool',
                    'Threat',
                    'Vulnerability',
                ]
            )

        if '${OWNERS}' in valid_values:
            valid_values.remove('${OWNERS}')

        if '${USERS}' in valid_values:
            valid_values.remove('${USERS}')
        return valid_values

    def has_feature(self, feature: str) -> bool:
        """Return True if App has the provided feature."""
        return feature.lower() in [f.lower() for f in self.model.features]

    # @cached_property
    @property
    def model(self) -> 'InstallJsonModel':
        """Return the Install JSON model."""
        return InstallJsonModel(**self.contents)

    @property
    def params_dict(self) -> List['ParamsModel']:
        """Return params as name/model.

        Used in tcex_testing for dynamic generation of output variables.
        """
        params = {}
        for p in self.model.params:
            params.setdefault(p.name, p)
        return params

    def params_to_args(
        self,
        name: Optional[str] = None,
        hidden: Optional[bool] = None,
        required: Optional[bool] = None,
        service_config: Optional[bool] = None,
        _type: Optional[str] = None,
        input_permutations: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Return params as cli args.

        Used by tcex_testing project.

        Args:
            name: The name of the input to return.
            required: If set the inputs will be filtered based on required field.
            service_config: If set the inputs will be filtered based on serviceConfig field.
            _type: The type of input to return.
            input_permutations: A list of valid input names for provided permutation.

        Returns:
            dict: All args for current filter
        """
        args = {}
        for n, p in self.model.filter_params(
            name, hidden, required, service_config, _type, input_permutations
        ).items():
            if p.type.lower() == 'boolean':
                args[n] = p.default
            elif p.type.lower() == 'choice':
                # provide all options by default
                valid_values = f"[{'|'.join(self.expand_valid_values(p.valid_values))}]"

                # use the value from input_permutations if available or provide valid values
                if input_permutations is not None:
                    valid_values = input_permutations.get(n, valid_values)

                # use default if available
                if p.default is not None:
                    valid_values = p.default

                args[n] = valid_values
            elif p.type.lower() == 'multichoice':
                args[n] = p.valid_values
            elif p.type.lower() == 'keyvaluelist':
                args[n] = '<KeyValueArray>'
            elif n in ['tc_api_access_id', 'tc_api_secret_key']:  # pragma: no cover
                # leave these parameters set to the value defined in defaults
                pass
            else:
                types = '|'.join(p.playbook_data_type)
                if types:
                    args[n] = p.default or f'<{types}>'
                else:  # pragma: no cover
                    args[n] = p.default or ''
        return args

    @property
    def tc_playbook_out_variables(self) -> list:
        """Return playbook output variable name array"""
        return self.create_output_variables(self.model.playbook.output_variables)

    @property
    def tc_playbook_out_variables_csv(self) -> str:
        """Return playbook output variables as CSV string"""
        return ','.join(self.tc_playbook_out_variables)

    @property
    def update(self) -> 'InstallJsonUpdate':
        """Return InstallJsonUpdate instance."""
        return InstallJsonUpdate(ij=self)

    @property
    def validate(self) -> 'InstallJsonValidate':
        """Validate install.json."""
        return InstallJsonValidate(ij=self)

    def write(self):
        """Write current data file."""
        data = self.model.json(
            by_alias=True, exclude_defaults=True, exclude_none=True, indent=2, sort_keys=True
        )
        with self.fqfn.open(mode='w') as fh:
            fh.write(f'{data}\n')
