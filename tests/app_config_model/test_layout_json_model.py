"""Test the LayoutJson Config"""
# pylint: disable=R1710
# standard library
import json
import os
import shutil
from pathlib import Path
from typing import Optional

# third-party
from deepdiff import DeepDiff

# first-party
from tcex.app_config.install_json import InstallJson
from tcex.app_config.layout_json import LayoutJson
from tcex.app_config.models.layout_json_model import OutputsModel, ParametersModel


class TestLayoutJsonModel:
    """Test the TcEx App Feature Advance Request Module."""

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     fqfn = Path('tests/app_config_model/layout_json_samples/tcpb/tcpb-example1-layout.json')
    #     try:
    #         lj = LayoutJson(filename=fqfn.name, path=fqfn.parent)
    #     except Exception as ex:
    #         assert False, f'Failed parsing file {fqfn.name} ({ex})'

    #     # ij = InstallJson(
    #     #     filename='tcpb_-_blackberry_optics-install.json',
    #     #     path='tests/app_config_model/install_json_samples/tcpb',
    #     # )
    #     print('\nfilename', filename)
    #     # lj.create(inputs=ij.data.params, outputs=ij.data.playbook.output_variables)
    #     print('lj.data.inputs', lj.data.inputs)
    #     # print('lj.data.outputs', lj.data.outputs)

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
    def lj(app_type: str, filename: Optional[str] = None):
        """Return layout.json instance."""
        filename = filename or f'{app_type}-example1-layout.json'
        base_path = f'tests/app_config_model/layout_json_samples/{app_type}'
        fqfn = Path(os.path.join(base_path, filename))
        try:
            return LayoutJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def lj_bad(app_type: str):
        """Return layout.json instance with "bad" file."""
        base_path = f'tests/app_config_model/layout_json_samples/{app_type}'
        shutil.copy2(
            os.path.join(base_path, f'{app_type}-example1-layout-bad-template.json'),
            os.path.join(base_path, f'{app_type}-example1-layout-bad.json'),
        )
        fqfn = Path(os.path.join(base_path, f'{app_type}-example1-layout-bad.json'))
        try:
            return LayoutJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def model_validate(path: str) -> None:
        """Validate input model in and out."""
        lj_path = Path(path)
        for fqfn in sorted(lj_path.glob('**/*layout.json')):
            fqfn = Path(fqfn)
            with fqfn.open() as fh:
                json_dict = json.load(fh)

            try:
                lj = LayoutJson(filename=fqfn.name, path=fqfn.parent)
                lj.update.multiple()
            except Exception as ex:
                assert False, f'Failed parsing file {fqfn.name} ({ex})'

            ddiff = DeepDiff(
                json_dict,
                lj.data.dict(by_alias=True, exclude_defaults=True, exclude_none=True),
                ignore_order=True,
            )
            assert ddiff == {}, f'Failed validation of file {fqfn.name}'

    def test_create(self):
        """Test method"""
        ij = self.ij('tcpb')
        lj = self.lj('tcpb', 'tcpb-layout-create.json')
        lj.create(inputs=ij.data.params, outputs=ij.data.playbook.output_variables)
        assert lj.fqfn.is_file()

        # remove temp file
        lj.fqfn.unlink()

    def test_has_layout(self):
        """Test method"""
        assert self.lj('tcpb').has_layout

    def test_model_get_param(self):
        """Test method"""
        assert isinstance(self.lj('tcpb').data.get_param('tc_action'), ParametersModel)

    def test_model_get_output(self):
        """Test method"""
        assert isinstance(self.lj('tcpb').data.get_output('test1.output'), OutputsModel)

    def test_model_output_(self):
        """Test method"""
        assert isinstance(self.lj('tcpb').data.outputs_, dict)

    def test_model_param_names(self):
        """Test method"""
        assert isinstance(self.lj('tcpb').data.param_names, list)

    def test_tcpb_support(self):
        """Validate layout.json files."""
        self.model_validate('tests/app_config_model/layout_json_samples/tcpb')

    def test_tcvc_support(self):
        """Validate layout.json files."""
        self.model_validate('tests/app_config_model/layout_json_samples/tcvc')
