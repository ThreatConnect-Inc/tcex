"""TcEx Generate Configurations CLI Command"""
# standard library
import os
import shutil
import subprocess  # nosec

# third-party
import black
import isort
import typer
from pydantic import ValidationError

# first-party
from tcex.app_config import AppSpecYml
from tcex.bin.bin_abc import BinABC
from tcex.bin.spec_tool_app_input import SpecToolAppInput
from tcex.bin.spec_tool_app_spec_yml import SpecToolAppSpecYml
from tcex.bin.spec_tool_install_json import SpecToolInstallJson
from tcex.bin.spec_tool_job_json import SpecToolJobJson
from tcex.bin.spec_tool_layout_json import SpecToolLayoutJson
from tcex.bin.spec_tool_readme_md import SpecToolReadmeMd
from tcex.bin.spec_tool_tcex_json import SpecToolTcexJson


class SpecTool(BinABC):
    """Generate App Config Files"""

    def __init__(self, overwrite: bool = False):
        """Initialize class properties."""
        super().__init__()
        self.overwrite = overwrite

        # properties
        self.app_spec_filename = 'app_spec.yml'
        self.asy = AppSpecYml()
        self.report_data = {}
        self.summary_data = []

        # rename app.yaml to app_spec.yml
        self.rename_app_file('app.yaml', 'app_spec.yml')

    def _check_has_spec(self):
        """Validate that the app_spec.yml file exists."""
        if not self.asy.has_spec:
            self.print_failure(
                f'No {self.asy.fqfn.name} file found.\nTry running `tcex spectool '
                f'--app-spec` first to generate the {self.asy.fqfn.name} specification file.'
            )

    @property
    def _git_installed(self) -> bool:
        """Check if git is installed."""
        installed = True
        try:
            #  pylint: disable=consider-using-with
            subprocess.Popen('git', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # nosec
        except OSError:
            installed = False

        self.log.debug(f'action=check-git-installed, results={installed}')
        return installed

    def _git_mv_file(self, src_filename: str, dest_filename: str) -> bool:
        """Check if git is installed."""
        moved = True
        try:
            #  pylint: disable=consider-using-with
            cmd = subprocess.Popen(  # nosec
                ['git', 'mv', src_filename, dest_filename],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            _ = cmd.communicate()[0]
            moved = cmd.returncode == 0
        except OSError:
            moved = False

        self.log.debug(
            f'action=mv-file, src-filename={src_filename}, '
            f'dest-filename={dest_filename}, results={moved}'
        )
        return moved

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
            print(_code)
            self.print_failure(f'Formatting of code failed {ex}.')
        except black.NothingChanged:
            pass

        return _code

    def generate_app_input(self):
        """Generate the app_input.py file."""
        # force migration of app.yaml file
        _ = self.asy.model.app_id

        gen = SpecToolAppInput()
        code = gen.generate()
        self.write_app_file(gen.filename, self.format_code('\n'.join(code)))
        if gen.report_mismatch:
            _report = []
            for r in gen.report_mismatch:
                _report.append(
                    {
                        'label': 'Mismatch',
                        'value': r,
                        'fg_color': typer.colors.YELLOW,
                    }
                )
            self.report_data['Mismatch Report'] = _report

    def generate_app_spec(self, schema: bool):
        """Generate the app_spec.yml file."""
        gen = SpecToolAppSpecYml()
        if schema:
            print(gen.generate_schema())
        else:
            try:
                config = gen.generate()
            except ValidationError as ex:
                self.print_failure(f'Failed Generating app_spec.yml:\n{ex}')

            self.write_app_file(gen.filename, f'{config}\n')

    def generate_install_json(self, schema: bool):
        """Generate the install.json file."""
        gen = SpecToolInstallJson(self.asy)
        if schema:
            print(gen.generate_schema())
        else:
            # check that app_spec.yml exists
            self._check_has_spec()

            try:
                ij = gen.generate()
            except ValidationError as ex:
                self.print_failure(f'Failed Generating install.json:\n{ex}')

            # exclude_defaults - if False then all unused fields are added in - not good.
            # exclude_none - this should be safe to leave as True.
            # exclude_unset - this should be safe to leave as True.
            config = ij.json(
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=True,
                indent=2,
                sort_keys=True,
            )
            self.write_app_file(gen.filename, f'{config}\n')

    def generate_layout_json(self, schema: bool):
        """Generate the layout.json file."""
        gen = SpecToolLayoutJson(self.asy)
        if schema:
            print(gen.generate_schema())
        elif self.asy.model.runtime_level.lower() != 'organization':
            # check that app_spec.yml exists
            self._check_has_spec()

            if self.asy.model.requires_layout:
                try:
                    lj = gen.generate()
                except ValidationError as ex:
                    self.print_failure(f'Failed Generating layout.json:\n{ex}')

                # exclude_defaults - if False then all unused fields are added in - not good.
                # exclude_none - this should be safe to leave as True.
                # exclude_unset - this should be safe to leave as True.
                config = lj.json(
                    by_alias=True,
                    exclude_defaults=True,
                    exclude_none=True,
                    exclude_unset=True,
                    indent=2,
                    sort_keys=True,
                )
                self.write_app_file(gen.filename, f'{config}\n')

    def generate_job_json(self, schema: bool):
        """Generate the job.json file."""
        gen = SpecToolJobJson(self.asy)
        if schema:
            print(gen.generate_schema())
        elif self.asy.model.runtime_level.lower() == 'organization':
            # check that app_spec.yml exists
            self._check_has_spec()

            try:
                for filename, job in gen.generate():
                    if job is not None:
                        config = job.json(
                            by_alias=True,
                            exclude_defaults=True,
                            exclude_none=True,
                            exclude_unset=True,
                            indent=2,
                            sort_keys=True,
                        )
                        self.write_app_file(filename, f'{config}\n')
            except ValidationError as ex:
                self.print_failure(f'Failed Generating job.json:\n{ex}')

    def generate_readme_md(self):
        """Generate the README.me file."""
        # check that app_spec.yml exists
        self._check_has_spec()

        gen = SpecToolReadmeMd(self.asy)
        readme_md = gen.generate()
        self.write_app_file(gen.filename, '\n'.join(readme_md))

    def generate_tcex_json(self, schema: bool):
        """Generate the tcex.json file."""
        gen = SpecToolTcexJson(self.asy)
        if schema:
            print(gen.generate_schema())
        else:
            # check that app_spec.yml exists
            self._check_has_spec()

            try:
                tj = gen.generate()
            except ValidationError as ex:
                self.print_failure(f'Failed Generating tcex.json:\n{ex}')

            # exclude_defaults - if False then all unused fields are added in - not good.
            # exclude_none - this should be safe to leave as True.
            # exclude_unset - this should be safe to leave as True.
            config = tj.json(
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=True,
                indent=2,
                sort_keys=True,
            )
            self.write_app_file(gen.filename, f'{config}\n')

    def rename_app_file(self, src_filename: str, dest_filename: str):
        """Rename the app.yaml file to app_spec.yml."""
        if os.path.isfile(src_filename):
            self.log.debug(
                f'action=rename-file, src-filename={src_filename}, dest-filename={dest_filename}'
            )

            moved = False
            if self._git_installed is True:
                # to not loose git history of the file
                moved = self._git_mv_file(src_filename, dest_filename)

            if moved is False:
                shutil.move('app.yaml', 'app_spec.yml')

    def print_report(self):
        """Print report data."""
        for report_name, report_data in self.report_data.items():
            self.print_title(report_name)
            for report in report_data:
                self.print_setting(
                    report.get('label'), report.get('value'), fg_color=report.get('fg_color')
                )

    def print_summary(self):
        """Print action summary."""
        if self.summary_data:
            self.print_title('Summary Data')
            for summary in self.summary_data:
                self.print_setting(
                    summary.get('label'), summary.get('value'), fg_color=summary.get('fg_color')
                )

    def write_app_file(self, file_name: str, contents: str):
        """Write contents to file."""
        action = 'Created'
        write_file = True
        if os.path.isfile(file_name):
            action = 'Updated'
            if self.overwrite is False:
                prompt = self.prompt_choice(
                    f'The {file_name} file already exists: Overwrite?',
                    choices=['yes', 'no'],
                    default='no',
                    fg_color=typer.colors.YELLOW,
                )
                if prompt == 'no':
                    action = 'Skipped'
                    write_file = False

        if write_file is True:
            with open(file_name, 'w') as f:
                f.write(contents)

        self.summary_data.append(
            {
                'fg_color': typer.colors.GREEN,
                'label': f'{action} File',
                'value': file_name,
            }
        )
