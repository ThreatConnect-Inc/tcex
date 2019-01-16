# -*- coding: utf-8 -*-
""" ThreatConnect Playbook App """

# Import default Playbook Class (Required)
from playbook_app import PlaybookApp
from tcex import IterateOnArg, OnException, OnSuccess, Output


# pylint: disable=R0201
class App(PlaybookApp):
    """Playbook App"""

    def __init__(self, _tcex):
        """Initialize class properties."""
        super(App, self).__init__(_tcex)
        self.output_strings = []

    @IterateOnArg(arg='input_strings')
    @OnException(msg='Failed to run capitalize operation.')
    @OnSuccess(msg='Successfully ran capitalize operation.')
    @Output(attribute='output_strings')
    def capitalize(self, string):
        """Return capitalized string."""
        return string.capitalize()

    @IterateOnArg(arg='input_strings')
    @OnException(msg='Failed to run lowercase operation.')
    @OnSuccess(msg='Successfully ran lowercase operation.')
    @Output(attribute='output_strings')
    def lowercase(self, string):
        """Return string in lowercase."""
        return string.lower()

    @IterateOnArg(arg='input_strings')
    @OnException(msg='Failed to run reverse operation.')
    @OnSuccess(msg='Successfully ran reverse operation.')
    @Output(attribute='output_strings')
    def reverse(self, string=None):
        """Return string reversed."""
        return string[::-1]

    @IterateOnArg(arg='input_strings')
    @OnException(msg='Failed to run strip operation.')
    @OnSuccess(msg='Successfully ran strip operation.')
    @Output(attribute='output_strings')
    def strip(self, string):
        """Return string stripping any whitespaces at beginning and end."""
        return string.strip()

    @IterateOnArg(arg='input_strings')
    @OnException(msg='Failed to run swap case operation.')
    @OnSuccess(msg='Successfully ran swap case operation.')
    @Output(attribute='output_strings')
    def swap_case(self, string):
        """Return string with the case swapped."""
        return string.swapcase()

    @IterateOnArg(arg='input_strings')
    @OnException(msg='Failed to run title case operation.')
    @OnSuccess(msg='Successfully ran title case operation.')
    @Output(attribute='output_strings')
    def title_case(self, string):
        """Return string in title case."""
        return string.title()

    @IterateOnArg(arg='input_strings')
    @OnException(msg='Failed to run uppercase operation.')
    @OnSuccess(msg='Successfully ran uppercase operation.')
    @Output(attribute='output_strings')
    def uppercase(self, string):
        """Return string in uppercase."""
        return string.upper()

    def write_output(self):
        """ Write the Playbook output variables. """
        # output
        self.tcex.log.debug('output_strings: {}'.format(self.output_strings))

        self.tcex.playbook.create_output('string.operation', self.args.tc_action)
        self.tcex.playbook.create_output('string.outputs', self.output_strings)
        if self.output_strings:
            self.tcex.playbook.create_output('string.outputs.0', self.output_strings[0])
        self.tcex.playbook.create_output('string.outputs.count', len(self.output_strings))
