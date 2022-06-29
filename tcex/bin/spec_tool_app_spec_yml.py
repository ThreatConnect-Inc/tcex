"""TcEx Generate Configurations CLI Command"""
# standard library
import json
import os

# third-party
from semantic_version import Version

# first-party
from tcex.app_config import AppSpecYml, InstallJson, JobJson, LayoutJson, TcexJson
from tcex.app_config.models import AppSpecYmlModel
from tcex.bin.bin_abc import BinABC


class SpecToolAppSpecYml(BinABC):
    """Generate App Config File"""

    def __init__(self):
        """Initialize class properties."""
        super().__init__()

        # properties
        self.filename = 'app_spec.yml'
        self.asy = AppSpecYml(logger=self.log)
        self.ij = InstallJson(logger=self.log)
        self.jj = JobJson(logger=self.log)
        self.lj = LayoutJson(logger=self.log)
        self.tj = TcexJson(logger=self.log)

    def _add_standard_fields(self, app_spec_yml_data: dict):
        """Add field that apply to ALL App types."""
        app_spec_yml_data.update(
            {
                'allowOnDemand': self.ij.model.allow_on_demand,
                'apiUserTokenParam': self.ij.model.api_user_token_param,
                'appId': str(self.ij.model.app_id),
                'category': self.ij.model.category,
                'deprecatesApps': self.ij.model.deprecates_apps,
                'displayName': self.ij.model.display_name,
                'features': self.ij.model.features,
                'labels': self.ij.model.labels,
                'languageVersion': self.ij.model.language_version,
                'listDelimiter': self.ij.model.list_delimiter,
                'minServerVersion': str(self.ij.model.min_server_version),
                'note': self.ij.model.note,
                'outputPrefix': self.ij.model.playbook.output_prefix,
                'packageName': self.tj.model.package.app_name,
                'programLanguage': self.ij.model.program_language,
                'programMain': self.ij.model.program_main,
                'programVersion': str(self.ij.model.program_version),
                'runtimeLevel': self.ij.model.runtime_level,
            }
        )

    def _add_category(self, app_spec_yml_data: dict):
        """Add category."""
        _category = ''
        if self.ij.model.runtime_level.lower() != 'organization':
            _category = self.ij.model.playbook.type or ''
        app_spec_yml_data['category'] = _category

    def _add_feeds(self, app_spec_yml_data: dict):
        """Add organization feeds section."""
        if self.ij.model.runtime_level.lower() != 'organization':
            return

        feeds = []
        for feed in self.ij.model.feeds or []:
            if not os.path.isfile(feed.job_file):
                self.log.error(
                    f'feature=app-spec-yml, exception=failed-reading-file, filename={feed.job_file}'
                )
                continue
            with open(feed.job_file) as f:
                job = json.load(f)
            feed = feed.dict(by_alias=True)
            feed['job'] = job
            feeds.append(feed)
        app_spec_yml_data.setdefault('organization', {})
        app_spec_yml_data['organization']['feeds'] = feeds

    def _add_note_per_action(self, app_spec_yml_data: dict):
        """Add note per action."""
        _notes_per_action = []
        param = self.ij.model.get_param('tc_action')
        if param.valid_values:
            for action in param.valid_values:
                _notes_per_action.append({'action': action, 'note': ''})

            app_spec_yml_data['notesPerAction'] = _notes_per_action

    def _add_organization(self, app_spec_yml_data: dict):
        """Add asy.organization."""
        if self.ij.model.runtime_level.lower() == 'organization':
            app_spec_yml_data.setdefault('organization', {})
            if self.ij.model.publish_out_files:
                app_spec_yml_data['organization'][
                    'publishOutFiles'
                ] = self.ij.model.publish_out_files
            if self.ij.model.repeating_minutes:
                app_spec_yml_data['organization'][
                    'repeatingMinutes'
                ] = self.ij.model.repeating_minutes

    def _add_output_data(self, app_spec_yml_data: dict):
        """Add asy.outputData."""
        if self.ij.model.runtime_level.lower() != 'organization':
            # build outputs based on display value
            _output_data_temp = {}
            if self.lj.has_layout:
                # layout based Apps could will have a display clause for each output
                for o in self.ij.model.playbook_outputs.values():
                    o = self.lj.model.get_output(o.name)
                    _output_data_temp.setdefault(o.display or '1', []).append(o.name)
            else:
                for _, o in self.ij.model.playbook_outputs.items():
                    _output_data_temp.setdefault('1', []).append(o.name)

            _output_data = []
            for display, names in _output_data_temp.items():
                _output_variables = []
                for name in names:
                    if not self._is_advanced_request_output(name):
                        _output_variables.append(self.ij.model.get_output(name).dict(by_alias=True))

                _output_data.append({'display': display, 'outputVariables': _output_variables})

            app_spec_yml_data['outputData'] = _output_data

    def _add_playbook(self, app_spec_yml_data: dict):
        """Add asy.playbook."""
        if self.ij.model.runtime_level.lower() != 'organization':
            app_spec_yml_data.setdefault('playbook', {})
            if self.ij.model.playbook.retry:
                app_spec_yml_data['playbook']['retry'] = self.ij.model.playbook.retry

    @staticmethod
    def _add_release_notes(app_spec_yml_data: dict):
        """Add release_notes."""
        app_spec_yml_data['releaseNotes'] = [
            {
                'notes': ['Initial Release'],
                'version': '1.0.0',
            }
        ]

    def _add_sections(self, app_spec_yml_data: dict):
        """Return params from ij and lj formatted for app_spec."""
        sections = []
        for section in self._current_data:
            _section_data = {'sectionName': section.get('title'), 'params': []}
            for p in section.get('parameters', []):
                if not self._is_advanced_request_input(p.get('name')):
                    param = self.ij.model.get_param(p.get('name')).dict(by_alias=True)
                    param['display'] = p.get('display')
                    _section_data['params'].append(param)
            sections.append(_section_data)
        app_spec_yml_data['sections'] = sections

    @property
    def _current_data(self):
        """Retrieve the appropriate data regardless of if its a layout based app."""
        if self.lj.has_layout:
            # handle layout based Apps
            _current_data = [i.dict(by_alias=True) for i in self.lj.model.inputs]

            # add hidden inputs from install.json (hidden inputs are not in layouts.json)
            _current_data.append(
                {
                    'parameters': [
                        p.dict(by_alias=True) for p in self.ij.model.params if p.hidden is True
                    ],
                    'title': 'Hidden Inputs',
                }
            )
        else:
            # handle non-layout based Apps
            _current_data = [
                {
                    'parameters': [p.dict(by_alias=True) for p in self.ij.model.params],
                    'title': 'Inputs',
                }
            ]
        return _current_data

    def _is_64_min_version(self) -> bool:
        """Return params from ij and lj formatted for app_spec."""

        for section in self._current_data:
            for p in section.get('parameters', []):
                param = self.ij.model.get_param(p.get('name')).dict(by_alias=True)
                if param['type'].lower() == 'editchoice':
                    return True
        return False

    @staticmethod
    def _is_advanced_request_input(name: str) -> bool:
        """Return true if input is an Advanced Request input."""
        return name in [
            'tc_adv_req_path',
            'tc_adv_req_http_method',
            'tc_adv_req_params',
            'tc_adv_req_exclude_null_params',
            'tc_adv_req_headers',
            'tc_adv_req_body',
            'tc_adv_req_urlencode_body',
            'tc_adv_req_fail_on_error',
        ]

    @staticmethod
    def _is_advanced_request_output(name: str) -> bool:
        """Return true if input is an Advanced Request input."""
        return name in [
            'any_run.request.content',
            'any_run.request.content.binary',
            'any_run.request.headers',
            'any_run.request.ok',
            'any_run.request.reason',
            'any_run.request.status_code',
            'any_run.request.url',
        ]

    def _add_min_tc_version(self, app_spec_yml_data: dict):
        """Add the correct min TC server version."""

        if self._is_64_min_version() and self.ij.model.min_server_version < Version('6.4.0'):
            app_spec_yml_data['minServerVersion'] = '6.4.0'

    def generate(self):
        """Generate the layout.json file data."""
        app_spec_yml_data = {}

        # add feeds
        self._add_feeds(app_spec_yml_data)

        # add release notes
        self._add_release_notes(app_spec_yml_data)

        # add standard fields
        self._add_standard_fields(app_spec_yml_data)

        # add category
        self._add_category(app_spec_yml_data)

        # add note per action
        self._add_note_per_action(app_spec_yml_data)

        # add organization (feed, jobs, etc)
        self._add_organization(app_spec_yml_data)

        # add playbook (retry)
        self._add_playbook(app_spec_yml_data)

        # add sections
        self._add_sections(app_spec_yml_data)

        # add output data
        self._add_output_data(app_spec_yml_data)

        # parse and validate the data (use json so that json_encoder convert complex types)
        asy_data = json.loads(
            AppSpecYmlModel(**app_spec_yml_data).json(
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=True,
                sort_keys=False,
            )
        )

        # force order of keys
        return self.asy.dict_to_yaml(self.asy.order_data(asy_data))

    @staticmethod
    def generate_schema():
        """Return the schema for the install.json file."""
        return AppSpecYmlModel.schema_json(indent=2, sort_keys=True)
