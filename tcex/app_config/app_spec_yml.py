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
    ):
        """Initialize class properties."""
        filename = filename or 'app_spec.yml'
        path = path or os.getcwd()
        self.log = logger or tcex_logger

        # properties
        self.fqfn = Path(os.path.join(path, filename))

    @property
    def _feature_data_advanced_request_inputs(self):
        """Return all inputs for advanced request."""
        return [
            {
                'display': '''tc_action in ('Advanced Request')''',
                'label': 'API Endpoint/Path',
                'name': 'tc_adv_req_path',
                'note': 'The API Path request.',
                'playbookDataType': ['String'],
                'required': True,
                'type': 'String',
                'validValues': ['${TEXT}'],
            },
            {
                'display': '''tc_action in ('Advanced Request')''',
                'default': 'GET',
                'label': 'HTTP Method',
                'name': 'tc_adv_req_http_method',
                'note': 'HTTP method to use.',
                'required': True,
                'type': 'Choice',
                'validValues': ['GET', 'POST', 'DELETE', 'PUT', 'HEAD', 'PATCH', 'OPTIONS'],
            },
            {
                'display': '''tc_action in ('Advanced Request')''',
                'label': 'Query Parameters',
                'name': 'tc_adv_req_params',
                'note': (
                    'Query parameters to append to the URL. For sensitive information like API '
                    'keys, using variables is recommended to ensure that the Playbook will not '
                    'export sensitive data.'
                ),
                'playbookDataType': ['String', 'StringArray'],
                'required': False,
                'type': 'KeyValueList',
                'validValues': ['${KEYCHAIN}', '${TEXT}'],
            },
            {
                'display': '''tc_action in ('Advanced Request')''',
                'label': 'Exclude Empty/Null Parameters',
                'name': 'tc_adv_req_exclude_null_params',
                'note': (
                    '''Some API endpoint don't handle null/empty query parameters properly '''
                    '''(e.g., ?name=&type=String). If selected this options will exclude any '''
                    '''query parameters that has a null/empty value.'''
                ),
                'type': 'Boolean',
            },
            {
                'display': '''tc_action in ('Advanced Request')''',
                'label': 'Headers',
                'name': 'tc_adv_req_headers',
                'note': (
                    'Headers to include in the request. When using Multi-part Form/File data, '
                    'do **not** add a **Content-Type** header. For sensitive information like '
                    'API keys, using variables is recommended to ensure that the Playbook will '
                    'not export sensitive data.'
                ),
                'playbookDataType': ['String'],
                'required': False,
                'type': 'KeyValueList',
                'validValues': ['${KEYCHAIN}', '${TEXT}'],
            },
            {
                'display': (
                    '''tc_action in ('Advanced Request') AND tc_adv_req_http_method '''
                    '''in ('POST', 'PUT', 'DELETE', 'PATCH')'''
                ),
                'label': 'Body',
                'name': 'tc_adv_req_body',
                'note': 'Content of the HTTP request.',
                'playbookDataType': ['String', 'Binary'],
                'required': False,
                'type': 'String',
                'validValues': ['${KEYCHAIN}', '${TEXT}'],
                'viewRows': 4,
            },
            {
                'display': (
                    '''tc_action in ('Advanced Request') AND tc_adv_req_http_method '''
                    '''in ('POST', 'PUT', 'DELETE', 'PATCH')'''
                ),
                'label': 'URL Encode JSON Body',
                'name': 'tc_adv_req_urlencode_body',
                'note': (
                    '''URL encode a JSON-formatted body. Typically used for'''
                    ''' 'x-www-form-urlencoded' data, where the data can be configured in the '''
                    '''body as a JSON string.'''
                ),
                'type': 'Boolean',
            },
            {
                'display': '''tc_action in ('Advanced Request')''',
                'default': True,
                'label': 'Fail for Status',
                'name': 'tc_adv_req_fail_on_error',
                'note': 'Fail if the response status code is 4XX - 5XX.',
                'type': 'Boolean',
            },
        ]

    @staticmethod
    def _feature_data_advanced_request_outputs(prefix: str) -> dict:
        """Return all outputs for advanced request."""
        return {
            'display': 'tc_action in (\'Advanced Request\')',
            'outputVariables': [
                {
                    'name': f'{prefix}.request.content',
                },
                {
                    'name': f'{prefix}.request.content.binary',
                    'type': 'Binary',
                },
                {
                    'name': f'{prefix}.request.headers',
                },
                {
                    'name': f'{prefix}.request.ok',
                },
                {
                    'name': f'{prefix}.request.reason',
                },
                {
                    'name': f'{prefix}.request.status_code',
                },
                {
                    'name': f'{prefix}.request.url',
                },
            ],
        }

    def _migrate_schema_100_to_110(self, contents: dict):
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

        # migrate app.jira to internalNotes schema
        self._migrate_schema_100_to_110_jira_notes(contents)

        # migrate app.releaseNotes to new schema
        self._migrate_schema_100_to_110_release_notes(contents)

        # migrate app.retry to playbook.retry
        self._migrate_schema_100_to_110_retry(contents)

        # update the schema version
        contents['schemaVersion'] = contents.get('schemaVersion') or '1.1.0'

        # dict -> mode -> dict (filtered)
        self.rewrite_contents(contents)

    @staticmethod
    def _migrate_schema_100_to_110_app(contents: dict):
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        # remove "app" top level
        for k, v in dict(contents).get('app').items():
            contents[k] = v

        # assure minServerVersion exists
        if contents.get('minServerVersion') is None:
            contents['minServerVersion'] = '6.0.0'

        # remove "app" from "app_spec"
        del contents['app']

    @staticmethod
    def _migrate_schema_100_to_110_organization_feeds(contents: dict):
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        if contents.get('feeds') is not None and contents['runtimeLevel'].lower() == 'organization':
            contents.setdefault('organization', {})
            contents['organization']['feeds'] = contents.pop('feeds', [])

    @staticmethod
    def _migrate_schema_100_to_110_organization_repeating_minutes(contents: dict):
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        if (
            contents.get('repeatingMinutes') is not None
            and contents['runtimeLevel'].lower() == 'organization'
        ):
            contents.setdefault('organization', {})
            contents['organization']['repeatingMinutes'] = contents.pop('repeatingMinutes', [])

    @staticmethod
    def _migrate_schema_100_to_110_organization_publish_out_files(contents: dict):
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        if (
            contents.get('publishOutFiles') is not None
            and contents['runtimeLevel'].lower() == 'organization'
        ):
            contents.setdefault('organization', {})
            contents['organization']['publishOutFiles'] = contents.pop('publishOutFiles', [])

    @staticmethod
    def _migrate_schema_100_to_110_input_groups(contents: dict):
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        contents['sections'] = contents.pop('inputGroups', {})
        for section in contents.get('sections'):
            section['sectionName'] = section.pop('group')
            section['params'] = section.pop('inputs')

            # add missing name
            for param in section['params']:
                if param.get('name') is None:
                    param['name'] = param.get('label')

                if 'sequence' in param:
                    del param['sequence']

                if param.get('type') is None:
                    param['type'] = 'String'

    @staticmethod
    def _migrate_schema_100_to_110_notes_per_action(contents: dict):
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        contents['notePerAction'] = contents.pop('notes', {})
        note_per_action = []
        for action, note in contents['notePerAction'].items():
            note_per_action.append({'action': action, 'note': note})
        contents['notePerAction'] = note_per_action

    @staticmethod
    def _migrate_schema_100_to_110_retry(contents: dict):
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        if contents['runtimeLevel'].lower() == 'playbook':
            contents.setdefault('playbook', {})
            contents['playbook']['retry'] = contents.pop('retry', {})

    @staticmethod
    def _migrate_schema_100_to_110_output_groups(contents: dict):
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        outputs = []
        contents['outputData'] = contents.pop('outputGroups', {})
        for display, group in contents.get('outputData').items():
            output_data = {'display': display, 'outputVariables': []}

            # fix schema when output type is assumed
            if isinstance(group, list):
                group = {'String': group}

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
    def _migrate_schema_100_to_110_jira_notes(contents: dict):
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        jira_notes = []
        for k, v in contents.get('jira', {}).items():
            # look for the trailer to find our items
            if k == '_TRAILER_':
                for item in v:
                    jira_notes.append(item)
        contents['internalNotes'] = jira_notes

    @staticmethod
    def _migrate_schema_100_to_110_release_notes(contents: dict):
        """Migrate 1.0.0 schema to 1.1.0 schema."""
        release_notes = []
        for k, v in contents.get('releaseNotes').items():
            release_notes.append({'version': k, 'notes': v})
        contents['releaseNotes'] = release_notes

    @cached_property
    def contents(self) -> dict:
        """Return install.json file contents."""

        def _load_contents() -> dict:
            """Load contents from file."""
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
                self.log.error(
                    f'feature=app-spec-yml, exception=file-not-found, filename={self.fqfn}'
                )

            return contents

        contents = _load_contents()

        # migrate schema from 1.0.0 to 1.1.0
        if contents.get('schemaVersion', '1.0.0') == '1.0.0':
            self._migrate_schema_100_to_110(contents)
        else:
            # reformat file
            self.rewrite_contents(contents)

        # migrate schema
        return _load_contents()

    @staticmethod
    def dict_to_yaml(data: dict) -> str:
        """Convert dict to yaml."""
        return yaml.dump(
            data,
            Dumper=Dumper,
            default_flow_style=False,
            sort_keys=False,
        )

    @property
    def has_spec(self):
        """Return True if App has app_spec.yml file."""
        return self.fqfn.is_file()

    @cached_property
    def model(self) -> 'AppSpecYmlModel':
        """Return the Install JSON model.

        If writing app_spec.yml file after the method then the model will include
        advancedRequest inputs/outputs, etc.
        """
        _contents = self.contents
        # special case for dynamic handling of advancedRequest feature
        if 'advancedRequest' in _contents.get('features', []):

            # Add "Advanced Request" action to Valid Values
            # when "advancedRequest" feature is enabled
            for section in _contents.get('sections', []):
                for param in section.get('params', []):
                    if param.get('name') == 'tc_action' and 'Advanced Request' not in param.get(
                        'validValues', []
                    ):
                        param['validValues'].append('Advanced Request')

                if section.get('sectionName') == 'Configure':
                    section['params'].extend(self._feature_data_advanced_request_inputs)

            # add outputs
            prefix = _contents.get('outputPrefix', '')
            _contents['outputData'].append(self._feature_data_advanced_request_outputs(prefix))

        return AppSpecYmlModel(**self.contents)

    @staticmethod
    def order_data(asy_data: dict) -> dict:
        """Order field with direction given by Business Analysis."""
        asy_data_ordered = {}

        # "important" fields
        asy_data_ordered['displayName'] = asy_data.get('displayName')
        asy_data_ordered['packageName'] = asy_data.get('packageName')
        asy_data_ordered['appId'] = asy_data.get('appId')
        asy_data_ordered['category'] = asy_data.get('category', '')
        asy_data_ordered['programVersion'] = asy_data.get('programVersion')
        if asy_data.get('displayPath') is not None:
            asy_data_ordered['displayPath'] = asy_data.get('displayPath')
        if asy_data.get('internalNotes') is not None:
            asy_data_ordered['internalNotes'] = asy_data.get('internalNotes', [])
        asy_data_ordered['releaseNotes'] = asy_data.get('releaseNotes', [])
        asy_data_ordered['deprecatesApps'] = asy_data.get('deprecatesApps', [])
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
        if asy_data.get('runtimeLevel').lower() not in ('apiservice', 'organization'):
            asy_data_ordered['outputData'] = asy_data.get('outputData')
        if asy_data.get('outputPrefix'):
            asy_data_ordered['outputPrefix'] = asy_data.get('outputPrefix')

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

    def rewrite_contents(self, contents: dict):
        """Rewrite app_spec.yml file."""
        # fix for null appId value
        if 'appId' in contents and contents.get('appId') is None:
            del contents['appId']

        # exclude_defaults - if False then all unused fields are added in - not good.
        # exclude_none - this should be safe to leave as True.
        # exclude_unset - this should be False to ensure that all fields are included.
        contents = json.loads(
            AppSpecYmlModel(**contents).json(
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=False,
                sort_keys=True,
            )
        )

        # write the new contents to the file
        self.write(contents)

        return contents

    def write(self, contents: dict):
        """Write yaml to file."""
        with self.fqfn.open(mode='w', encoding='utf-8') as fh:
            fh.write(self.dict_to_yaml(self.order_data(contents)))
