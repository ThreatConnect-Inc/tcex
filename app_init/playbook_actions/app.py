"""ThreatConnect Playbook App"""

# third-party
from tcex import IterateOnArg, OnException, OnSuccess, Output

# first-party
from playbook_app import PlaybookApp  # Import default Playbook App Class (Required)


# pylint: disable=no-self-use
class App(PlaybookApp):
    """Playbook App"""

    def __init__(self, _tcex):
        """Initialize class properties."""
        super().__init__(_tcex)
        self.output_strings = []

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run capitalize action.')
    @OnSuccess(exit_msg='Successfully ran capitalize action.')
    @Output(attribute='output_strings')
    def capitalize(self, input_strings) -> str:
        """Return capitalized string."""
        return input_strings.capitalize()

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run lowercase action.')
    @OnSuccess(exit_msg='Successfully ran lowercase action.')
    @Output(attribute='output_strings')
    def lowercase(self, input_strings) -> str:
        """Return string in lowercase."""
        return input_strings.lower()

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run reverse action.')
    @OnSuccess(exit_msg='Successfully ran reverse action.')
    @Output(attribute='output_strings')
    def reverse(self, input_strings) -> str:
        """Return string reversed."""
        return input_strings[::-1]

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run strip action.')
    @OnSuccess(exit_msg='Successfully ran strip action.')
    @Output(attribute='output_strings')
    def strip(self, input_strings) -> str:
        """Return string stripping any whitespaces at beginning and end."""
        return input_strings.strip()

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run swap case action.')
    @OnSuccess(exit_msg='Successfully ran swap case action.')
    @Output(attribute='output_strings')
    def swap_case(self, input_strings) -> str:
        """Return string with the case swapped."""
        return input_strings.swapcase()

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run title case action.')
    @OnSuccess(exit_msg='Successfully ran title case action.')
    @Output(attribute='output_strings')
    def title_case(self, input_strings) -> str:
        """Return string in title case."""
        return input_strings.title()

    @IterateOnArg(arg='input_strings')
    @OnException(exit_msg='Failed to run uppercase action.')
    @OnSuccess(exit_msg='Successfully ran uppercase action.')
    @Output(attribute='output_strings')
    def uppercase(self, input_strings) -> str:
        """Return string in uppercase."""
        return input_strings.upper()

    def write_output(self):
        """Write the Playbook output variables."""
        # output
        self.tcex.log.debug(f'output_strings: {self.output_strings}')

        self.tcex.playbook.create_output('string.action', self.args.tc_action)
        self.tcex.playbook.create_output('string.outputs', self.output_strings)
        if self.output_strings:
            self.tcex.playbook.create_output('string.outputs.0', self.output_strings[0])
        self.tcex.playbook.create_output('string.outputs.count', len(self.output_strings))
