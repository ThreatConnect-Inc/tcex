"""TcEx Generate Configurations CLI Command"""
# standard library
import os

# third-party
import black
import isort
import typer

# first-party
from tcex.bin.bin_abc import BinABC
from tcex.bin.gen_config_app_input import GenConfigAppInput


class GenConfig(BinABC):
    """Generate App Config Files"""

    def __init__(self, force: bool = False) -> None:
        """Initialize class properties."""
        super().__init__()
        self.force = force

    def format_code(self, _code):
        """Return formatted code."""

        # run isort on code
        settings_file = None
        if os.path.isfile('setup.cfg'):
            settings_file = 'setup.cfg'
        try:
            isort_config = isort.Config(settings_file=settings_file)
            _code = isort.code(_code, config=isort_config)
        except Exception as ex:
            self.print_failure(f'Formatting of code failed {ex}.')

        # run black formatter on code
        mode = black.FileMode(line_length=100, string_normalization=False)
        try:
            _code = black.format_file_contents(_code, fast=False, mode=mode)
        except black.InvalidInput as ex:
            self.print_failure(f'Formatting of code failed {ex}.')
        except black.NothingChanged:
            pass

        return _code

    def generate_app_input(self) -> None:
        """Generate the app_input.py file."""
        gen = GenConfigAppInput()
        code = gen.generate()
        self.write_app_file(gen.filename, self.format_code('\n'.join(code)))
        if gen.report_mismatch:
            self.print_title('Mismatch Report')
            for entry in gen.report_mismatch:
                self.print_setting('Mismatch', entry, fg_color=typer.colors.YELLOW)

    def generate_install_json(self) -> None:
        """Generate the install.json file."""

    def generate_layout_json(self) -> None:
        """Generate the layout.json file."""

    def write_app_file(self, file_name: str, contents: str):
        """Write contents to file."""
        if os.path.isfile(file_name) and self.force is False:
            prompt = self.prompt_choice(
                f'The {file_name} file already exists: Overwrite?',
                choices=['yes', 'no'],
                default='no',
                fg_color=typer.colors.YELLOW,
            )
            if prompt == 'no':
                self.print_failure('File already exists. Use --force to overwrite.')

        self.print_setting('Writing file', file_name)
        with open(file_name, 'w') as f:
            f.write(contents)
