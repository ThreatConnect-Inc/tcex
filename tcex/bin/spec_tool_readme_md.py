"""TcEx Generate Configurations CLI Command"""
# standard library
from typing import TYPE_CHECKING, List, Optional

# first-party
from tcex.app_config.permutation import Permutation
from tcex.bin.bin_abc import BinABC

if TYPE_CHECKING:
    # first-party
    from tcex.app_config import AppSpecYml
    from tcex.app_config.install_json import ParamsModel
    from tcex.app_config.models.app_spec_yml_model import SectionsModel


class SpecToolReadmeMd(BinABC):
    """Generate App Config File"""

    def __init__(self, asy: 'AppSpecYml'):
        """Initialize class properties."""
        super().__init__()
        self.asy = asy

        # properties
        # self.i1 = ' ' * 2
        self.i1 = ''
        self.filename = 'README.md'
        self.permutations = Permutation(self.log)

    @staticmethod
    def _add_actions_title(readme_md: List[str]):
        """Add title for action section."""
        readme_md.append('# Actions')
        readme_md.append('')
        readme_md.append('---')
        readme_md.append('')

    def _add_actions_sub_title(self, readme_md: List[str], action: str):
        """Add title for sub action section."""
        readme_md.append(f'## {action}')
        readme_md.append('')
        npa = self.asy.model.get_note_per_action(action).note
        if npa is not None:
            readme_md.append(self.asy.model.get_note_per_action(action).note)
            readme_md.append('')

    def _add_labels(self, readme_md: List[str]):
        """Add labels data to readme.md."""
        if self.asy.model.labels:
            readme_md.append('# Labels')
            readme_md.append('')
            _labels = ', '.join(sorted(self.asy.model.labels))
            readme_md.append(f'-   {_labels}')

    def _add_description(self, readme_md: List[str]):
        """Add top level description/note data to readme.md."""
        if self.asy.model.note:
            readme_md.append('# Description')
            readme_md.append('')
            readme_md.append(self.asy.model.note)
            readme_md.append('')
            if self.asy.model.note_per_action:
                readme_md.append('\n\n'.join(self.asy.model.note_per_action_formatted))
                readme_md.append('')

    @staticmethod
    def _add_inputs_title(readme_md: List[str], header: int):
        """Add title for input section."""
        header_value = '#' * header
        readme_md.append(f'{header_value} Inputs')
        readme_md.append('')

    @staticmethod
    def _add_service_config_title(readme_md: List[str], header: int):
        """Add title for service configuration section."""
        header_value = '#' * header
        readme_md.append(f'{header_value} Service Configuration')
        readme_md.append('')

    def _add_param(self, readme_md: List[str], param: 'ParamsModel'):
        """Add params data to readme.md.

        **API Key** _(String)_
        _**Duration**_ _(String, Optional)_
        """
        label = f'**{param.label}**'
        type_data = f'{param.type}'

        if param.required is False:
            # change the format of the label name to italics if it is optional
            if param.type.lower() not in ['boolean']:
                label = f'_{label}_'
                type_data += ', Optional'

        if param.default is not None:
            # following current format where boolean values are shown as
            # selected/unselected and others true/false
            if param.type.lower() == 'boolean':
                default_value = 'Selected' if param.default is True else 'Unselected'
            else:
                default_value = param.default
            type_data += f''', Default: {str(default_value).replace('|', ', ')}'''

        readme_md.append(f'{self.i1}{label} _({type_data})_')
        readme_md.append('')

    def _add_params(
        self, readme_md: List[str], section: 'SectionsModel', action: Optional[str] = None
    ):
        # add params
        for param in section.params:
            if param.disabled is True or param.hidden is True:
                continue

            # don't add tc_action param since it's the top level action
            if param.name == 'tc_action':
                continue

            if action is not None:
                # validate that the input is valid for the current action
                if self._valid_param_for_action(param, action) is False:
                    continue

            # add param data
            self._add_param(readme_md, param)

            # add param note data
            self._add_param_note(readme_md, param)

            # add param playbook data types data
            self._add_param_pb_data_type(readme_md, param)

            # add param valid_values data
            self._add_param_valid_values(readme_md, param)

    def _add_param_note(self, readme_md: List[str], param: 'ParamsModel'):
        """Add note data to readme.md."""
        if param.note:
            readme_md.append(f'{self.i1}{param.note}')
            readme_md.append('')

    def _add_param_pb_data_type(self, readme_md: List[str], param: 'ParamsModel'):
        """Add playbook data types values data to readme.md."""
        # matching current format where single 'String' is not displayed
        if param.playbook_data_type and param.playbook_data_type != ['String']:
            _pdt = ', '.join(param.playbook_data_type)
            readme_md.append(f'{self.i1}> **Allows:** {_pdt}')
            readme_md.append('')

    def _add_param_valid_values(self, readme_md: List[str], param: 'ParamsModel'):
        """Add valid values data to readme.md."""
        # matching current format where TEXT and KEYCHAIN were excluded.
        valid_values = [p for p in param.valid_values if not p.startswith('${')]
        if valid_values:
            _valid_values = ', '.join(valid_values)
            readme_md.append(f'{self.i1}> **Valid Values:** {_valid_values}')
            readme_md.append('')

    def _add_outputs(self, readme_md: List[str], action: str = None):
        """Add output data to readme.md."""
        if self.asy.model.output_variables:
            readme_md.append('### Outputs')
            readme_md.append('')
            outputs = self.ij.model.playbook.output_variables
            if action:
                outputs = self.permutations.outputs_by_action(action)

            for output in outputs:
                readme_md.append(f'{self.i1}-   {output.name} _({output.type})_')

            readme_md.append('')

    def _has_section_params(self, section: 'SectionsModel', action: str) -> bool:
        """Return True if the provided section has params."""
        if [
            sp
            for sp in section.params
            if not any([sp.disabled, sp.hidden, sp.service_config])
            and sp.name != 'tc_action'
            and self._valid_param_for_action(sp, action) is True
        ]:
            return True
        return False

    def _valid_param_for_action(self, param: 'ParamsModel', action: str) -> bool:
        """Return True if param is valid for action."""
        return self.permutations.validate_input_variable(
            param.name,
            {'tc_action': action},
            self.permutations.extract_tc_action_clause(param.display),
        )

    @staticmethod
    def _add_section_title(readme_md: List[str], section: 'SectionsModel'):
        """Add title for input section."""
        readme_md.append(f'### _{section.section_name}_')
        readme_md.append('')

    def _add_params_for_playbook_action_app(self, readme_md: List[str], actions: List[str]):
        """Add inputs for playbook action app."""
        # add title for actions section
        self._add_actions_title(readme_md)

        for action in actions:

            # add title for action sub section
            self._add_actions_sub_title(readme_md, action)

            # add inputs and sections
            self._add_inputs_title(readme_md, 3)

            for section in self.asy.model.sections:
                # don't show the section if it has no params
                if self._has_section_params(section, action) is False:
                    continue

                # add section title
                self._add_section_title(readme_md, section)

                # add params
                self._add_params(readme_md, section, action)

            # add output data
            self._add_outputs(readme_md, action)

            # add horizontal rule
            readme_md.append('---')
            readme_md.append('')

    def _add_params_for_playbook_std_app(self, readme_md: List[str]):
        """Add inputs for playbook standard app."""
        self._add_inputs_title(readme_md, 3)

        for section in self.asy.model.sections:
            # don't show the section if it has no params
            valid_section = False
            for sp in section.params:
                if sp.disabled is False and sp.hidden is False:
                    valid_section = True

            if valid_section is False:
                continue

            # add section title
            self._add_section_title(readme_md, section)

            self._add_params(readme_md, section)

            # add output data
            self._add_outputs(readme_md)

    def _add_params_for_non_playbook_apps(self, readme_md: List[str]):
        """Add inputs for non playbook app."""
        service_config = []
        non_service_config = []

        # Separate Params into service configuration params and other parameters
        for param in self.asy.model.params:
            if param.disabled is True or param.hidden is True:
                continue
            if param.service_config is True:
                service_config.append(param)
            else:
                non_service_config.append(param)

        # Add service configuration params to ReadMe file.
        if service_config:
            self._add_service_config_title(readme_md, 1)

            for param in service_config:
                # add param data
                self._add_param(readme_md, param)

                # add param note data
                self._add_param_note(readme_md, param)

                # add param valid_values data
                self._add_param_valid_values(readme_md, param)

        # add inputs and sections
        self._add_inputs_title(readme_md, 3)

        for param in non_service_config:
            # add param data
            self._add_param(readme_md, param)

            # add param note data
            self._add_param_note(readme_md, param)

            # add param valid_values data
            self._add_param_valid_values(readme_md, param)

        # add output data
        self._add_outputs(readme_md)

    def generate(self) -> List[str]:
        """Generate the layout.json file data."""
        readme_md = []

        # add App Name
        readme_md.append(f'# {self.asy.model.display_name}')
        readme_md.append('')

        # add release notes
        readme_md.extend(self.asy.model.release_notes_formatted)

        # add category
        if self.asy.model.category:
            readme_md.append('# Category')
            readme_md.append('')
            readme_md.append(f'-   {self.asy.model.category}')
            readme_md.append('')

        # add description
        self._add_description(readme_md)

        # add inputs
        if self.asy.model.runtime_level.lower() == 'playbook':
            actions = self.ij.model.get_param('tc_action').valid_values or []
            if actions:
                # add inputs for action based sections
                self._add_params_for_playbook_action_app(readme_md, actions)
            else:
                # add inputs for non action based sections
                self._add_params_for_playbook_std_app(readme_md)

        elif self.asy.model.runtime_level.lower() in [
            'triggerservice',
            'webhooktriggerservice',
            'organization',
        ]:
            self._add_params_for_non_playbook_apps(readme_md)

        # add labels
        self._add_labels(readme_md)

        # add end of file newline
        readme_md.append('')
        return readme_md
