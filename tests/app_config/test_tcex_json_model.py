"""Test TcexJson"""
# pylint: disable=R1710
# standard library
import json
import os
import shutil
from pathlib import Path

# third-party
from deepdiff import DeepDiff

# first-party
from tcex.app_config import InstallJson, TcexJson


class TestTcexJson:
    """App Config TcexJson testing."""

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     fqfn = Path('tests/app_config/tcex_json_samples/example1-tcex.json')
    #     try:
    #         tj = TcexJson(filename=fqfn.name, path=fqfn.parent)
    #     except Exception as ex:
    #         assert False, f'Failed parsing file {fqfn.name} ({ex})'

    #     print('\nfilename', fqfn.name)
    #     print('tj.data.lib_versions', tj.data.lib_versions)
    #     print('tj.data.package', tj.data.package)
    #     print('tj.data.template', tj.data.template)

    @staticmethod
    def ij(app_type: str):
        """Return install.json instance."""
        base_path = f'tests/app_config/install_json_samples/{app_type}'
        fqfn = Path(os.path.join(base_path, f'{app_type}-example1-install.json'))
        try:
            return InstallJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def tj():
        """Return tcex.json instance."""
        base_path = 'tests/app_config/tcex_json_samples'
        fqfn = Path(f'{base_path}/example1-tcex.json')
        try:
            return TcexJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def tj_bad():
        """Return tcex.json instance with "bad" file."""
        base_path = 'tests/app_config/tcex_json_samples'
        shutil.copy2(
            f'{base_path}/example1-tcex-bad-template.json',
            f'{base_path}/example1-tcex-bad.json',
        )
        fqfn = Path(os.path.join(base_path, 'example1-tcex-bad.json'))
        try:
            return TcexJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def model_validate(path: str) -> None:
        """Validate input model in and out."""
        tj_path = Path(path)
        for fqfn in sorted(tj_path.glob('**/*tcex.json')):
            fqfn = Path(fqfn)
            with fqfn.open() as fh:
                json_dict = json.load(fh)

            try:
                tj = TcexJson(filename=fqfn.name, path=fqfn.parent)
                # tj.update.multiple()
            except Exception as ex:
                assert False, f'Failed parsing file {fqfn.name} ({ex})'

            ddiff = DeepDiff(
                json_dict,
                tj.data.dict(by_alias=True, exclude_defaults=True, exclude_none=True),
                ignore_order=True,
            )
            assert ddiff == {}, f'Failed validation of file {fqfn.name}'

    def test_print_warnings(self):
        """Test method"""
        tj = self.tj_bad()
        tj.print_warnings()

        # remove temp file
        tj.fqfn.unlink()

    def test_update(self):
        """Test method"""
        tj = self.tj_bad()
        tj.ij = self.ij('tcpb')

        try:
            tj.update.multiple(template='service_api')
            assert True
        except Exception as ex:
            assert False, f'Failed to update tcex.json file ({ex}).'
        finally:
            # cleanup temp file
            tj.fqfn.unlink()

    def test_support(self):
        """Validate tcex.json files."""
        self.model_validate('tests/app_config/tcex_json_samples')
