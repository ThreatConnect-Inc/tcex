"""Test the InstallJson Config"""
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


class TestInstallJsonModel:
    """Test the TcEx App Feature Advance Request Module."""

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     fqfn = Path('tests/app_config_model/install_json_samples/tcpb/tcpb-example1-install.json')
    #     try:
    #         ij = InstallJson(filename=fqfn.name, path=fqfn.parent)
    #     except Exception as ex:
    #         assert False, f'Failed parsing file {fqfn.name} ({ex})'

    #     print('\nfilename', filename)
    #     print('commit_hash', ij.data.commit_hash)
    #     print('runtime_level', ij.data.runtime_level)

    #     print('data.cache_info', InstallJson.data.fget.cache_info())
    #     print('ij.update', ij.update())
    #     print('data.cache_info', InstallJson.data.fget.cache_info())
    #     print('ij.data.features', ij.data.features)
    #     print('ij.data.display_name', ij.data.display_name)

    @staticmethod
    def ij(app_type: str):
        """Return install.json instance."""
        base_path = f'tests/app_config_model/install_json_samples/{app_type}'
        fqfn = Path(os.path.join(base_path, f'{app_type}-example1-install.json'))
        try:
            return InstallJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def ij_bad(app_type: str):
        """Return install.json instance with "bad" file."""
        base_path = f'tests/app_config_model/install_json_samples/{app_type}'
        shutil.copy2(
            os.path.join(base_path, f'{app_type}-example1-install-bad-template.json'),
            os.path.join(base_path, f'{app_type}-example1-install-bad.json'),
        )
        fqfn = Path(os.path.join(base_path, f'{app_type}-example1-install-bad.json'))
        try:
            return InstallJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def model_validate(path: str) -> None:
        """Validate input model in and out."""
        ij_path = Path(path)
        for fqfn in sorted(ij_path.glob('**/*install.json')):
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
                ij.data.dict(by_alias=True, exclude_defaults=True, exclude_none=True),
                ignore_order=True,
            )
            assert ddiff == {}, f'Failed validation of file {fqfn.name}'

    def test_app_prefix(self):
        """Test method"""
        assert self.ij('tc').app_prefix == 'TC_-_'
        assert self.ij('tcpb').app_prefix == 'TCPB_-_'
        assert self.ij('tcva').app_prefix == 'TCVA_-_'
        assert self.ij('tcvc').app_prefix == 'TCVC_-_'
        assert self.ij('tcvw').app_prefix == 'TCVW_-_'

    def test_create_output_variables(self):
        """Test method"""
        output_variables = self.ij('tcpb').create_output_variables(
            self.ij('tcpb').data.playbook.output_variables
        )
        assert '#App:9876:binary!binary' in output_variables

    def test_expand_valid_values(self):
        """Test method"""
        ij = self.ij('tcpb')

        # test GROUP_TYPES
        valid_values = ij.expand_valid_values(['${GROUP_TYPES}'])
        assert valid_values == [
            'Adversary',
            'Campaign',
            'Document',
            'Email',
            'Event',
            'Incident',
            'Intrusion Set',
            'Signature',
            'Task',
            'Threat',
        ]

        # test OWNERS
        valid_values = ij.expand_valid_values(['${OWNERS}'])
        assert valid_values == []

        # test USERS
        valid_values = ij.expand_valid_values(['${USERS}'])
        assert valid_values == []

    def test_params_to_args(self):
        """Test method"""
        ij = self.ij('tcpb')

        # bool
        name = 'boolean_required'
        args = ij.params_to_args(name=name)
        assert args.get(name) is True

        # choice
        name = 'tc_action'
        args = ij.params_to_args(name=name)
        assert args.get(name) == 'choice1'

        # key-value-list
        name = 'key_value_list'
        args = ij.params_to_args(name=name)
        assert args.get(name) == '<KeyValueArray>'

        # multi-choice
        name = 'multi_choice_required'
        args = ij.params_to_args(name=name)
        assert args.get(name) == ['choice1', 'choice2', 'choice3']

        # else
        name = 'string_required'
        args = ij.params_to_args(name=name)
        assert args.get(name) == (
            '<Binary|BinaryArray|KeyValue|KeyValueArray|String|'
            'StringArray|TCEntity|TCEntityArray|TCEnhancedEntityArray>'
        )

    def test_tc_playbook_out_variables(self):
        """Test method"""
        data = self.ij('tcpb').tc_playbook_out_variables
        assert data == [
            '#App:9876:binary!binary',
            '#App:9876:binary_array!BinaryArray',
            '#App:9876:key_value!KeyValue',
            '#App:9876:key_value_array!KeyValueArray',
            '#App:9876:string!String',
            '#App:9876:string_array!StringArray',
            '#App:9876:tc_entity!TCEntity',
            '#App:9876:tc_entity_array!TCEnhancedEntity',
            '#App:9876:tc_enhanced_entity_array!TCEnhancedEntityArray',
        ]

    def test_tc_playbook_out_variables_csv(self):
        """Test method"""
        data = self.ij('tcpb').tc_playbook_out_variables_csv
        assert data == (
            '#App:9876:binary!binary,#App:9876:binary_array!BinaryArray,'
            '#App:9876:key_value!KeyValue,#App:9876:key_value_array!KeyValueArray,'
            '#App:9876:string!String,#App:9876:string_array!StringArray,'
            '#App:9876:tc_entity!TCEntity,#App:9876:tc_entity_array!TCEnhancedEntity,'
            '#App:9876:tc_enhanced_entity_array!TCEnhancedEntityArray'
        )

    def test_has_feature(self):
        """Test method"""
        assert self.ij('tcpb').has_feature('fileParams')

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
        ij = self.ij_bad('tcpb')
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
        ij = self.ij_bad('tcpb')
        assert ij.data.app_output_var_type == 'App'

        # cleanup temp file
        ij.fqfn.unlink()

        ij = self.ij_bad('tcvc')
        assert ij.data.app_output_var_type == 'Trigger'

        # cleanup temp file
        ij.fqfn.unlink()

    def test_model_commit_hash(self):
        """Test method"""
        ij = self.ij_bad('tcpb')

        assert ij.data.commit_hash

        # cleanup temp file
        ij.fqfn.unlink()

    def test_model_filter_params(self):
        """Test method"""
        ij = self.ij('tcvc')

        assert ij.data.filter_params(name='service_string_required')
        assert ij.data.filter_params(hidden=True)
        assert ij.data.filter_params(required=True)
        assert ij.data.filter_params(service_config=True)
        assert ij.data.filter_params(_type='String')

    def test_model_get_param(self):
        """Test method"""
        assert self.ij('tcpb').data.get_param('tc_action')

    def test_model_optional_params(self):
        """Test method"""
        assert self.ij('tcpb').data.optional_params

    def test_model_param_names(self):
        """Test method"""
        assert self.ij('tcpb').data.param_names

    def test_model_playbook_outputs(self):
        """Test method"""
        assert self.ij('tcpb').data.playbook_outputs

    def test_model_required_params(self):
        """Test method"""
        assert self.ij('tcpb').data.required_params

    def test_model_service_config_params(self):
        """Test method"""
        assert self.ij('tcvc').data.service_config_params

    def test_model_service_playbook_params(self):
        """Test method"""
        assert self.ij('tcvc').data.service_playbook_params

    def test_tc_support(self) -> None:
        """Validate install.json files."""
        self.model_validate('tests/app_config_model/install_json_samples/tc')

    def test_tcpb_support(self) -> None:
        """Validate install.json files."""
        self.model_validate('tests/app_config_model/install_json_samples/tcpb')

    def test_tcva_support(self) -> None:
        """Validate install.json files."""
        self.model_validate('tests/app_config_model/install_json_samples/tcva')

    def test_tcvc_support(self) -> None:
        """Validate install.json files."""
        self.model_validate('tests/app_config_model/install_json_samples/tcvc')

    def test_tcvw_support(self) -> None:
        """Validate install.json files."""
        self.model_validate('tests/app_config_model/install_json_samples/tcvw')
