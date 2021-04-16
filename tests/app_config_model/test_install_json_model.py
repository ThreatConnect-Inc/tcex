"""Test the InstallJson Config"""
# standard library
import os
from pathlib import Path

# first-party
from tcex.app_config.install_json import InstallJson


class TestInstallJsonModel:
    """Test the TcEx App Feature Advance Request Module."""

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     tcpb_path = Path('tests/app_config_model/install_json_samples/tcpb')
    #     for filename in sorted(tcpb_path.glob('**/*')):
    #         try:
    #             ij = InstallJson(filename=os.path.basename(filename), path=str(tcpb_path))
    #             assert True
    #         except Exception as ex:
    #             assert False, f'Failed parsing file {os.path.basename(filename)} ({ex})'

    #         print('\nfilename', filename)
    #         print('commit_hash', ij.data.commit_hash)
    #         print('runtime_level', ij.data.runtime_level)
    #         print('app-prefix', ij.data.app_prefix)
    #         # for param in ij.data.params:
    #         #     # print('param.playbookDataType', type(param))
    #         #     print('param.playbookDataType', '|'.join(param.playbook_data_type))
    #         print('duplicate-outputs', ij.validate_duplicate_output())
    #         print('duplicate-sequence', ij.validate_duplicate_sequence())

    #         # print('required-params', ij.data.required_params)
    #         # print('dict', ij.data.dict(by_alias=True))

    #         print('ij.data.features', ij.data.features)
    #         print('data.cache_info', InstallJson.data.fget.cache_info())
    #         print('ij.update', ij.update())
    #         print('data.cache_info', InstallJson.data.fget.cache_info())
    #         print('ij.data.features', ij.data.features)
    #         print('ij.data.display_name', ij.data.display_name)

    #         break

    @staticmethod
    def test_tc_support():
        """."""
        tcpb_path = Path('tests/app_config_model/install_json_samples/tc')
        for filename in sorted(tcpb_path.glob('**/*')):
            try:
                InstallJson(filename=os.path.basename(filename), path=str(tcpb_path)).data
                assert True
            except Exception as ex:
                assert False, f'Failed parsing file {os.path.basename(filename)} ({ex})'

    @staticmethod
    def test_tcpb_support():
        """."""
        tcpb_path = Path('tests/app_config_model/install_json_samples/tcpb')
        for filename in sorted(tcpb_path.glob('**/*')):
            try:
                InstallJson(filename=os.path.basename(filename), path=str(tcpb_path)).data
                assert True
            except Exception as ex:
                assert False, f'Failed parsing file {os.path.basename(filename)} ({ex})'

    @staticmethod
    def test_tcva_support():
        """."""
        tcpb_path = Path('tests/app_config_model/install_json_samples/tcva')
        for filename in sorted(tcpb_path.glob('**/*')):
            try:
                InstallJson(filename=os.path.basename(filename), path=str(tcpb_path)).data
                assert True
            except Exception as ex:
                assert False, f'Failed parsing file {os.path.basename(filename)} ({ex})'

    @staticmethod
    def test_tcvc_support():
        """."""
        tcpb_path = Path('tests/app_config_model/install_json_samples/tcvc')
        for filename in sorted(tcpb_path.glob('**/*')):
            try:
                InstallJson(filename=os.path.basename(filename), path=str(tcpb_path)).data
                assert True
            except Exception as ex:
                assert False, f'Failed parsing file {os.path.basename(filename)} ({ex})'

    @staticmethod
    def test_tcvw_support():
        """."""
        tcpb_path = Path('tests/app_config_model/install_json_samples/tcvw')
        for filename in sorted(tcpb_path.glob('**/*')):
            try:
                InstallJson(filename=os.path.basename(filename), path=str(tcpb_path)).data
                assert True
            except Exception as ex:
                assert False, f'Failed parsing file {os.path.basename(filename)} ({ex})'
