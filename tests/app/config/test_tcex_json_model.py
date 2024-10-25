"""TcEx Framework Module"""

# pylint: disable=R1710
# standard library
import json
import os
import shutil
from pathlib import Path

# third-party
from deepdiff import DeepDiff

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.app.config.tcex_json import TcexJson


class TestTcexJson:
    """App Config TcexJson testing."""

    @property
    def tcex_test_dir(self) -> Path:
        """Return tcex test directory."""
        tcex_test_dir = os.getenv('TCEX_TEST_DIR')
        if tcex_test_dir is None:
            assert False, 'TCEX_TEST_DIR environment variable not set.'
        return Path(tcex_test_dir)

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     fqfn = Path('tests/app/config/tcex_json_samples/example1-tcex.json')
    #     try:
    #         tj = TcexJson(filename=fqfn.name, path=fqfn.parent)
    #     except Exception as ex:
    #         assert False, f'Failed parsing file {fqfn.name} ({ex})'

    #     print('\nfilename', fqfn.name)
    #     print('tj.model.lib_versions', tj.model.lib_versions)
    #     print('tj.model.package', tj.model.package)
    #     print('tj.model.template', tj.model.template)

    def ij(self, app_name: str = 'app_1', app_type: str = 'tcpb'):
        """Return install.json instance."""
        # reset singleton
        # InstallJson._instances = {}

        fqfn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name / 'install.json'
        try:
            return InstallJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    def tj(self, app_name: str = 'app_1', app_type: str = 'tcpb'):
        """Return tcex.json instance."""
        # reset singleton
        TcexJson._instances = {}  # type: ignore

        fqfn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name / 'tcex.json'
        try:
            return TcexJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    def tj_bad(self, app_name: str = 'app_bad_tcex_json', app_type: str = 'tcpb'):
        """Return tcex.json instance with "bad" file."""
        # reset singleton
        TcexJson._instances = {}  # type: ignore

        base_fqpn = self.tcex_test_dir / 'app' / 'config' / 'apps' / app_type / app_name
        shutil.copy2(
            f'{base_fqpn}/tcex-template.json',
            f'{base_fqpn}/tcex.json',
        )
        fqfn = base_fqpn / 'tcex.json'
        try:
            return TcexJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    def model_validate(self, path: str):
        """Validate input model in and out."""
        tj_path = self.tcex_test_dir / path
        for fqfn in tj_path.glob('**/*tcex.json'):
            # reset singleton
            TcexJson._instances = {}  # type: ignore

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
                # template requires json dump to serialize certain fields
                json.loads(tj.model.json(by_alias=True, exclude_defaults=True, exclude_none=True)),
                ignore_order=True,
            )
            assert not ddiff, f'Failed validation of file {fqfn.name}'

    def test_print_warnings(self):
        """Test method"""
        tj = self.tj_bad()

        # remove temp file
        tj.fqfn.unlink()

    def test_update(self):
        """Test method"""
        tj = self.tj_bad()
        tj.ij = self.ij(app_name='app_bad_tcex_json', app_type='tcpb')

        try:
            tj.update.multiple(template='service_api')
            # print(tj.model.schema_json())
            print(
                tj.model.json(exclude_defaults=False, exclude_none=True, indent=2, sort_keys=True)
            )
            assert True
        except Exception as ex:
            assert False, f'Failed to update tcex.json file ({ex}).'
        finally:
            # cleanup temp file
            # tj.fqfn.unlink()
            pass

    def test_support(self):
        """Validate tcex.json files."""
        # self.model_validate(self.tj())
        self.model_validate('tests/app/config/apps/tcpb')
