"""TestInstallJsonModel for TcEx App Config InstallJson Model Module Testing.

This module contains comprehensive test cases for the TcEx App Config InstallJson Model Module,
specifically testing InstallJson configuration functionality including model validation,
file parsing, singleton management, and proper configuration behavior across different
JSON file formats and validation scenarios for TcEx application installation configuration.

Classes:
    TestInstallJsonModel: Test class for TcEx App Config InstallJson Model Module functionality

TcEx Module Tested: app.config.install_json
"""


import json
import os
import shutil
from pathlib import Path

import pytest


from _pytest.monkeypatch import MonkeyPatch
from deepdiff import DeepDiff


from tcex.app.config.install_json import InstallJson


class TestInstallJsonModel:
    """TestInstallJsonModel for TcEx App Config InstallJson Model Module Testing.

    This class provides comprehensive testing for the TcEx App Config InstallJson Model Module,
    covering various InstallJson configuration scenarios including model validation,
    file parsing, singleton management, and proper configuration behavior for
    TcEx application installation configuration management.
    """

    def setup_method(self) -> None:
        """Configure setup before all tests.

        This method is called before each test method to initialize
        test environment and prepare for InstallJson model testing.
        """
        # Setup method for future use if needed

    @property
    def tcex_test_dir(self) -> Path:
        """Return tcex test directory.

        This property provides access to the test directory path for InstallJson
        configuration testing, ensuring proper test file location management.
        """
        tcex_test_dir = os.getenv('TCEX_TEST_DIR')
        if tcex_test_dir is None:
            pytest.fail('TCEX_TEST_DIR environment variable not set.')
        return Path(tcex_test_dir)

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     fqfn = Path('tests/app/config/install_json_samples/tcpb/tcpb-example1-install.json')
    #     try:
    #         ij = InstallJson(filename=fqfn.name, path=fqfn.parent)
    #     except Exception as ex:
    #         assert False, f'Failed parsing file {fqfn.name} ({ex})'

    #     print('\nfilename', filename)
    #     print('commit_hash', ij.model.commit_hash)
    #     print('runtime_level', ij.model.runtime_level)

    #     print('data.cache_info', InstallJson.model.fget.cache_info())
    #     print('ij.update', ij.update())
    #     print('data.cache_info', InstallJson.model.fget.cache_info())
    #     print('ij.model.features', ij.model.features)
    #     print('ij.model.display_name', ij.model.display_name)

    def ij(self, app_name: str = 'app_1', app_type: str = 'tcpb') -> InstallJson:
        """Return install.json instance.

        This method creates and returns an InstallJson instance for testing
        configuration scenarios with proper file path management.

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

    def ij_bad(self, app_name: str = 'app_bad_install_json', app_type: str = 'tcpb') -> InstallJson:
        """Return install.json instance with "bad" file.

        This method creates an InstallJson instance with intentionally malformed
        configuration for testing error handling and validation scenarios.

        Parameters:
            app_name: The name of the bad application to test
            app_type: The type of application (e.g., tcpb, tcva)

        Returns:
            InstallJson: Configured InstallJson instance with bad configuration
        """
        # reset singleton
        # InstallJson._instances = {}

        base_fqpn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name
        src = base_fqpn / 'install-template.json'
        dst = base_fqpn / 'install.json'
        shutil.copy2(src, dst)
        fqfn = base_fqpn / 'install.json'
        try:
            return InstallJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

    def model_validate(self, path: str) -> None:
        """Validate input model in and out.

        This method validates InstallJson model configurations by comparing
        input JSON with parsed model output, ensuring proper model
        serialization and deserialization.

        Parameters:
            path: The path to validate InstallJson model configurations
        """
        ij_path = self.tcex_test_dir / path
        for fqfn_path in sorted(ij_path.glob('**/*install.json')):
            # reset singleton
            # InstallJson._instances = {}

            fqfn = Path(fqfn_path)
            with fqfn.open() as fh:
                json_dict = json.load(fh)

            try:
                ij = InstallJson(filename=fqfn.name, path=fqfn.parent)
                # ij.update.multiple()
            except Exception as ex:
                pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

            # Ensure both dictionaries are sorted consistently for comparison
            model_dict = json.loads(
                ij.model.model_dump_json(by_alias=True, exclude_defaults=True, exclude_none=True)
            )
            json_dict_sorted = json.loads(json.dumps(json_dict, sort_keys=True))
            model_dict_sorted = json.loads(json.dumps(model_dict, sort_keys=True))

            ddiff = DeepDiff(
                json_dict_sorted,
                model_dict_sorted,
                ignore_order=True,
                exclude_paths="root['sdkVersion']",
            )
            assert not ddiff, f'Failed validation of file {fqfn.name}'

    def test_app_prefix(self):
        """Test method"""
        assert self.ij(app_type='tc').app_prefix == 'TC_-_'
        assert self.ij(app_type='tcpb').app_prefix == 'TCPB_-_'
        assert self.ij(app_type='tcva').app_prefix == 'TCVA_-_'
        assert self.ij(app_type='tcvf').app_prefix == 'TCVF_-_'
        assert self.ij(app_type='tcvc').app_prefix == 'TCVC_-_'
        assert self.ij(app_type='tcvw').app_prefix == 'TCVW_-_'

    def test_create_output_variables(self):
        """Test method"""
        output_variables = self.ij(app_type='tcpb').create_output_variables(
            self.ij(app_type='tcpb').model.playbook.output_variables  # type: ignore
        )
        assert '#App:9876:action_1.binary.output1!Binary' in output_variables

    def test_expand_valid_values(self):
        """Test method"""
        ij = self.ij(app_type='tcpb')

        # test GROUP_TYPES
        valid_values = ij.expand_valid_values(['${GROUP_TYPES}'])
        assert valid_values == [
            'Adversary',
            'Attack Pattern',
            'Campaign',
            'Course of Action',
            'Document',
            'Email',
            'Event',
            'Incident',
            'Intrusion Set',
            'Malware',
            'Signature',
            'Tactic',
            'Task',
            'Tool',
            'Threat',
            'Vulnerability',
        ]

        # test OWNERS
        valid_values = ij.expand_valid_values(['${OWNERS}'])
        assert not valid_values

        # test USERS
        valid_values = ij.expand_valid_values(['${USERS}'])
        assert not valid_values

    # def test_params_to_args(self):
    #     """Test method"""
    #     ij = self.ij(app_type='tcpb')

    #     # bool
    #     name = 'boolean_input_required'
    #     args = ij.params_to_args(name=name)
    #     assert args.get(name) is True

    #     # choice
    #     name = 'tc_action'
    #     args = ij.params_to_args(name=name)
    #     assert args.get(name) == 'Action 1'

    #     # key-value-list
    #     name = 'key_value_list_required'
    #     args = ij.params_to_args(name=name)
    #     assert args.get(name) == '<KeyValueArray>'

    #     # multi-choice
    #     name = 'multi_choice_required'
    #     args = ij.params_to_args(name=name)
    #     assert args.get(name) == ['Option 1', 'Option 2', 'Option 3']

    #     # else
    #     name = 'string_required'
    #     args = ij.params_to_args(name=name)
    #     assert args.get(name) == (
    #         '<Binary|BinaryArray|KeyValue|KeyValueArray|String|'
    #         'StringArray|TCEntity|TCEntityArray|TCEnhancedEntityArray>'
    #     )

    def test_tc_playbook_out_variables(self) -> None:
        """Test TC Playbook Out Variables for TcEx App Config InstallJson Model Module.

        This test case verifies that the InstallJson model correctly provides
        playbook output variables for various data types and actions,
        ensuring proper variable naming and type specification for
        playbook application outputs.

        This test validates the playbook output variable generation
        and formatting capabilities of the InstallJson configuration.
        """
        data = self.ij(app_type='tcpb').tc_playbook_out_variables
        assert data == [
            '#App:9876:action_1.binary.output1!Binary',
            '#App:9876:action_1.binary.output2!Binary',
            '#App:9876:action_1.binary.output3!Binary',
            '#App:9876:action_1.binary_array.output1!BinaryArray',
            '#App:9876:action_1.binary_array.output2!BinaryArray',
            '#App:9876:action_1.binary_array.output3!BinaryArray',
            '#App:9876:action_1.key_value.output1!KeyValue',
            '#App:9876:action_1.key_value.output2!KeyValue',
            '#App:9876:action_1.key_value.output3!KeyValue',
            '#App:9876:action_1.key_value_array.output1!KeyValueArray',
            '#App:9876:action_1.key_value_array.output2!KeyValueArray',
            '#App:9876:action_1.key_value_array.output3!KeyValueArray',
            '#App:9876:action_1.string.output1!String',
            '#App:9876:action_1.string.output2!String',
            '#App:9876:action_1.string.output3!String',
            '#App:9876:action_1.string_array.output1!StringArray',
            '#App:9876:action_1.string_array.output2!StringArray',
            '#App:9876:action_1.string_array.output3!StringArray',
            '#App:9876:action_1.tcentity.output1!TCEntity',
            '#App:9876:action_1.tcentity.output2!TCEntity',
            '#App:9876:action_1.tcentity.output3!TCEntity',
            '#App:9876:action_1.tcentity_array.output1!TCEntityArray',
            '#App:9876:action_1.tcentity_array.output2!TCEntityArray',
            '#App:9876:action_1.tcentity_array.output3!TCEntityArray',
            '#App:9876:action_2.binary.output1!Binary',
            '#App:9876:action_2.binary.output2!Binary',
            '#App:9876:action_2.binary.output3!Binary',
            '#App:9876:action_2.binary_array.output1!BinaryArray',
            '#App:9876:action_2.binary_array.output2!BinaryArray',
            '#App:9876:action_2.binary_array.output3!BinaryArray',
            '#App:9876:action_2.key_value.output1!KeyValue',
            '#App:9876:action_2.key_value.output2!KeyValue',
            '#App:9876:action_2.key_value.output3!KeyValue',
            '#App:9876:action_2.key_value_array.output1!KeyValueArray',
            '#App:9876:action_2.key_value_array.output2!KeyValueArray',
            '#App:9876:action_2.key_value_array.output3!KeyValueArray',
            '#App:9876:action_2.string.output1!String',
            '#App:9876:action_2.string.output2!String',
            '#App:9876:action_2.string.output3!String',
            '#App:9876:action_2.string_array.output1!StringArray',
            '#App:9876:action_2.string_array.output2!StringArray',
            '#App:9876:action_2.string_array.output3!StringArray',
            '#App:9876:action_2.tcentity.output1!TCEntity',
            '#App:9876:action_2.tcentity.output2!TCEntity',
            '#App:9876:action_2.tcentity.output3!TCEntity',
            '#App:9876:action_2.tcentity_array.output1!TCEntityArray',
            '#App:9876:action_2.tcentity_array.output2!TCEntityArray',
            '#App:9876:action_2.tcentity_array.output3!TCEntityArray',
            '#App:9876:action_3.binary.output1!Binary',
            '#App:9876:action_3.binary.output2!Binary',
            '#App:9876:action_3.binary.output3!Binary',
            '#App:9876:action_3.binary_array.output1!BinaryArray',
            '#App:9876:action_3.binary_array.output2!BinaryArray',
            '#App:9876:action_3.binary_array.output3!BinaryArray',
            '#App:9876:action_3.key_value.output1!KeyValue',
            '#App:9876:action_3.key_value.output2!KeyValue',
            '#App:9876:action_3.key_value.output3!KeyValue',
            '#App:9876:action_3.key_value_array.output1!KeyValueArray',
            '#App:9876:action_3.key_value_array.output2!KeyValueArray',
            '#App:9876:action_3.key_value_array.output3!KeyValueArray',
            '#App:9876:action_3.string.output1!String',
            '#App:9876:action_3.string.output2!String',
            '#App:9876:action_3.string.output3!String',
            '#App:9876:action_3.string_array.output1!StringArray',
            '#App:9876:action_3.string_array.output2!StringArray',
            '#App:9876:action_3.string_array.output3!StringArray',
            '#App:9876:action_3.tcentity.output1!TCEntity',
            '#App:9876:action_3.tcentity.output2!TCEntity',
            '#App:9876:action_3.tcentity.output3!TCEntity',
            '#App:9876:action_3.tcentity_array.output1!TCEntityArray',
            '#App:9876:action_3.tcentity_array.output2!TCEntityArray',
            '#App:9876:action_3.tcentity_array.output3!TCEntityArray',
            '#App:9876:action_all.binary.output1!Binary',
            '#App:9876:action_all.binary.output2!Binary',
            '#App:9876:action_all.binary.output3!Binary',
            '#App:9876:action_all.binary_array.output1!BinaryArray',
            '#App:9876:action_all.binary_array.output2!BinaryArray',
            '#App:9876:action_all.binary_array.output3!BinaryArray',
            '#App:9876:action_all.key_value.output1!KeyValue',
            '#App:9876:action_all.key_value.output2!KeyValue',
            '#App:9876:action_all.key_value.output3!KeyValue',
            '#App:9876:action_all.key_value_array.output1!KeyValueArray',
            '#App:9876:action_all.key_value_array.output2!KeyValueArray',
            '#App:9876:action_all.key_value_array.output3!KeyValueArray',
            '#App:9876:action_all.string.output1!String',
            '#App:9876:action_all.string.output2!String',
            '#App:9876:action_all.string.output3!String',
            '#App:9876:action_all.string_array.output1!StringArray',
            '#App:9876:action_all.string_array.output2!StringArray',
            '#App:9876:action_all.string_array.output3!StringArray',
            '#App:9876:action_all.tcentity.output1!TCEntity',
            '#App:9876:action_all.tcentity.output2!TCEntity',
            '#App:9876:action_all.tcentity.output3!TCEntity',
            '#App:9876:action_all.tcentity_array.output1!TCEntityArray',
            '#App:9876:action_all.tcentity_array.output2!TCEntityArray',
            '#App:9876:action_all.tcentity_array.output3!TCEntityArray',
        ]

    def test_tc_playbook_out_variables_csv(self) -> None:
        """Test TC Playbook Out Variables CSV for TcEx App Config InstallJson Model Module.

        This test case verifies that the InstallJson model correctly provides
        playbook output variables in CSV format for various data types and actions,
        ensuring proper variable formatting and comma-separated value generation
        for playbook application outputs.

        This test validates the CSV output variable generation
        and formatting capabilities of the InstallJson configuration.
        """
        data = self.ij(app_type='tcpb').tc_playbook_out_variables_csv
        assert data == (
            '#App:9876:action_1.binary.output1!Binary,#App:9876:action_1.binary.output2!Binary,#App'
            ':9876:action_1.binary.output3!Binary,#App:9876:action_1.binary_array.output1!BinaryArr'
            'ay,#App:9876:action_1.binary_array.output2!BinaryArray,#App:9876:action_1.binary_array'
            '.output3!BinaryArray,#App:9876:action_1.key_value.output1!KeyValue,#App:9876:action_1.'
            'key_value.output2!KeyValue,#App:9876:action_1.key_value.output3!KeyValue,#App:9876:act'
            'ion_1.key_value_array.output1!KeyValueArray,#App:9876:action_1.key_value_array.output2'
            '!KeyValueArray,#App:9876:action_1.key_value_array.output3!KeyValueArray,#App:9876:acti'
            'on_1.string.output1!String,#App:9876:action_1.string.output2!String,#App:9876:action_1'
            '.string.output3!String,#App:9876:action_1.string_array.output1!StringArray,#App:9876:a'
            'ction_1.string_array.output2!StringArray,#App:9876:action_1.string_array.output3!Strin'
            'gArray,#App:9876:action_1.tcentity.output1!TCEntity,#App:9876:action_1.tcentity.output'
            '2!TCEntity,#App:9876:action_1.tcentity.output3!TCEntity,#App:9876:action_1.tcentity_ar'
            'ray.output1!TCEntityArray,#App:9876:action_1.tcentity_array.output2!TCEntityArray,#App'
            ':9876:action_1.tcentity_array.output3!TCEntityArray,#App:9876:action_2.binary.output1!'
            'Binary,#App:9876:action_2.binary.output2!Binary,#App:9876:action_2.binary.output3!Bina'
            'ry,#App:9876:action_2.binary_array.output1!BinaryArray,#App:9876:action_2.binary_array'
            '.output2!BinaryArray,#App:9876:action_2.binary_array.output3!BinaryArray,#App:9876:act'
            'ion_2.key_value.output1!KeyValue,#App:9876:action_2.key_value.output2!KeyValue,#App:98'
            '76:action_2.key_value.output3!KeyValue,#App:9876:action_2.key_value_array.output1!KeyV'
            'alueArray,#App:9876:action_2.key_value_array.output2!KeyValueArray,#App:9876:action_2.'
            'key_value_array.output3!KeyValueArray,#App:9876:action_2.string.output1!String,#App:98'
            '76:action_2.string.output2!String,#App:9876:action_2.string.output3!String,#App:9876:a'
            'ction_2.string_array.output1!StringArray,#App:9876:action_2.string_array.output2!Strin'
            'gArray,#App:9876:action_2.string_array.output3!StringArray,#App:9876:action_2.tcentity'
            '.output1!TCEntity,#App:9876:action_2.tcentity.output2!TCEntity,#App:9876:action_2.tcen'
            'tity.output3!TCEntity,#App:9876:action_2.tcentity_array.output1!TCEntityArray,#App:987'
            '6:action_2.tcentity_array.output2!TCEntityArray,#App:9876:action_2.tcentity_array.outp'
            'ut3!TCEntityArray,#App:9876:action_3.binary.output1!Binary,#App:9876:action_3.binary.o'
            'utput2!Binary,#App:9876:action_3.binary.output3!Binary,#App:9876:action_3.binary_array'
            '.output1!BinaryArray,#App:9876:action_3.binary_array.output2!BinaryArray,#App:9876:act'
            'ion_3.binary_array.output3!BinaryArray,#App:9876:action_3.key_value.output1!KeyValue,#'
            'App:9876:action_3.key_value.output2!KeyValue,#App:9876:action_3.key_value.output3!KeyV'
            'alue,#App:9876:action_3.key_value_array.output1!KeyValueArray,#App:9876:action_3.key_v'
            'alue_array.output2!KeyValueArray,#App:9876:action_3.key_value_array.output3!KeyValueAr'
            'ray,#App:9876:action_3.string.output1!String,#App:9876:action_3.string.output2!String,'
            '#App:9876:action_3.string.output3!String,#App:9876:action_3.string_array.output1!Strin'
            'gArray,#App:9876:action_3.string_array.output2!StringArray,#App:9876:action_3.string_a'
            'rray.output3!StringArray,#App:9876:action_3.tcentity.output1!TCEntity,#App:9876:action'
            '_3.tcentity.output2!TCEntity,#App:9876:action_3.tcentity.output3!TCEntity,#App:9876:ac'
            'tion_3.tcentity_array.output1!TCEntityArray,#App:9876:action_3.tcentity_array.output2!'
            'TCEntityArray,#App:9876:action_3.tcentity_array.output3!TCEntityArray,#App:9876:action'
            '_all.binary.output1!Binary,#App:9876:action_all.binary.output2!Binary,#App:9876:action'
            '_all.binary.output3!Binary,#App:9876:action_all.binary_array.output1!BinaryArray,#App:'
            '9876:action_all.binary_array.output2!BinaryArray,#App:9876:action_all.binary_array.out'
            'put3!BinaryArray,#App:9876:action_all.key_value.output1!KeyValue,#App:9876:action_all.'
            'key_value.output2!KeyValue,#App:9876:action_all.key_value.output3!KeyValue,#App:9876:a'
            'ction_all.key_value_array.output1!KeyValueArray,#App:9876:action_all.key_value_array.o'
            'utput2!KeyValueArray,#App:9876:action_all.key_value_array.output3!KeyValueArray,#App:9'
            '876:action_all.string.output1!String,#App:9876:action_all.string.output2!String,#App:9'
            '876:action_all.string.output3!String,#App:9876:action_all.string_array.output1!StringA'
            'rray,#App:9876:action_all.string_array.output2!StringArray,#App:9876:action_all.string'
            '_array.output3!StringArray,#App:9876:action_all.tcentity.output1!TCEntity,#App:9876:ac'
            'tion_all.tcentity.output2!TCEntity,#App:9876:action_all.tcentity.output3!TCEntity,#App'
            ':9876:action_all.tcentity_array.output1!TCEntityArray,#App:9876:action_all.tcentity_ar'
            'ray.output2!TCEntityArray,#App:9876:action_all.tcentity_array.output3!TCEntityArray'
        )

    def test_has_feature(self) -> None:
        """Test Has Feature for TcEx App Config InstallJson Model Module.

        This test case verifies that the InstallJson model correctly
        identifies and reports feature availability, ensuring proper
        feature detection and configuration management.

        This test validates the feature detection capabilities
        of the InstallJson configuration system.
        """
        assert self.ij(app_type='tcpb').has_feature('fileParams')

    def test_update(self) -> None:
        """Test Update for TcEx App Config InstallJson Model Module.

        This test case verifies that the InstallJson model update
        functionality works correctly across different application types,
        ensuring proper configuration updates and file management.

        This test validates the update capabilities and file handling
        of the InstallJson configuration system.
        """
        for app_type in ['tc', 'tcpb', 'tcva']:
            ij = self.ij_bad(app_type=app_type)
            try:
                ij.update.multiple()
                assert True
            except Exception as ex:
                pytest.fail(f'Failed to update install.json file ({ex}).')
            finally:
                # cleanup temp file
                ij.fqfn.unlink()

    def test_validate(self) -> None:
        """Test Validate for TcEx App Config InstallJson Model Module.

        This test case verifies that the InstallJson model validation
        functionality works correctly by testing duplicate detection
        and validation error reporting.

        This test validates the validation capabilities and error
        detection of the InstallJson configuration system.
        """
        ij = self.ij_bad(app_type='tcpb')
        try:
            assert ij.validate.validate_duplicate_input() == ['boolean_optional']
            assert ij.validate.validate_duplicate_output() == ['binary']
            assert ij.validate.validate_duplicate_sequence() == [12]
        except Exception as ex:
            pytest.fail(f'Failed to validate install.json file ({ex}).')
        finally:
            # cleanup temp file
            ij.fqfn.unlink()

    def test_model_app_output_var_typ(self) -> None:
        """Test Model App Output Variable Type for TcEx App Config InstallJson Model Module.

        This test case verifies that the InstallJson model correctly
        identifies and reports application output variable types,
        ensuring proper type classification for different application types.

        This test validates the output variable type detection
        and classification capabilities of the InstallJson model.
        """
        ij = self.ij_bad(app_type='tcpb')
        try:
            assert ij.model.app_output_var_type == 'App'

            # cleanup temp file
            ij.fqfn.unlink()

            ij = self.ij_bad(app_type='tcvc')
            assert ij.model.app_output_var_type == 'Trigger'
        finally:
            # cleanup temp file
            ij.fqfn.unlink()

    def test_model_commit_hash(self, monkeypatch: MonkeyPatch) -> None:
        """Test Model Commit Hash for TcEx App Config InstallJson Model Module.

        This test case verifies that the InstallJson model correctly
        retrieves and reports commit hash information from environment
        variables, ensuring proper version tracking and deployment
        information management.

        Parameters:
            monkeypatch: Pytest fixture for patching environment variables

        This test validates the commit hash retrieval and environment
        variable integration capabilities of the InstallJson model.
        """
        monkeypatch.setenv('CI_COMMIT_SHA', '1234567890123456789012345678901234567890')
        ij = self.ij_bad(app_type='tcpb')

        try:
            assert ij.model.commit_hash == os.getenv('CI_COMMIT_SHA')
        finally:
            # cleanup temp file
            ij.fqfn.unlink()

    def test_model_filter_params(self) -> None:
        """Test Model Filter Params for TcEx App Config InstallJson Model Module.

        This test case verifies that the InstallJson model correctly
        provides filtered parameter information, ensuring proper
        parameter management and filtering capabilities.

        This test validates the parameter filtering and management
        capabilities of the InstallJson model.
        """
        ij = self.ij(app_type='tcvc')

        assert ij.model.filter_params(name='service_string_required')
        assert ij.model.filter_params(hidden=True)
        assert ij.model.filter_params(required=True)
        assert ij.model.filter_params(service_config=True)
        assert ij.model.filter_params(_type='String')

    def test_model_get_param(self):
        """Test method"""
        assert self.ij(app_type='tcpb').model.get_param('tc_action')

    def test_model_optional_params(self):
        """Test method"""
        assert self.ij(app_type='tcpb').model.optional_params

    def test_model_param_names(self):
        """Test method"""
        assert self.ij(app_type='tcpb').model.param_names

    def test_model_playbook_outputs(self):
        """Test method"""
        assert self.ij(app_type='tcpb').model.playbook_outputs

    def test_model_required_params(self):
        """Test method"""
        assert self.ij(app_type='tcpb').model.required_params

    def test_model_service_config_params(self):
        """Test method"""
        assert self.ij(app_type='tcvc').model.service_config_params

    def test_model_service_playbook_params(self):
        """Test method"""
        assert self.ij(app_type='tcvc').model.service_playbook_params

    def test_tc_support(self):
        """Validate install.json files."""
        self.model_validate('app/config/apps/tc')

    def test_tcpb_support(self):
        """Validate install.json files."""
        self.model_validate('app/config/apps/tcpb')

    def test_tcva_support(self):
        """Validate install.json files."""
        self.model_validate('app/config/apps/tcva')

    def test_tcvc_support(self):
        """Validate install.json files."""
        self.model_validate('app/config/apps/tcvc')

    def test_tcvw_support(self):
        """Validate install.json files."""
        self.model_validate('app/config/apps/tcvw')
