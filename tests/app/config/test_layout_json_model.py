"""TestLayoutJsonModel for TcEx App Config LayoutJson Model Module Testing.

This module contains comprehensive test cases for the TcEx App Config LayoutJson Model Module,
specifically testing LayoutJson configuration functionality including model validation,
file parsing, singleton management, and proper configuration behavior across different
JSON file formats and validation scenarios for TcEx application layout configuration.

Classes:
    TestLayoutJsonModel: Test class for TcEx App Config LayoutJson Model Module functionality

TcEx Module Tested: app.config.layout_json
"""


import json
import os
import shutil
from pathlib import Path

import pytest


from deepdiff import DeepDiff


from tcex.app.config.install_json import InstallJson
from tcex.app.config.layout_json import LayoutJson
from tcex.app.config.model.layout_json_model import OutputsModel, ParametersModel


class TestLayoutJsonModel:
    """TestLayoutJsonModel for TcEx App Config LayoutJson Model Module Testing.

    This class provides comprehensive testing for the TcEx App Config LayoutJson Model Module,
    covering various LayoutJson configuration scenarios including model validation,
    file parsing, singleton management, and proper configuration behavior for
    TcEx application layout configuration management.
    """

    @property
    def tcex_test_dir(self) -> Path:
        """Return tcex test directory.

        This property provides access to the test directory path for LayoutJson
        configuration testing, ensuring proper test file location management.
        """
        tcex_test_dir = os.getenv('TCEX_TEST_DIR')
        if tcex_test_dir is None:
            pytest.fail('TCEX_TEST_DIR environment variable not set.')
        return Path(tcex_test_dir)

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     fqfn = Path('tests/app/config/layout_json_samples/tcpb/tcpb-example1-layout.json')
    #     try:
    #         lj = LayoutJson(filename=fqfn.name, path=fqfn.parent)
    #     except Exception as ex:
    #         assert False, f'Failed parsing file {fqfn.name} ({ex})'

    #     # ij = InstallJson(
    #     #     filename='tcpb_-_blackberry_optics-install.json',
    #     #     path='tests/app/config/install_json_samples/tcpb',
    #     # )
    #     print('\nfilename', filename)
    #     # lj.create(inputs=ij.model.params, outputs=ij.model.playbook.output_variables)
    #     print('lj.model.inputs', lj.model.inputs)
    #     # print('lj.model.outputs', lj.model.outputs)

    def ij(self, app_name: str = 'app_1', app_type: str = 'tcpb') -> InstallJson:
        """Return install.json instance.

        This method creates and returns an InstallJson instance for testing
        LayoutJson configuration scenarios with proper file path management.

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

    def lj(self, app_name: str = 'app_1', app_type: str = 'tcpb') -> LayoutJson:
        """Return layout.json instance.

        This method creates and returns a LayoutJson instance for testing
        configuration scenarios with proper singleton management.

        Parameters:
            app_name: The name of the application to test
            app_type: The type of application (e.g., tcpb, tcva)

        Returns:
            LayoutJson: Configured LayoutJson instance for testing
        """
        # reset singleton
        LayoutJson._instances = {}  # noqa: SLF001

        fqfn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name / 'layout.json'
        try:
            return LayoutJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

    def lj_bad(self, app_name: str = 'app_bad_layout_json', app_type: str = 'tcpb') -> LayoutJson:
        """Return layout.json instance with "bad" file.

        This method creates a LayoutJson instance with intentionally malformed
        configuration for testing error handling and validation scenarios.

        Parameters:
            app_name: The name of the bad application to test
            app_type: The type of application (e.g., tcpb, tcva)

        Returns:
            LayoutJson: Configured LayoutJson instance with bad configuration
        """
        # reset singleton
        LayoutJson._instances = {}  # noqa: SLF001

        base_fqpn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name
        shutil.copy2(
            base_fqpn / 'layout-template.json',
            base_fqpn / 'layout.json',
        )
        fqfn = base_fqpn / 'layout.json'
        try:
            return LayoutJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

    def model_validate(self, path: str) -> None:
        """Validate input model in and out.

        This method validates LayoutJson model configurations by comparing
        input JSON with parsed model output, ensuring proper model
        serialization and deserialization.

        Parameters:
            path: The path to validate LayoutJson model configurations
        """
        lj_path = self.tcex_test_dir / path
        for fqfn_path in sorted(lj_path.glob('**/*layout.json')):
            # reset singleton
            LayoutJson._instances = {}  # noqa: SLF001

            fqfn = Path(fqfn_path)
            with fqfn.open() as fh:
                json_dict = json.load(fh)

            try:
                lj = LayoutJson(filename=fqfn.name, path=fqfn.parent)
                # lj.update.multiple()
            except Exception as ex:
                pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

            ddiff = DeepDiff(
                json_dict,
                # template requires json dump to serialize certain fields
                json.loads(lj.model.json(by_alias=True, exclude_defaults=True, exclude_none=True)),
                ignore_order=True,
            )
            assert not ddiff, f'Failed validation of file {fqfn.name}'

    def test_create(self):
        """Test method"""
        ij = self.ij(app_type='tcpb')
        lj = self.lj(app_name='app_create_layout', app_type='tcpb')
        lj.create(
            inputs=ij.model.params,
            outputs=ij.model.playbook.output_variables,  # type: ignore
        )
        assert lj.fqfn.is_file()

        # remove temp file
        lj.fqfn.unlink()

    def test_has_layout(self):
        """Test method"""
        assert self.lj().has_layout

    def test_model_get_param(self):
        """Test method"""
        assert isinstance(self.lj().model.get_param('tc_action'), ParametersModel)

    def test_model_get_output(self):
        """Test method"""
        assert isinstance(self.lj().model.get_output('action_1.binary.output1'), OutputsModel)

    def test_model_output_(self):
        """Test method"""
        assert isinstance(self.lj().model.outputs_, dict)

    def test_model_param_names(self):
        """Test method"""
        assert isinstance(self.lj().model.param_names, list)

    def test_update(self):
        """Test method"""
        lj = self.lj_bad()
        try:
            lj.update.multiple()
            assert True
        except Exception as ex:
            pytest.fail(f'Failed to update layout.json file ({ex}).')
        finally:
            # cleanup temp file
            # lj.fqfn.unlink()
            pass

    def test_tcpb_support(self):
        """Validate layout.json files."""
        self.model_validate('tests/app/config/app/tcpb')

    def test_tcvc_support(self):
        """Validate layout.json files."""
        self.model_validate('tests/app/config/app/tcvc')
