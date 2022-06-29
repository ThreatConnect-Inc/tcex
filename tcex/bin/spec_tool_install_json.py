"""TcEx Generate Configurations CLI Command"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.app_config.models import InstallJsonModel
from tcex.bin.bin_abc import BinABC

if TYPE_CHECKING:
    # first-party
    from tcex.app_config import AppSpecYml


class SpecToolInstallJson(BinABC):
    """Generate App Config File"""

    def __init__(self, asy: 'AppSpecYml'):
        """Initialize class properties."""
        super().__init__()
        self.asy = asy

        # properties
        self.filename = 'install.json'

    def _add_standard_fields(self, install_json_data: dict):
        """Add field that apply to ALL App types."""
        install_json_data.update(
            {
                'allowOnDemand': self.asy.model.allow_on_demand,
                'apiUserTokenParam': self.asy.model.api_user_token_param,
                'appId': self.asy.model.app_id,
                'category': self.asy.model.category,
                'deprecatesApps': self.asy.model.deprecates_apps,
                'displayName': self.asy.model.display_name,
                'features': self.asy.model.features,
                'labels': self.asy.model.labels,
                'languageVersion': self.asy.model.language_version,
                'listDelimiter': self.asy.model.list_delimiter,
                'minServerVersion': str(self.asy.model.min_server_version),
                'note': f'{self.asy.model.note}{self._note_per_action}\n',
                'params': [p.dict(by_alias=True) for p in self.asy.model.params],
                'programLanguage': self.asy.model.program_language,
                'programMain': self.asy.model.program_main,
                # 'programName': '',
                'programVersion': str(self.asy.model.program_version),
                'runtimeLevel': self.asy.model.runtime_level,
            }
        )

    def _add_type_api_service_fields(self, install_json_data: dict):
        """Add field that apply to ALL App types."""
        if self.asy.model.runtime_level.lower() == 'apiservice':
            install_json_data['displayPath'] = self.asy.model.display_path

    def _add_type_organization_fields(self, install_json_data: dict):
        """Add field that apply to ALL App types."""
        if self.asy.model.organization:
            # the nested job object is not part of the install.json, it
            # instead gets written to the *.job.json file.
            if self.asy.model.organization.feeds:
                _feeds = []
                for feed in self.asy.model.organization.feeds:
                    feed = feed.dict(by_alias=True)
                    if feed.get('job') is not None:
                        del feed['job']
                    _feeds.append(feed)
                install_json_data['feeds'] = _feeds

            # publish_out_files
            _publish_out_files = self.asy.model.organization.publish_out_files
            if _publish_out_files:
                install_json_data['publishOutFiles'] = _publish_out_files

            # repeating_minutes
            _repeating_minutes = self.asy.model.organization.repeating_minutes
            if _repeating_minutes:
                install_json_data['repeatingMinutes'] = _repeating_minutes

    def _add_type_playbook_fields(self, install_json_data: dict):
        """Add field that apply to ALL App types."""
        if self.asy.model.runtime_level.lower() in [
            'playbook',
            'triggerservice',
            'webhooktriggerservice',
        ]:
            install_json_data['allowRunAsUser'] = self.asy.model.allow_run_as_user
            install_json_data['playbook'] = {
                'outputPrefix': self.asy.model.output_prefix,
                'outputVariables': [
                    ov.dict(by_alias=True) for ov in self.asy.model.output_variables
                ],
                'type': self.asy.model.category,
            }
            if self.asy.model.playbook and self.asy.model.playbook.retry.allowed is True:
                install_json_data['playbook']['retry'] = self.asy.model.playbook.retry.dict(
                    by_alias=True
                )

    @property
    def _note_per_action(self):
        """Return note per action string."""
        # note per action is only supported on playbook Apps
        note_per_action = ''
        if self.asy.model.note_per_action:
            note_per_action = '\n\n'.join(self.asy.model.note_per_action_formatted)
        return note_per_action

    def generate(self):
        """Generate the install.json file data."""
        # all keys added to dict must be in camelCase
        install_json_data = {}

        # add standard fields
        self._add_standard_fields(install_json_data)

        # add app type api service fields
        self._add_type_api_service_fields(install_json_data)

        # add app type organization fields
        self._add_type_organization_fields(install_json_data)

        # add app type organization fields
        self._add_type_playbook_fields(install_json_data)

        # update sequence numbers
        for sequence, param in enumerate(install_json_data.get('params'), start=1):
            param['sequence'] = sequence

        return InstallJsonModel(**install_json_data)

    @staticmethod
    def generate_schema():
        """Return the schema for the install.json file."""
        return InstallJsonModel.schema_json(indent=2, sort_keys=True)
