"""Test the LayoutJson Config"""
# standard library
import os
from pathlib import Path

# first-party
# from tcex.app_config.install_json import InstallJson
from tcex.app_config.layout_json import LayoutJson


class TestLayoutJsonModel:
    """Test the TcEx App Feature Advance Request Module."""

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     tcpb_path = Path('tests/app_config_model/layout_json_samples/tcpb')
    #     for filename in sorted(tcpb_path.glob('**/*')):
    #         try:
    #             lj = LayoutJson(filename=os.path.basename(filename), path=str(tcpb_path))
    #             assert True
    #         except Exception as ex:
    #             assert False, f'Failed parsing file {os.path.basename(filename)} ({ex})'

    #         # ij = InstallJson(
    #         #     filename='tcpb_-_blackberry_optics-install.json',
    #         #     path='tests/app_config_model/install_json_samples/tcpb',
    #         # )
    #         print('\nfilename', filename)
    #         # lj.create(inputs=ij.data.params, outputs=ij.data.playbook.output_variables)
    #         print('lj.data.inputs', lj.data.inputs)
    #         # print('lj.data.outputs', lj.data.outputs)

    #         break

    @staticmethod
    def test_tcpb_support():
        """."""
        tcpb_path = Path('tests/app_config_model/layout_json_samples/tcpb')
        for filename in sorted(tcpb_path.glob('**/*')):
            try:
                LayoutJson(filename=os.path.basename(filename), path=str(tcpb_path)).data
                assert True
            except Exception as ex:
                assert False, f'Failed parsing file {os.path.basename(filename)} ({ex})'

    @staticmethod
    def test_tcvc_support():
        """."""
        tcpb_path = Path('tests/app_config_model/layout_json_samples/tcvc')
        for filename in sorted(tcpb_path.glob('**/*')):
            try:
                LayoutJson(filename=os.path.basename(filename), path=str(tcpb_path)).data
                assert True
            except Exception as ex:
                assert False, f'Failed parsing file {os.path.basename(filename)} ({ex})'
