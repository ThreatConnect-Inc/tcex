"""Install JSON App Config"""
# standard library
import json
import logging
import os
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from .install_json_update import InstallJsonUpdate
from .install_json_validate import InstallJsonValidate
from .models import InstallJsonModel

__all__ = ['InstallJson']


class InstallJson:
    """Provide a model for the install.json config file."""

    def __init__(
        self,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize class properties."""
        filename = filename or 'install.json'
        path = path or os.getcwd()
        self.log = logger or logging.getLogger('install_json')

        # properties
        self.fqfn = Path(os.path.join(path, filename))

    @property
    @lru_cache
    def contents(self) -> dict:
        """Return install.json file contents."""
        contents = {'runtimeLevel': 'external'}
        if self.fqfn.is_file():
            try:
                with self.fqfn.open() as fh:
                    contents = json.load(fh, object_pairs_hook=OrderedDict)
            except OSError:
                self.log.error(
                    f'feature=install-json, exception=failed-reading-file, filename={self.fqfn}'
                )
        else:
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
        return f'#{self.data.app_output_var_type}:{job_id}:{var_name}!{var_type}'

    @property
    @lru_cache
    def data(self) -> InstallJsonModel:
        """Return the Install JSON model."""
        return InstallJsonModel(**self.contents)

    @staticmethod
    def expand_valid_values(valid_values: list) -> list:
        """Expand supported playbook variables to their full list.

        Args:
            valid_values: The list of valid values for Choice or MultiChoice inputs.

        Returns:
            list: An expanded list of valid values for Choice or MultiChoice inputs.
        """
        valid_values = list(valid_values)
        if '${GROUP_TYPES}' in valid_values:
            valid_values.remove('${GROUP_TYPES}')
            valid_values.extend(
                [
                    'Adversary',
                    'Campaign',
                    'Document',
                    'Email',
                    'Event',
                    'Incident',
                    'Intrusion Set',
                    'Signature',
                    'Task',
                    'Threat',
                ]
            )
        elif '${OWNERS}' in valid_values:
            valid_values.remove('${OWNERS}')
        elif '${USERS}' in valid_values:
            valid_values.remove('${USERS}')
        return valid_values

    def has_feature(self, feature: str) -> bool:
        """Return True if App has the provided feature."""
        return feature.lower() in [f.lower() for f in self.data.features]

    def params_to_args(
        self,
        name: Optional[str] = None,
        hidden: Optional[bool] = None,
        required: Optional[bool] = None,
        service_config: Optional[bool] = None,
        _type: Optional[str] = None,
        input_permutations: Optional[list] = None,
    ) -> dict[str, Any]:
        """Return params as cli args.

        Args:
            name: The name of the input to return. Defaults to None.
            required: If set the inputs will be filtered based on required field.
            service_config: If set the inputs will be filtered based on serviceConfig field.
            _type: The type of input to return. Defaults to None.
            input_permutations: A list of valid input names for provided permutation.

        Returns:
            dict: All args for current filter
        """
        args = {}
        for n, p in self.data.filter_params(
            name, hidden, required, service_config, _type, input_permutations
        ).items():
            if p.type.lower() == 'boolean':
                args[n] = p.default
            elif p.type.lower() == 'choice':
                # use the value from input_permutations if available or provide valid values
                valid_values = f"[{'|'.join(self.expand_valid_values(p.valid_values))}]"
                if input_permutations is not None:
                    valid_values = input_permutations.get(n, valid_values)
                args[n] = valid_values
            elif p.type.lower() == 'multichoice':
                args[n] = p.valid_values
            elif p.type.lower() == 'keyvaluelist':
                args[n] = '<KeyValueArray>'
            elif n in ['api_access_id', 'api_secret_key']:
                # leave these parameters set to the value defined in defaults
                pass
            else:
                types = '|'.join(p.playbook_data_type)
                if types:
                    args[n] = p.default or f'<{types}>'
                else:
                    args[n] = p.default or ''
        return args

    @property
    def tc_playbook_out_variables(self) -> list:
        """Return playbook output variable name array"""
        return self.create_output_variables(self.data.playbook.output_variables)

    @property
    def tc_playbook_out_variables_csv(self) -> str:
        """Return playbook output variables as CSV string"""
        return ','.join(self.tc_playbook_out_variables)

    @property
    def update(self) -> InstallJsonUpdate:
        """Return InstallJsonUpdate instance."""
        return InstallJsonUpdate(ij=self)

    @property
    def validate(self) -> InstallJsonValidate:
        """Validate install.json."""
        return InstallJsonValidate(ij=self)
