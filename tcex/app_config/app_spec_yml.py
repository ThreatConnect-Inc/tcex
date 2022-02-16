"""App Spec Yml App Config"""
# standard library
import json
import logging
import os
from pathlib import Path
from typing import Optional

# third-party
import yaml

try:
    # third-party
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper

# first-party
from tcex.app_config.models import AppSpecYmlModel
from tcex.backports import cached_property

# get tcex logger
tcex_logger = logging.getLogger('tcex')


class AppSpecYml:
    """Provide a model for the app_spec.yml config file."""

    def __init__(
        self,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize class properties."""
        filename = filename or 'app_spec.yml'
        path = path or os.getcwd()
        self.log = logger or tcex_logger

        # properties
        self.fqfn = Path(os.path.join(path, filename))

    def _migrate_schema_100_to_110(self, contents: dict) -> None:
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        # moved app.* to top level
        self._migrate_schema_100_to_110_app(contents)

        # migrate app.feeds to app.organization.feeds
        self._migrate_schema_100_to_110_organization_feeds(contents)

        # migrate app.feeds to app.organization.repeating_minutes
        self._migrate_schema_100_to_110_organization_repeating_minutes(contents)

        # migrate app.feeds to app.organization.publish_out_files
        self._migrate_schema_100_to_110_organization_publish_out_files(contents)

        # migrate app.inputGroup to new schema
        self._migrate_schema_100_to_110_input_groups(contents)

        # migrate app.note to app.notePerAction with new schema
        self._migrate_schema_100_to_110_notes_per_action(contents)

        # migrate app.outputGroups to outputData with new schema
        self._migrate_schema_100_to_110_output_groups(contents)

        # migrate app.playbookType to category
        contents['category'] = contents.pop('playbookType', '')

        # migrate app.releaseNotes to new schema
        self._migrate_schema_100_to_110_release_notes(contents)

        # migrate app.retry to playbook.retry
        self._migrate_schema_100_to_110_retry(contents)

        # remove deprecated playbook.outputPrefix field
        if contents.get('outputPrefix') is not None:
            del contents['outputPrefix']

        # update the schema version
        contents['schemaVersion'] = contents.get('schemaVersion') or '1.1.0'

        # dict -> mode -> dict (filtered)
        contents = json.loads(
            AppSpecYmlModel(**contents).json(
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=True,
                sort_keys=True,
            )
        )

        # write the new contents to the file
        self.write(contents)

    @staticmethod
    def _migrate_schema_100_to_110_app(contents: dict) -> None:
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        # remove "app" top level
        for k, v in dict(contents).get('app').items():
            contents[k] = v

        # remove "app" from "app_spec"
        del contents['app']

    @staticmethod
    def _migrate_schema_100_to_110_organization_feeds(contents: dict) -> None:
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        if contents.get('feeds') is not None and contents['runtimeLevel'].lower() == 'organization':
            contents.setdefault('organization', {})
            contents['organization']['feeds'] = contents.pop('feeds', [])

    @staticmethod
    def _migrate_schema_100_to_110_organization_repeating_minutes(contents: dict) -> None:
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        if (
            contents.get('repeatingMinutes') is not None
            and contents['runtimeLevel'].lower() == 'organization'
        ):
            contents.setdefault('organization', {})
            contents['organization']['repeatingMinutes'] = contents.pop('repeatingMinutes', [])

    @staticmethod
    def _migrate_schema_100_to_110_organization_publish_out_files(contents: dict) -> None:
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        if (
            contents.get('publishOutFiles') is not None
            and contents['runtimeLevel'].lower() == 'organization'
        ):
            contents.setdefault('organization', {})
            contents['organization']['publishOutFiles'] = contents.pop('publishOutFiles', [])

    @staticmethod
    def _migrate_schema_100_to_110_input_groups(contents: dict) -> None:
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        contents['sections'] = contents.pop('inputGroups', {})
        for section in contents.get('sections'):
            section['sectionName'] = section.pop('group')
            section['params'] = section.pop('inputs')

            # add missing name
            for param in section['params']:
                if param.get('name') is None:
                    param['name'] = param.get('label').replace(' ', '_').lower()

                if param.get('type') is None:
                    param['type'] = 'String'

                # This can probably be removed. Default values are set when
                # writing the output files instead of keeping in the model.

                # if (
                #     contents['runtimeLevel'].lower() == 'playbook'
                #     and param.get('playbookDataType') is None
                #     and param.get('type') == 'String'
                # ):
                #     param['playbookDataType'] = ['String']

                # if (
                #     param.get('validValues') is None
                #     and param.get('type') == 'String'
                #     and 'String' in param.get('playbookDataType', [])
                # ):
                #     param['validValues'] = ['${TEXT}']
                #     if param.get('encrypt') is True:
                #         param['validValues'] = ['${KEYCHAIN}']

    @staticmethod
    def _migrate_schema_100_to_110_notes_per_action(contents: dict) -> None:
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        contents['notePerAction'] = contents.pop('notes', {})
        note_per_action = []
        for action, note in contents['notePerAction'].items():
            note_per_action.append({'action': action, 'note': note})
        contents['notePerAction'] = note_per_action

    @staticmethod
    def _migrate_schema_100_to_110_retry(contents: dict) -> None:
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        if contents['runtimeLevel'].lower() == 'playbook':
            contents.setdefault('playbook', {})
            contents['playbook']['retry'] = contents.pop('retry', {})

    @staticmethod
    def _migrate_schema_100_to_110_output_groups(contents: dict) -> None:
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        outputs = []
        contents['outputData'] = contents.pop('outputGroups', {})
        for output, group in contents.get('outputData').items():
            output_data = {'display': output, 'outputVariables': []}

            for variable_type, variables in group.items():
                for name in variables:
                    disabled = False
                    if name.startswith('~'):
                        name = name.replace('~', '')
                        disabled = True

                    output_data['outputVariables'].append(
                        {
                            'disabled': disabled,
                            'encrypt': False,
                            'intelTypes': [],
                            'name': name,
                            'note': None,
                            'type': variable_type,
                        }
                    )
            outputs.append(output_data)
        contents['outputData'] = outputs

    @staticmethod
    def _migrate_schema_100_to_110_release_notes(contents: dict) -> None:
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        release_notes = []
        for k, v in contents.get('releaseNotes').items():
            release_notes.append({'version': k, 'notes': v})
        contents['releaseNotes'] = release_notes

    @cached_property
    def contents(self) -> dict:
        """Return install.json file contents."""
        contents = {}
        if self.fqfn.is_file():
            try:
                with self.fqfn.open() as fh:
                    contents = yaml.load(fh, Loader=Loader)  # nosec
            except (OSError, ValueError):  # pragma: no cover
                self.log.error(
                    f'feature=app-spec-yml, exception=failed-reading-file, filename={self.fqfn}'
                )
        else:  # pragma: no cover
            self.log.error(f'feature=app-spec-yml, exception=file-not-found, filename={self.fqfn}')

        # migrate schema from 1.0.0 to 1.1.0
        if contents.get('schemaVersion', '1.0.0') == '1.0.0':
            self._migrate_schema_100_to_110(contents)

            # clear cache for data property
            if 'contents' in self.__dict__:
                del self.__dict__['contents']

            # read contents again after migration
            return self.contents

        # migrate schema
        return contents

    @staticmethod
    def dict_to_yaml(data: dict) -> str:
        """Convert dict to yaml."""
        return yaml.dump(data, Dumper=Dumper, default_flow_style=False, sort_keys=False)

    @cached_property
    def model(self) -> 'AppSpecYmlModel':
        """Return the Install JSON model."""
        return AppSpecYmlModel(**self.contents)

    @staticmethod
    def order_data(asy_data: dict) -> dict:
        """Order field with direction given by Business Analysis."""
        asy_data_ordered = {}

        # "important" fields
        asy_data_ordered['displayName'] = asy_data.get('displayName')
        asy_data_ordered['appId'] = asy_data.get('appId')
        asy_data_ordered['category'] = asy_data.get('category', '')
        asy_data_ordered['programVersion'] = asy_data.get('programVersion')
        if asy_data.get('displayPath') is not None:
            asy_data_ordered['displayPath'] = asy_data.get('displayPath')
        asy_data_ordered['releaseNotes'] = asy_data.get('releaseNotes', [])
        asy_data_ordered['deprecatedApps'] = asy_data.get('deprecatedApps', [])
        asy_data_ordered['features'] = asy_data.get('features')
        asy_data_ordered['labels'] = asy_data.get('labels', [])
        asy_data_ordered['minServerVersion'] = asy_data.get('minServerVersion')
        asy_data_ordered['note'] = asy_data.get('note') or ''
        if asy_data.get('notePerAction') is not None:
            asy_data_ordered['notePerAction'] = asy_data.get('notePerAction')
        asy_data_ordered['runtimeLevel'] = asy_data.get('runtimeLevel')

        # per runtime level (App type)
        if asy_data.get('organization'):
            asy_data_ordered['organization'] = asy_data.get('organization')
        if asy_data.get('playbook'):
            asy_data_ordered['playbook'] = asy_data.get('playbook')
        if asy_data.get('service'):
            asy_data_ordered['service'] = asy_data.get('service')

        # inputs / outputs
        asy_data_ordered['sections'] = asy_data.get('sections')
        if asy_data.get('outputData'):
            asy_data_ordered['outputData'] = asy_data.get('outputData')

        # standard fields
        asy_data_ordered['allowOnDemand'] = asy_data.get('allowOnDemand', True)
        if asy_data.get('allowRunAsUser') is not None:
            asy_data_ordered['allowRunAsUser'] = asy_data.get('allowRunAsUser')
        asy_data_ordered['programLanguage'] = asy_data.get('programLanguage')
        asy_data_ordered['languageVersion'] = asy_data.get('languageVersion')
        asy_data_ordered['programMain'] = asy_data.get('programMain')
        asy_data_ordered['listDelimiter'] = asy_data.get('listDelimiter')

        # auto-generated
        asy_data_ordered['schemaVersion'] = str(asy_data.get('schemaVersion', '1.1.0'))

        return asy_data_ordered

    def write(self, contents: dict) -> None:
        """Write yaml to file."""
        with self.fqfn.open(mode='w') as fh:
            fh.write(self.dict_to_yaml(self.order_data(contents)))
