"""TcEx Framework Module"""
# pylint: disable=R1710
# standard library
import os
from pathlib import Path

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.app.config.layout_json import LayoutJson
from tcex.app.config.permutation import Permutation
from tcex.pleb.cached_property import cached_property


class TestPermutation:
    """App Config Permutations testing."""

    @property
    def tcex_test_dir(self) -> Path:
        """Return tcex test directory."""
        tcex_test_dir = os.getenv('TCEX_TEST_DIR')
        if tcex_test_dir is None:
            assert False, 'TCEX_TEST_DIR environment variable not set.'
        return Path(tcex_test_dir)

    def test_dev_testing(self):
        """."""
        try:
            permutation = Permutation()
            permutation.ij = self.ij('tcpb', 'app_1')
            permutation.lj = self.lj('tcpb', 'app_1')
        except Exception as ex:
            assert False, f'Failed initializing permutation ({ex})'

        print('\n----------------')
        # print('tj.model.lib_versions', tj.model.lib_versions)
        # print('tj.model.package', tj.model.package)
        # print('tj.model.template', tj.model.template)
        # permutation.permutations()

    def ij(self, app_type: str, app_name: str) -> InstallJson:
        """Return install.json instance."""
        # reset singleton
        # InstallJson._instances = {}

        fqfn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name / 'install.json'
        try:
            return InstallJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    def lj(self, app_type: str, app_name: str):
        """Return layout.json instance."""
        # reset singleton
        LayoutJson._instances = {}

        fqfn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name / 'layout.json'
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
            assert False, f'Failed initializing permutation ({ex})'

        return permutation

    def test_input_dict(self):
        """Test method"""
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

    def test_input_names(self):
        """Test method"""
        input_names: list[list] = self.permutation.input_names
        assert isinstance(input_names, list)

    def test_input_permutations(self):
        """Test method"""
        input_names: list[list] = self.permutation.input_permutations
        assert isinstance(input_names, list)

    def test_output_permutations(self):
        """Test method"""
        input_names: list[list] = self.permutation.output_permutations
        assert isinstance(input_names, list)

    # TODO: [low] updated this to validate the returned data model
    # def test_outputs_by_inputs(self):
    #     """Test method"""
    #     outputs: List[List[dict]] = self.permutation.outputs_by_inputs({'tc_action': 'Action 1'})
    #     assert isinstance(outputs, list)

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
