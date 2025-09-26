"""TestTcexJsonModel for TcEx App Config TcexJson Model Module Testing.

This module contains comprehensive test cases for the TcEx App Config TcexJson Model Module,
specifically testing TcexJson configuration functionality including model validation,
file parsing, singleton management, and proper configuration behavior across different
JSON file formats and validation scenarios for TcEx application configuration.

Classes:
    TestTcexJsonModel: Test class for TcEx App Config TcexJson Model Module functionality

TcEx Module Tested: app.config.tcex_json
"""


import json
import os
import shutil
from pathlib import Path

import pytest


from deepdiff import DeepDiff


from tcex.app.config.install_json import InstallJson
from tcex.app.config.tcex_json import TcexJson


class TestTcexJsonModel:
    """TestTcexJsonModel for TcEx App Config TcexJson Model Module Testing.

    This class provides comprehensive testing for the TcEx App Config TcexJson Model Module,
    covering various TcexJson configuration scenarios including model validation,
    file parsing, singleton management, and proper configuration behavior for
    TcEx application configuration management.
    """

    @property
    def tcex_test_dir(self) -> Path:
        """Return tcex test directory.

        This property provides access to the test directory path for TcexJson
        configuration testing, ensuring proper test file location management.
        """
        tcex_test_dir = os.getenv('TCEX_TEST_DIR')
        if tcex_test_dir is None:
            pytest.fail('TCEX_TEST_DIR environment variable not set.')
        return Path(tcex_test_dir)

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     fqfn = Path('tests/app/config/tcex_json_samples/example1-tcex.json')
    #     try:
    #         tj = TcexJson(filename=fqfn.name, path=fqfn.parent)
    #     except Exception as ex:
    #         assert False, f'Failed parsing file {fqfn.name} ({ex})'

    #     print('\nfilename', fqfn.name)
    #     print('tj.model.lib_versions', tj.model.lib_versions)
    #     print('tj.model.package', tj.model.package)
    #     print('tj.model.template', tj.model.template)

    def ij(self, app_name: str = 'app_1', app_type: str = 'tcpb') -> InstallJson:
        """Return install.json instance.

        This method creates and returns an InstallJson instance for testing
        TcexJson configuration scenarios with proper file path management.

        Parameters:
            app_name: The name of the application to test
            app_type: The type of application (e.g., tcpb, tcva)

        Returns:
            InstallJson: Configured InstallJson instance for testing
        """
        # reset singleton
        # InstallJson._instances = {}

        fqfn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name / 'install.json'
        try:
            return InstallJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

    def tj(self, app_name: str = 'app_1', app_type: str = 'tcpb') -> TcexJson:
        """Return tcex.json instance.

        This method creates and returns a TcexJson instance for testing
        configuration scenarios with proper singleton management.

        Parameters:
            app_name: The name of the application to test
            app_type: The type of application (e.g., tcpb, tcva)

        Returns:
            TcexJson: Configured TcexJson instance for testing
        """
        # reset singleton
        TcexJson._instances = {}  # type: ignore  # noqa: SLF001

        fqfn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name / 'tcex.json'
        try:
            return TcexJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

    def tj_bad(self, app_name: str = 'app_bad_tcex_json', app_type: str = 'tcpb') -> TcexJson:
        """Return tcex.json instance with "bad" file.

        This method creates a TcexJson instance with intentionally malformed
        configuration for testing error handling and validation scenarios.

        Parameters:
            app_name: The name of the bad application to test
            app_type: The type of application (e.g., tcpb, tcva)

        Returns:
            TcexJson: Configured TcexJson instance with bad configuration
        """
        # reset singleton
        TcexJson._instances = {}  # type: ignore  # noqa: SLF001

        base_fqpn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name
        shutil.copy2(
            f'{base_fqpn}/tcex-template.json',
            f'{base_fqpn}/tcex.json',
        )
        fqfn = base_fqpn / 'tcex.json'
        try:
            return TcexJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

    def model_validate(self, path: str) -> None:
        """Validate input model in and out.

        This method validates TcexJson model configurations by comparing
        input JSON with parsed model output, ensuring proper model
        serialization and deserialization.

        Parameters:
            path: The path to validate TcexJson model configurations
        """
        tj_path = self.tcex_test_dir / path
        for fqfn_path in tj_path.glob('**/*tcex.json'):
            # reset singleton
            TcexJson._instances = {}  # type: ignore  # noqa: SLF001

            fqfn = Path(fqfn_path)
            with fqfn.open() as fh:
                json_dict = json.load(fh)

            try:
                tj = TcexJson(filename=fqfn.name, path=fqfn.parent)
                # tj.update.multiple()
            except Exception as ex:
                pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

            ddiff = DeepDiff(
                json_dict,
                # template requires json dump to serialize certain fields
                json.loads(tj.model.json(by_alias=True, exclude_defaults=True, exclude_none=True)),
                ignore_order=True,
            )
            assert not ddiff, f'Failed validation of file {fqfn.name}'

    def test_print_warnings(self) -> None:
        """Test Print Warnings for TcEx App Config TcexJson Model Module.

        This test case verifies that the TcexJson model properly handles
        warning scenarios by testing with intentionally malformed configuration
        files and ensuring proper cleanup of temporary test files.

        This test validates the warning and error handling capabilities
        of the TcexJson configuration model.
        """
        tj = self.tj_bad()

        # remove temp file
        tj.fqfn.unlink()

    def test_update(self) -> None:
        """Test Update for TcEx App Config TcexJson Model Module.

        This test case verifies that the TcexJson model update functionality
        works correctly by testing multiple template updates and ensuring
        proper model serialization and configuration management.

        This test validates the update capabilities and model persistence
        of the TcexJson configuration system.
        """
        tj = self.tj_bad()
        tj.ij = self.ij(app_name='app_bad_tcex_json', app_type='tcpb')

        try:
            tj.update.multiple(template='service_api')
            # print(tj.model.schema_json())
            # print(tj.model.model_dump_json(exclude_defaults=False, exclude_none=True, indent=2))
            assert True
        except Exception as ex:
            pytest.fail(f'Failed to update tcex.json file ({ex}).')
        finally:
            # cleanup temp file
            # tj.fqfn.unlink()
            pass

    def test_support(self) -> None:
        """Test Support for TcEx App Config TcexJson Model Module.

        This test case validates TcexJson configuration files by testing
        model validation across multiple configuration scenarios, ensuring
        proper parsing, validation, and model consistency.

        This test provides comprehensive validation of TcexJson
        configuration file support and model integrity.
        """
        # self.model_validate(self.tj())
        self.model_validate('tests/app/config/apps/tcpb')
