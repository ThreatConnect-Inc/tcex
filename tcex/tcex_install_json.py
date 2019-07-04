#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Bin Command Base Module."""
import json
import os


class InstallJson(object):
    """Object for install.json file."""

    def __init__(self, filename=None, path=None):
        """Initialize class properties."""
        self.filename = filename or 'install.json'
        if path is not None:
            self.filename = os.path.join(path, self.filename)

        # properties
        self._contents = None

    @staticmethod
    def _to_bool(value):
        """Convert string value to bool."""
        bool_value = False
        if str(value).lower() in ['1', 'true']:
            bool_value = True
        return bool_value

    @staticmethod
    def expand_valid_values(valid_values):
        """Expand supported playbook variables to their full list.

        Args:
            valid_values (list): The list of valid values for Choice or MultiChoice inputs.

        Returns:
            list: An expanded list of valid values for Choice or MultiChoice inputs.
        """

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
            valid_values.append('')
        elif '${USERS}' in valid_values:
            valid_values.remove('${USERS}')
            valid_values.append('')
        return valid_values

    @property
    def contents(self):
        """Return install.json contents."""
        if self._contents is None:
            with open(self.filename, 'r') as fh:
                self._contents = json.load(fh)
        return self._contents

    @property
    def config_params_dict(self):
        """Return params as name/data dict."""
        params = {}
        for p in self.params:
            if p.get('config'):
                params.setdefault(p.get('name'), p)
        return params

    def filter_params_dict(self, config=None, name=None, required=None, _type=None):
        """Return params as name/data dict."""
        params = {}
        for p in self.params:
            if config is not None:
                if p.get('config') is not config:
                    continue

            if name is not None:
                if p.get('name') == name:
                    continue

            if required is not None:
                if p.get('required') is not required:
                    continue

            if _type is not None:
                if p.get('type') is not _type:
                    continue

            params.setdefault(p.get('name'), p)
        return params

    @property
    def optional_params_dict(self):
        """Return params as name/data dict."""
        params = {}
        for p in self.params:
            if p.get('required') is False:
                params.setdefault(p.get('name'), p)
        return params

    def output_variables_dict(self):
        """Return output variables as name/data dict."""
        output_variables = {}
        for o in self.contents.get('playbook', {}).get('outputVariables') or []:
            output_variables.setdefault(o.get('name'), o)
        return output_variables

    @property
    def params_dict(self):
        """Return params as name/data dict."""
        params = {}
        for p in self.params:
            params.setdefault(p.get('name'), p)
        return params

    def params_to_args(self, config=None, name=None, required=None, _type=None):
        """Return params as name/data dict."""
        args = {}
        for n, p in self.filter_params_dict(config, name, required, _type).items():
            if p.get('type').lower() == 'boolean':
                args[p.get('name')] = self._to_bool(p.get('default', False))
            elif p.get('type').lower() == 'choice':
                valid_values = '|'.join(self.expand_valid_values(p.get('validValues', [])))
                args[p.get('name')] = '[{}]'.format(valid_values)
            elif p.get('type').lower() == 'multichoice':
                args[p.get('name')] = p.get('validValues', [])
            elif p.get('type').lower() == 'keyvaluelist':
                args[p.get('name')] = '<KeyValueList>'
            elif p.get('name') in ['api_access_id', 'api_secret_key']:
                # leave these parameters set to the value defined in defaults
                pass
            else:
                types = '|'.join(p.get('playbookDataType', []))
                if types:
                    args[p.get('name')] = p.get('default', '<{}>'.format(types))
                else:
                    args[p.get('name')] = p.get('default', '')
        return args

    @property
    def require_params_dict(self):
        """Return params as name/data dict."""
        params = {}
        for p in self.params:
            if p.get('required') is True:
                params.setdefault(p.get('name'), p)
        return params

    #
    # properties
    #

    @property
    def allow_on_demand(self):
        """Return property."""
        return self.contents.get('allowOnDemand', False)

    @property
    def display_name(self):
        """Return property."""
        return self.contents.get('displayName')

    @property
    def features(self):
        """Return property."""
        return self.contents.get('features', [])

    @property
    def feeds(self):
        """Return property."""
        return self.contents.get('feeds', {})

    @property
    def labels(self):
        """Return property."""
        return self.contents.get('labels', [])

    @property
    def language_version(self):
        """Return property."""
        return self.contents.get('languageVersion')

    @property
    def list_delimiter(self):
        """Return property."""
        return self.contents.get('listDelimiter')

    @property
    def min_server_version(self):
        """Return property."""
        return self.contents.get('minServerVersion')

    @property
    def note(self):
        """Return property."""
        return self.contents.get('note')

    @property
    def params(self):
        """Return property."""
        return self.contents.get('params', [])

    @property
    def playbook(self):
        """Return property."""
        return self.contents.get('playbook', {})

    @property
    def program_icon(self):
        """Return property."""
        return self.contents.get('programIcon')

    @property
    def program_language(self):
        """Return property."""
        return self.contents.get('programLanguage')

    @property
    def program_main(self):
        """Return property."""
        return self.contents.get('programMain')

    @property
    def program_name(self):
        """Return property."""
        return self.contents.get('programName')

    @property
    def program_version(self):
        """Return property."""
        return self.contents.get('programVersion')

    @property
    def publish_out_files(self):
        """Return property."""
        return self.contents.get('publishOutFiles')

    @property
    def repeating_minutes(self):
        """Return property."""
        return self.contents.get('repeatingMinutes')

    @property
    def runtime_context(self):
        """Return property."""
        return self.contents.get('runtimeContext')

    @property
    def runtime_level(self):
        """Return property."""
        return self.contents.get('runtimeLevel')
