"""Test the InstallJson Config"""
# standard library
import json
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
    def input_model_validate(path: str) -> None:
        """Validate input model in and out."""
        ij_path = Path(path)
        for fqfn in sorted(ij_path.glob('**/*.json')):
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

    def test_tc_support(self) -> None:
        """Validate install.json files."""
        self.input_model_validate('tests/app_config_model/install_json_samples/tc')

    def test_tcpb_support(self) -> None:
        """Validate install.json files."""
        self.input_model_validate('tests/app_config_model/install_json_samples/tcpb')

    def test_tcva_support(self) -> None:
        """Validate install.json files."""
        self.input_model_validate('tests/app_config_model/install_json_samples/tcva')

    def test_tcvc_support(self) -> None:
        """Validate install.json files."""
        self.input_model_validate('tests/app_config_model/install_json_samples/tcvc')

    def test_tcvw_support(self) -> None:
        """Validate install.json files."""
        self.input_model_validate('tests/app_config_model/install_json_samples/tcvw')
