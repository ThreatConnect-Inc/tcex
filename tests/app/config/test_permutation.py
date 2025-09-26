"""TestPermutation for TcEx App Config Permutation Module Testing.

This module contains comprehensive test cases for the TcEx App Config Permutation Module,
specifically testing Permutation configuration functionality including input validation,
permutation generation, and proper configuration behavior across different
scenarios for TcEx application permutation testing.

Classes:
    TestPermutation: Test class for TcEx App Config Permutation Module functionality

TcEx Module Tested: app.config.permutation
"""


import os
from pathlib import Path

import pytest


from tcex.app.config.install_json import InstallJson
from tcex.app.config.layout_json import LayoutJson
from tcex.app.config.permutation import Permutation
from tcex.pleb.cached_property import cached_property


class TestPermutation:
    """TestPermutation for TcEx App Config Permutation Module Testing.

    This class provides comprehensive testing for the TcEx App Config Permutation Module,
    covering various permutation scenarios including input validation, permutation
    generation, and proper configuration behavior for TcEx application
    permutation testing and validation.
    """

    @property
    def tcex_test_dir(self) -> Path:
        """Return tcex test directory.

        This property provides access to the test directory path for Permutation
        configuration testing, ensuring proper test file location management.
        """
        tcex_test_dir = os.getenv('TCEX_TEST_DIR')
        if tcex_test_dir is None:
            pytest.fail('TCEX_TEST_DIR environment variable not set.')
        return Path(tcex_test_dir)

    def test_dev_testing(self) -> None:
        """Test Dev Testing for TcEx App Config Permutation Module.

        This test case verifies that the Permutation module properly initializes
        with InstallJson and LayoutJson instances, ensuring proper
        configuration setup for permutation testing scenarios.

        This test validates the basic initialization and configuration
        capabilities of the Permutation module.
        """
        try:
            permutation = Permutation()
            permutation.ij = self.ij('tcpb', 'app_1')
            permutation.lj = self.lj('tcpb', 'app_1')
        except Exception as ex:
            pytest.fail(f'Failed initializing permutation ({ex})')

        # Development testing output for debugging
        # print('\n----------------')
        # print('tj.model.lib_versions', tj.model.lib_versions)
        # print('tj.model.package', tj.model.package)
        # print('tj.model.template', tj.model.template)
        # permutation.permutations()

    def ij(self, app_type: str, app_name: str) -> InstallJson:
        """Return install.json instance.

        This method creates and returns an InstallJson instance for testing
        permutation scenarios with proper file path management.

        Parameters:
            app_type: The type of application (e.g., tcpb, tcva)
            app_name: The name of the application to test

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

    def lj(self, app_type: str, app_name: str) -> LayoutJson:
        """Return layout.json instance.

        This method creates and returns a LayoutJson instance for testing
        permutation scenarios with proper singleton management.

        Parameters:
            app_type: The type of application (e.g., tcpb, tcva)
            app_name: The name of the application to test

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

    @cached_property
    def permutation(self) -> Permutation:
        """Return Permutation instance.

        This cached property provides a configured Permutation instance
        for testing various permutation scenarios and validation.

        Returns:
            Permutation: Configured Permutation instance for testing
        """
        try:
            permutation = Permutation()
            permutation.ij = self.ij('tcpb', 'app_1')
            permutation.lj = self.lj('tcpb', 'app_1')
        except Exception as ex:
            pytest.fail(f'Failed initializing permutation ({ex})')

        return permutation

    def test_input_dict(self) -> None:
        """Test Input Dict for TcEx App Config Permutation Module.

        This test case verifies that the Permutation module correctly
        generates input dictionaries for specific permutation indices,
        ensuring proper input variable mapping and default value handling.

        This test validates the input dictionary generation and
        variable mapping capabilities of the Permutation module.
        """
        # run permutations command
        inputs = self.permutation.input_dict(0)
        assert inputs == {
            'tc_action': 'Action 1',
            'username': None,
            'password': None,
            'boolean_input_required': None,  # this is none because it's not in a display clause
            'choice_required': None,  # this is none because it's not in a display clause
            'key_value_list_required': None,
            'multi_choice_required': None,
            'string_required': None,
            'string_advanced': None,
        }

    def test_input_names(self) -> None:
        """Test Input Names for TcEx App Config Permutation Module.

        This test case verifies that the Permutation module correctly
        provides input names for permutation scenarios, ensuring proper
        input variable identification and naming.

        This test validates the input name generation and
        variable identification capabilities of the Permutation module.
        """
        input_names: list[list] = self.permutation.input_names
        assert isinstance(input_names, list), f'input_names ({type(input_names)}) is not a list'

    def test_input_permutations(self) -> None:
        """Test Input Permutations for TcEx App Config Permutation Module.

        This test case verifies that the Permutation module correctly
        generates input permutations for various scenarios, ensuring proper
        permutation logic and input combination generation.

        This test validates the input permutation generation and
        combination logic capabilities of the Permutation module.
        """
        input_names: list[list] = self.permutation.input_permutations
        assert isinstance(input_names, list), (
            f'input_permutations ({type(input_names)}) is not a list'
        )

    def test_output_permutations(self) -> None:
        """Test Output Permutations for TcEx App Config Permutation Module.

        This test case verifies that the Permutation module correctly
        generates output permutations for various scenarios, ensuring proper
        permutation logic and output combination generation.

        This test validates the output permutation generation and
        combination logic capabilities of the Permutation module.
        """
        input_names: list[list] = self.permutation.output_permutations
        assert isinstance(input_names, list), (
            f'output_permutations ({type(input_names)}) is not a list'
        )

    # TODO: [low] updated this to validate the returned data model
    # def test_outputs_by_inputs(self):
    #     """Test method"""
    #     outputs: List[List[dict]] = self.permutation.outputs_by_inputs({'tc_action': 'Action 1'})
    #     assert isinstance(outputs, list)

    def test_permutations(self) -> None:
        """Test Permutations for TcEx App Config Permutation Module.

        This test case verifies that the Permutation module correctly
        generates permutation files and handles file creation/deletion,
        ensuring proper permutation output and file management.

        This test validates the permutation file generation and
        file management capabilities of the Permutation module.
        """
        # run permutations command
        self.permutation.permutations()

        # default permutations.json file
        fqfn = Path('permutations.json')

        assert fqfn.is_file(), 'No permutation file created.'

        # remove temp file
        fqfn.unlink()

    def test_validate_input_variable(self) -> None:
        """Test Validate Input Variable for TcEx App Config Permutation Module.

        This test case verifies that the Permutation module correctly
        validates input variables against specific input combinations,
        ensuring proper variable validation and input requirement checking.

        This test validates the input variable validation and
        requirement checking capabilities of the Permutation module.
        """
        valid: bool = self.permutation.validate_input_variable(
            input_name='boolean_input_required', inputs={'tc_action': 'Action 1'}
        )
        assert valid is True, f'boolean_input_required validation ({valid}) is not True'

        valid = self.permutation.validate_input_variable(
            input_name='boolean_input_optional', inputs={'tc_action': 'Action 1'}
        )
        assert valid is False, f'boolean_input_optional validation ({valid}) is not False'
