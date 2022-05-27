#!/usr/bin/env python
"""TcEx Framework Package Module."""
# standard library
import fnmatch
import json
import os
import shutil
from pathlib import Path
from typing import List, Optional

# third-party
import colorama as c

# first-party
from tcex.app_config.install_json import InstallJson
from tcex.backports import cached_property
from tcex.bin.bin_abc import BinABC


class Package(BinABC):
    """Package ThreatConnect Job or Playbook App for deployment.

    This method will package the app for deployment to ThreatConnect. Validation of the
    install.json file or files will be automatically run before packaging the app.
    """

    def __init__(self, excludes: Optional[List[str]], ignore_validation: bool, output_dir: Path):
        """Initialize Class properties."""
        super().__init__()
        self._excludes = excludes or []
        self.ignore_validation = ignore_validation
        self.output_dir = output_dir

        # properties
        self.features = ['aotExecutionEnabled', 'secureParams']
        self.package_data = {'errors': [], 'updates': [], 'package': []}
        self.validation_data = {}

    @cached_property
    def _build_excludes_glob(self):  # pylint: disable=no-self-use
        """Return a list of files and folders that should be excluded during the build process."""
        # glob files/directories
        return [
            '__pycache__',
            '.pytest_cache',  # pytest cache directory
            '*.iml',  # PyCharm files
            '*.pyc',  # any pyc file
            '*.zip',  # any zip file
        ]

    @cached_property
    def _build_excludes_base(self):
        """Return a list of files/folders that should be excluded in the App base directory."""
        # base directory files/directories
        excludes = [
            self.output_dir,
            '.cache',  # local cache directory
            '.c9',  # C9 IDE
            '.coverage',  # coverage file
            '.coveragerc',  # coverage configuration file file
            '.git',  # git directory
            '.gitlab-ci.yml',  # gitlab ci file
            '.gitmodules',  # git modules
            '.history',  # vscode history plugin
            '.idea',  # PyCharm
            '.python-version',  # pyenv
            '.template_manifest.json',  # template manifest file
            '.vscode',  # Visual Studio Code
            'app.yaml',  # requirements builder configuration file
            'artifacts',  # pytest in CI/CD
            'assets',  # pytest in BB Pipelines
            'local-*',  # log directory
            'log',  # log directory
            'JIRA.html',  # documentation file
            'JIRA.md',  # documentation file
            'README.html',  # documentation file
            'test-reports',  # pytest in CI/CD
            'tests',  # pytest test directory
        ]
        # excludes.extend(self._build_excludes_base)
        excludes.extend(self._excludes)
        excludes.extend(self.tj.model.package.excludes)
        return excludes

    def exclude_files(self, src: str, names: list):
        """Ignore exclude files in shutil.copytree (callback)."""
        exclude_list = self._build_excludes_glob
        if src == os.getcwd():
            # get excludes that are specific to the Apps base directory
            exclude_list = self._build_excludes_base

        excluded_files = []
        for n in names:
            for e in exclude_list:
                if fnmatch.fnmatch(n, e):
                    excluded_files.append(n)
        return excluded_files

    @cached_property
    def build_fqpn(self) -> 'Path':
        """Return the fully qualified path name of the build directory."""
        build_fqpn = Path(os.path.join(self.app_path, self.output_dir.name, 'build'))
        build_fqpn.mkdir(exist_ok=True, parents=True)
        return build_fqpn

    @cached_property
    def template_fqpn(self) -> 'Path':
        """Return the fully qualified path name of the template directory."""
        template_fqpn = Path(os.path.join(self.build_fqpn, 'template'))
        if os.access(template_fqpn, os.W_OK):
            # cleanup any previous failed builds
            shutil.rmtree(template_fqpn)

        # update package data
        self.package_data['package'].append(
            {'action': 'Template Directory:', 'output': template_fqpn.name}
        )
        return template_fqpn

    def package(self):
        """Build the App package for deployment to ThreatConnect Exchange."""
        # copy project directory to temp location to use as template for multiple builds
        shutil.copytree(self.app_path, self.template_fqpn, False, ignore=self.exclude_files)

        # update package data
        self.package_data['package'].append(
            {'action': 'App Name:', 'output': self.tj.model.package.app_name}
        )

        # use developer defined app version (deprecated) or package_version from InstallJson model
        app_version = self.tj.model.package.app_version or self.ij.model.package_version

        # update package data
        self.package_data['package'].append({'action': 'App Version:', 'output': f'{app_version}'})

        # !!! The name of the folder in the zip is the *key* for an App. This value must
        # !!! remain consistent for the App to upgrade successfully.
        app_name_version = f'{self.tj.model.package.app_name}_{app_version}'

        # build app directory
        app_path_fqpn = os.path.join(self.build_fqpn, app_name_version)
        if os.access(app_path_fqpn, os.W_OK):
            # cleanup any previous failed builds
            shutil.rmtree(app_path_fqpn)
        shutil.copytree(self.template_fqpn, app_path_fqpn)

        # load template install json
        ij_template = InstallJson(path=app_path_fqpn)

        # automatically update install.json in template directory
        ij_template.update.multiple(sequence=False, valid_values=False, playbook_data_types=False)

        # zip file
        self.zip_file(self.app_path, app_name_version, self.build_fqpn)

        # cleanup build directory
        shutil.rmtree(app_path_fqpn)

    def print_json(self):
        """[App Builder] Print JSON output containing results of the package command."""
        print(
            json.dumps({'package_data': self.package_data, 'validation_data': self.validation_data})
        )

    def print_results(self):
        """Print results of the package command."""
        # Updates
        if self.package_data.get('updates'):
            print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Updates:')
            for p in self.package_data['updates']:
                print(
                    f"{p.get('action')!s:<20}{c.Style.BRIGHT}{c.Fore.CYAN} {p.get('output')!s:<50}"
                )

        # Packaging
        print(f'\n{c.Style.BRIGHT}{c.Fore.BLUE}Package:')
        for p in self.package_data['package']:
            if isinstance(p.get('output'), list):
                n = 5
                list_data = p.get('output')
                print(
                    f"{p.get('action'):<20}{c.Style.BRIGHT}{c.Fore.CYAN} "
                    f"{', '.join(p.get('output')[:n]):<50}"
                )
                del list_data[:n]
                for data in [
                    list_data[i : i + n] for i in range(0, len(list_data), n)  # noqa: E203
                ]:
                    print(f'''{''!s:<20}{c.Style.BRIGHT}{c.Fore.CYAN} {', '.join(data)!s:<50}''')

            else:
                print(
                    f'''{p.get('action')!s:<20}{c.Style.BRIGHT}'''
                    f'''{c.Fore.CYAN} {p.get('output')!s:<50}'''
                )

        # ignore exit code
        if not self.ignore_validation:
            print('\n')  # separate errors from normal output
            # print all errors
            for error in self.package_data.get('errors'):
                print(f'{c.Fore.RED}{error}')
                self.exit_code = 1

    def zip_file(self, app_path: Path, app_name: Path, tmp_path: Path):
        """Zip the App with tcex extension.

        Args:
            app_path: The path of the current project.
            app_name: The name of the App.
            tmp_path: The temp output path for the zip.
        """
        # zip build directory
        zip_fqpn = Path(os.path.join(app_path, self.output_dir, app_name))

        # create App package
        shutil.make_archive(zip_fqpn, format='zip', root_dir=tmp_path, base_dir=app_name)

        # rename the app swapping .zip for .tcx, some filename have "v1.0" which causes
        # the extra dot to be treated as an extension in pathlib.
        zip_fqfn = os.path.join(app_path, self.output_dir, f'{app_name}.zip')
        tcx_fqfn = os.path.join(app_path, self.output_dir, f'{app_name}.tcx')
        shutil.move(zip_fqfn, tcx_fqfn)

        # update package data
        self.package_data['package'].append({'action': 'App Package:', 'output': tcx_fqfn})
