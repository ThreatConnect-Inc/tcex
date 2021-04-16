"""Install JSON App Config"""
# standard library
import json
import logging
import os
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
from typing import Optional

from .models import InstallJsonModel

__all__ = ['InstallJson']


class InstallJson:
    """Provide a model for the install.json config file."""

    def __init__(
        self,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
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

    def create_output_variables(self, output_variables, job_id=9876):
        """Create output variables.

        # "#App:9876:app.data.count!String"
        # "#Trigger:9876:app.data.count!String"

        Args:
            output_variables (dict): A dict of the output variables
            job_id (int): A job id to use in output variable string.
        """
        variables = []
        for p in output_variables:
            variables.append(self.create_variable(p.get('name'), p.get('type'), job_id))
        return variables

    def create_variable(self, var_name, var_type, job_id=1234):
        """Create output variables.

        # "#App:9876:app.data.count!String"
        # "#Trigger:9876:app.data.count!String"

        Args:
            var_name (str): The variable name.
            var_type (str): The variable type.
            job_id (int): A job id to use in output variable string.
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

    @property
    def tc_playbook_out_variables(self):
        """Return playbook output variable name array"""
        return self.create_output_variables(self.output_variables)

    @property
    def tc_playbook_out_variables_csv(self):
        """Return playbook output variables as CSV string"""
        return ','.join(self.tc_playbook_out_variables)

    @property
    def update(self):
        """Return InstallJsonUpdate instance."""
        return InstallJsonUpdate(ij=self)

    @property
    def validate(self):
        """Validate install.json."""
        return InstallJsonValidate(ij=self)


class InstallJsonUpdate:
    """Update install.json file with current standards and schema."""

    def __init__(self, ij: InstallJson) -> None:
        """Initialize class properties."""
        self.ij = ij

    def multiple(
        self,
        features: Optional[bool] = True,
        migrate: Optional[bool] = False,
        sequence: Optional[bool] = True,
        valid_values: Optional[bool] = True,
        playbook_data_types: Optional[bool] = True,
    ) -> None:
        """Update the profile with all required changes.

        Args:
            features: If True, features will be updated.
            migrate: If True, programMain will be set to "run".
            sequence: If True, sequence numbers will be updated.
            valid_values: If True, validValues will be updated.
            playbook_data_types:  If True, pbDataTypes will be updated.
        """
        # update features array
        if features is True:
            self.update_features()

        if migrate is True:
            # update programMain to run
            self.update_program_main()

        # update sequence numbers
        if sequence is True:
            self.update_sequence_numbers()

        # update valid values
        if valid_values is True:
            self.update_valid_values()

        # update playbook data types
        if playbook_data_types is True:
            self.update_playbook_data_types()

        with self.ij.fqfn.open(mode='w') as fh:
            # write updated profile
            data = self.ij.data.json(
                by_alias=True, exclude_defaults=True, exclude_none=True, indent=2, sort_keys=True
            )
            fh.write(f'{data}\n')

    # def update_display_name(self, json_data: dict) -> None:
    #     """Update the displayName parameter."""
    #     if not self.ij.data.display_name:
    #         display_name = os.path.basename(os.getcwd()).replace(self.app_prefix, '')
    #         display_name = display_name.replace('_', ' ').replace('-', ' ')
    #         display_name = ' '.join([a.title() for a in display_name.split(' ')])
    #     self.ij.data.display_name = self.ij.data.display_name or display_name

    def update_features(self) -> None:
        """Update feature set based on App type."""
        features = []

        if self.ij.data.runtime_level.lower() in ['organization']:
            features = ['fileParams', 'secureParams']
        elif self.ij.data.runtime_level.lower() in ['playbook']:
            features = [
                'aotExecutionEnabled',
                'appBuilderCompliant',
                'fileParams',
                'secureParams',
            ]
        elif self.ij.data.runtime_level.lower() in [
            'apiservice',
            'triggerservice',
            'webhooktriggerservice',
        ]:
            features = ['appBuilderCompliant', 'fileParams']

        # add layoutEnabledApp if layout.json file exists in project
        if os.path.isfile(os.path.join(self.ij.fqfn.parent, 'layout.json')):
            features.append('layoutEnabledApp')

        # re-add supported optional features
        for feature in self.ij.data.features:
            if feature in [
                'advancedRequest',
                'CALSettings',
                'smtpSettings',
                'webhookResponseMarshall',
                'webhookServiceEndpoint',
            ]:
                features.append(feature)

        self.ij.data.features = features

    def update_program_main(self) -> None:
        """Update program main."""
        self.ij.data.program_main = 'run'

    def update_sequence_numbers(self) -> None:
        """Update program sequence numbers."""
        for sequence, param in enumerate(self.ij.data.params, start=1):
            param.sequence = sequence

    def update_valid_values(self) -> None:
        """Update program main on App type."""
        for param in self.ij.data.params:
            if param.type not in ['String', 'KeyValueList']:
                continue

            if param.encrypt is True:
                if '${KEYCHAIN}' not in param.valid_values:
                    param.valid_values.append('${KEYCHAIN}')
            else:
                if '${TEXT}' not in param.valid_values:
                    param.valid_values.append('${TEXT}')

    def update_playbook_data_types(self) -> None:
        """Update program main on App type."""
        if self.ij.data.runtime_level != 'Playbook':
            return

        for param in self.ij.data.params:
            if param.type != 'String':
                continue
            if not param.playbook_data_type:
                param.playbook_data_type.append('String')


class InstallJsonValidate:
    """Validate install.json file."""

    def __init__(self, ij: InstallJson) -> None:
        """Initialize class properties."""
        self.ij = ij

    def validate_duplicate_input(self) -> list:
        """Check for duplicate input names."""
        duplicates = []
        tracker = []
        for param in self.ij.data.data.params:
            if param.name in tracker:
                duplicates.append(param.name)
            tracker.append(param.name)
        return duplicates

    def validate_duplicate_output(self) -> list:
        """Check for duplicate input names."""
        duplicates = []
        tracker = []
        for output in self.ij.data.playbook.output_variables or []:
            name_type = f'{output.name}-{output.type}'
            if name_type in tracker:
                duplicates.append(output.name)
            tracker.append(name_type)
        return duplicates

    def validate_duplicate_sequence(self) -> list:
        """Check for duplicate sequence numbers."""
        duplicates = []
        tracker = []
        for param in self.ij.data.params:
            if param.sequence in tracker:
                duplicates.append(param.sequence)
            tracker.append(param.sequence)
        return duplicates
