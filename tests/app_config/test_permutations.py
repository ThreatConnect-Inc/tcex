"""Test the LayoutJson Config"""
# pylint: disable=R1710
# standard library
import os
from pathlib import Path
from typing import List

# first-party
from tcex.app_config.install_json import InstallJson
from tcex.app_config.layout_json import LayoutJson
from tcex.app_config.permutation import Permutation
from tcex.backports import cached_property


class TestPermutation:
    """App Config Permutations testing."""

    def test_dev_testing(self):
        """."""
        try:
            permutation = Permutation()
            permutation.ij = self.ij('tcpb', 'app_1')
            permutation.lj = self.lj('tcpb', 'app_1')
        except Exception as ex:
            assert False, f'Failed intializing permutation ({ex})'

        print('\n----------------')
        # print('tj.data.lib_versions', tj.data.lib_versions)
        # print('tj.data.package', tj.data.package)
        # print('tj.data.template', tj.data.template)
        # permutation.permutations()

    @staticmethod
    def ij(app_type: str, app_name: str) -> InstallJson:
        """Return install.json instance."""
        base_path = f'tests/app_config/apps/{app_type}/{app_name}'
        fqfn = Path(os.path.join(base_path, 'install.json'))
        try:
            return InstallJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def lj(app_type: str, app_name: str):
        """Return layout.json instance."""
        base_path = f'tests/app_config/apps/{app_type}/{app_name}'
        fqfn = Path(os.path.join(base_path, 'layout.json'))
        try:
            return LayoutJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @cached_property
    def permutation(self) -> Permutation:
        """Return Permutation instance."""
        try:
            permutation = Permutation()
            permutation.ij = self.ij('tcpb', 'app_1')
            permutation.lj = self.lj('tcpb', 'app_1')
        except Exception as ex:
            assert False, f'Failed intializing permutation ({ex})'

        return permutation

    def test_input_dict(self):
        """Test method"""
        # run permutations command
        inputs = self.permutation.input_dict(0)
        assert inputs == {
            'tc_action': 'Action 1',
            'username': None,
            'password': None,
            'boolean_input_required': True,
            'choice_required': 'Option 1',
            'key_value_list_required': None,
            'multi_choice_required': None,
            'string_required': None,
            'string_advanced': None,
        }

    def test_input_names(self):
        """Test method"""
        input_names: List[list] = self.permutation.input_names
        assert isinstance(input_names, list)

    def test_input_permutations(self):
        """Test method"""
        input_names: List[list] = self.permutation.input_permutations
        assert isinstance(input_names, list)

    def test_output_permutations(self):
        """Test method"""
        input_names: List[list] = self.permutation.output_permutations
        assert isinstance(input_names, list)

    def test_outputs_by_inputs(self):
        """Test method"""
        outputs: List[List[dict]] = self.permutation.outputs_by_inputs({'tc_action': 'Action 1'})
        assert isinstance(outputs, list)

    def test_permutations(self):
        """Test method"""
        # run permutations command
        self.permutation.permutations()

        # default permutations.json file
        fqfn = Path('permutations.json')

        assert fqfn.is_file(), 'No permutation file created.'

        # remove temp file
        fqfn.unlink()

    def test_validate_input_variable(self):
        """Test method"""
        valid: bool = self.permutation.validate_input_variable(
            input_name='boolean_input_required', inputs={'tc_action': 'Action 1'}
        )
        assert valid is True

        valid: bool = self.permutation.validate_input_variable(
            input_name='boolean_input_optional', inputs={'tc_action': 'Action 1'}
        )
        assert valid is False
