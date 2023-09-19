"""Install JSON Update"""
# pylint: disable=R0401
# standard library
import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .install_json import InstallJson


class InstallJsonUpdate:
    """Update install.json file with current standards and schema."""

    def __init__(self, ij: 'InstallJson'):  # pylint: disable=E0601
        """Initialize class properties."""
        self.ij = ij

    def multiple(
        self,
        features: Optional[bool] = True,
        sequence: Optional[bool] = True,
        valid_values: Optional[bool] = True,
        playbook_data_types: Optional[bool] = True,
    ):
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

        # update sequence numbers
        if sequence is True:
            self.update_sequence_numbers()

        # update valid values
        if valid_values is True:
            self.update_valid_values()

        # update playbook data types
        if playbook_data_types is True:
            self.update_playbook_data_types()

        # write updated profile
        self.ij.write()

    def update_features(self):
        """Update feature set based on App type."""
        features = ['runtimeVariables']

        if self.ij.model.is_organization_app:
            features.extend(['fileParams', 'secureParams'])
        elif self.ij.model.is_playbook_app:
            features.extend(
                [
                    'aotExecutionEnabled',
                    'appBuilderCompliant',
                    'fileParams',
                    'runtimeVariables',
                    'secureParams',
                ]
            )
        elif self.ij.model.is_service_app:
            features.extend(['appBuilderCompliant', 'fileParams'])

        # add layoutEnabledApp if layout.json file exists in project
        if os.path.isfile(os.path.join(self.ij.fqfn.parent, 'layout.json')):  # pragma: no cover
            features.append('layoutEnabledApp')

        # re-add supported optional features
        for feature in self.ij.model.features:
            if feature in [
                'advancedRequest',
                'CALSettings',
                'layoutEnabledApp',
                'smtpSettings',
                'webhookResponseMarshall',
                'webhookServiceEndpoint',
                # features for TC App loop prevention
                'CreatesGroup',
                'CreatesIndicator',
                'CreatesSecurityLabel',
                'CreatesTag',
                'DeletesGroup',
                'DeletesIndicator',
                'DeletesSecurityLabel',
                'DeletesTag',
            ]:
                features.append(feature)

        self.ij.model.features = sorted(list(set(features)))

    def update_sequence_numbers(self):
        """Update program sequence numbers."""
        for sequence, param in enumerate(self.ij.model.params, start=1):
            param.sequence = sequence

    def update_valid_values(self):
        """Update program main on App type."""
        for param in self.ij.model.params:
            if param.type not in ['String', 'KeyValueList']:
                continue

            store = 'TEXT'
            if param.encrypt is True:
                store = 'KEYCHAIN'

            if self.ij.model.is_organization_app or param.service_config is True:
                if f'${{USER:{store}}}' not in param.valid_values:
                    param.valid_values.append(f'${{USER:{store}}}')

                if f'${{ORGANIZATION:{store}}}' not in param.valid_values:
                    param.valid_values.append(f'${{ORGANIZATION:{store}}}')

                # remove entry that's specifically for playbooks Apps
                if f'${{{store}}}' in param.valid_values:
                    param.valid_values.remove(f'${{{store}}}')

            elif self.ij.model.is_playbook_app:
                if f'${{{store}}}' not in param.valid_values:
                    param.valid_values.append(f'${{{store}}}')

                # remove entry that's specifically for organization (job) Apps
                if f'${{USER:{store}}}' in param.valid_values:
                    param.valid_values.remove(f'${{USER:{store}}}')

                # remove entry that's specifically for organization (job) Apps
                if f'${{ORGANIZATION:{store}}}' in param.valid_values:
                    param.valid_values.remove(f'${{ORGANIZATION:{store}}}')

    def update_playbook_data_types(self):
        """Update program main on App type."""
        if not self.ij.model.is_playbook_app:
            return

        for param in self.ij.model.params:
            if param.type != 'String':
                continue
            if not param.playbook_data_type:
                param.playbook_data_type.append('String')
