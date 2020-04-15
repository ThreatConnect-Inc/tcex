# -*- coding: utf-8 -*-
"""ThreatConnect Playbook App"""

# Import default Playbook Class (Required)
from playbook_app import PlaybookApp
from tcex import IterateOnArg, OnException, OnSuccess, Output


# pylint: disable=no-self-use
class App(PlaybookApp):
    """Playbook App"""

    def __init__(self, _tcex):
        """Initialize class properties."""
        super().__init__(_tcex)
        self.output_strings = []

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run capitalize operation.')
    @OnSuccess(exit_msg='Successfully ran capitalize operation.')
    @Output(attribute='output_strings')
    def capitalize(self, input_strings):
        """Return capitalized string."""
        return input_strings.capitalize()

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run lowercase operation.')
    @OnSuccess(exit_msg='Successfully ran lowercase operation.')
    @Output(attribute='output_strings')
    def lowercase(self, input_strings):
        """Return string in lowercase."""
        return input_strings.lower()

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run reverse operation.')
    @OnSuccess(exit_msg='Successfully ran reverse operation.')
    @Output(attribute='output_strings')
    def reverse(self, input_strings):
        """Return string reversed."""
        return input_strings[::-1]

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run strip operation.')
    @OnSuccess(exit_msg='Successfully ran strip operation.')
    @Output(attribute='output_strings')
    def strip(self, input_strings):
        """Return string stripping any whitespaces at beginning and end."""
        return input_strings.strip()

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run swap case operation.')
    @OnSuccess(exit_msg='Successfully ran swap case operation.')
    @Output(attribute='output_strings')
    def swap_case(self, input_strings):
        """Return string with the case swapped."""
        return input_strings.swapcase()

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run title case operation.')
    @OnSuccess(exit_msg='Successfully ran title case operation.')
    @Output(attribute='output_strings')
    def title_case(self, input_strings):
        """Return string in title case."""
        return input_strings.title()

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run uppercase operation.')
    @OnSuccess(exit_msg='Successfully ran uppercase operation.')
    @Output(attribute='output_strings')
    def uppercase(self, input_strings):
        """Return string in uppercase."""
        return input_strings.upper()

    def write_output(self):
        """Write the Playbook output variables."""
        # output
        self.tcex.log.debug(f'output_strings: {self.output_strings}')

        self.tcex.playbook.create_output('string.operation', self.args.tc_action)
        self.tcex.playbook.create_output('string.outputs', self.output_strings)
        if self.output_strings:
            self.tcex.playbook.create_output('string.outputs.0', self.output_strings[0])
        self.tcex.playbook.create_output('string.outputs.count', len(self.output_strings))
