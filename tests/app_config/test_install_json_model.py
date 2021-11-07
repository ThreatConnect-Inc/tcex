"""Test InstallJson"""
# pylint: disable=R1710
# standard library
import json
import os
import shutil
from pathlib import Path

# third-party
from deepdiff import DeepDiff

# first-party
from tcex.app_config.install_json import InstallJson


class TestInstallJson:
    """App Config InstallJson testing."""

    def setup_method(self):  # pylint: disable=no-self-use
        """Configure setup before all tests."""
        print('')

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     fqfn = Path('tests/app_config/install_json_samples/tcpb/tcpb-example1-install.json')
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

    @staticmethod
    def ij(app_name: str = 'app_1', app_type: str = 'tcpb'):
        """Return install.json instance."""
        # reset singleton
        InstallJson._instances = {}

        ij_fqfn = os.path.join('tests', 'app_config', 'apps', app_type, app_name, 'install.json')
        fqfn = Path(ij_fqfn)
        try:
            _ij = InstallJson(filename=fqfn.name, path=fqfn.parent)
            return _ij
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def ij_bad(app_name: str = 'app_bad_install_json', app_type: str = 'tcpb'):
        """Return install.json instance with "bad" file."""
        # reset singleton
        InstallJson._instances = {}

        base_fqpn = os.path.join('tests', 'app_config', 'apps', app_type, app_name)
        shutil.copy2(
            os.path.join(base_fqpn, 'install-template.json'),
            os.path.join(base_fqpn, 'install.json'),
        )
        fqfn = Path(os.path.join(base_fqpn, 'install.json'))
        try:
            return InstallJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def model_validate(path: str) -> None:
        """Validate input model in and out."""
        ij_path = Path(path)
        for fqfn in sorted(ij_path.glob('**/*install.json')):
            # reset singleton
            InstallJson._instances = {}

            fqfn = Path(fqfn)
            with fqfn.open() as fh:
                json_dict = json.load(fh)

            try:
                ij = InstallJson(filename=fqfn.name, path=fqfn.parent)
                # ij.update.multiple()
            except Exception as ex:
                assert False, f'Failed parsing file {fqfn.name} ({ex})'

            ddiff = DeepDiff(
                json_dict,
                # template requires json dump to serialize certain fields
                json.loads(ij.model.json(by_alias=True, exclude_defaults=True, exclude_none=True)),
                ignore_order=True,
            )
            assert ddiff == {}, f'Failed validation of file {fqfn}'

    def test_app_prefix(self):
        """Test method"""
        assert self.ij(app_type='tc').app_prefix == 'TC_-_'
        assert self.ij(app_type='tcpb').app_prefix == 'TCPB_-_'
        assert self.ij(app_type='tcva').app_prefix == 'TCVA_-_'
        assert self.ij(app_type='tcvc').app_prefix == 'TCVC_-_'
        assert self.ij(app_type='tcvw').app_prefix == 'TCVW_-_'

    def test_create_output_variables(self):
        """Test method"""
        output_variables = self.ij(app_type='tcpb').create_output_variables(
            self.ij(app_type='tcpb').model.playbook.output_variables
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
        assert valid_values == []

        # test USERS
        valid_values = ij.expand_valid_values(['${USERS}'])
        assert valid_values == []

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

    def test_tc_playbook_out_variables(self):
        """Test method"""
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

    def test_tc_playbook_out_variables_csv(self):
        """Test method"""
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

    def test_has_feature(self):
        """Test method"""
        assert self.ij(app_type='tcpb').has_feature('fileParams')

    def test_update(self):
        """Test method"""
        for app_type in ['tc', 'tcpb', 'tcva']:
            ij = self.ij_bad(app_type=app_type)
            try:
                ij.update.multiple(migrate=True)
                assert True
            except Exception as ex:
                assert False, f'Failed to update install.json file ({ex}).'
            finally:
                # cleanup temp file
                ij.fqfn.unlink()

    def test_validate(self):
        """Test method"""
        ij = self.ij_bad(app_type='tcpb')
        try:
            assert ij.validate.validate_duplicate_input() == ['boolean_optional']
            assert ij.validate.validate_duplicate_output() == ['binary']
            assert ij.validate.validate_duplicate_sequence() == [12]
        except Exception as ex:
            assert False, f'Failed to validate install.json file ({ex}).'
        finally:
            # cleanup temp file
            ij.fqfn.unlink()

    def test_model_app_output_var_typ(self):
        """Test method"""
        ij = self.ij_bad(app_type='tcpb')
        assert ij.model.app_output_var_type == 'App'

        # cleanup temp file
        ij.fqfn.unlink()

        ij = self.ij_bad(app_type='tcvc')
        assert ij.model.app_output_var_type == 'Trigger'

        # cleanup temp file
        ij.fqfn.unlink()

    def test_model_commit_hash(self):
        """Test method"""
        ij = self.ij_bad(app_type='tcpb')

        assert ij.model.commit_hash

        # cleanup temp file
        ij.fqfn.unlink()

    def test_model_filter_params(self):
        """Test method"""
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

    def test_tc_support(self) -> None:
        """Validate install.json files."""
        self.model_validate('tests/app_config/apps/tc')

    def test_tcpb_support(self) -> None:
        """Validate install.json files."""
        self.model_validate('tests/app_config/apps/tcpb')

    def test_tcva_support(self) -> None:
        """Validate install.json files."""
        self.model_validate('tests/app_config/apps/tcva')

    def test_tcvc_support(self) -> None:
        """Validate install.json files."""
        self.model_validate('tests/app_config/apps/tcvc')

    def test_tcvw_support(self) -> None:
        """Validate install.json files."""
        self.model_validate('tests/app_config/apps/tcvw')
