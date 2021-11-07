"""Test TcexJson"""
# pylint: disable=R1710
# standard library
import json
import os
from pathlib import Path

# third-party
from deepdiff import DeepDiff

# first-party
from tcex.app_config.job_json import JobJson


class TestJobJson:
    """App Config JobJson testing."""

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     fqfn = Path('tests/app_config/app/tcpb/app_1/app_1_job.json')
    #     try:
    #         jj = JobJson(filename=fqfn.name, path=fqfn.parent)
    #     except Exception as ex:
    #         assert False, f'Failed parsing file {fqfn.name} ({ex})'

    #     print('\nfilename', fqfn.name)
    #     print('jj.model.allow_on_demand', jj.model.allow_on_demand)

    @staticmethod
    def jj(app_name: str = 'app_1', app_type: str = 'tcpb'):
        """Return tcex.json instance."""
        # reset singleton
        JobJson._instances = {}

        # the job.json file must be prefixed with the app_name
        tj_fqfn = os.path.join(
            'tests', 'app_config', 'apps', app_type, app_name, f'{app_name}_job.json'
        )
        fqfn = Path(tj_fqfn)
        try:
            return JobJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            assert False, f'Failed parsing file {fqfn.name} ({ex})'

    @staticmethod
    def model_validate(path: str) -> None:
        """Validate input model in and out."""
        jj_path = Path(path)
        for fqfn in jj_path.glob('**/*job.json'):
            # reset singleton
            JobJson._instances = {}

            fqfn = Path(fqfn)
            with fqfn.open() as fh:
                json_dict = json.load(fh)

            try:
                jj = JobJson(filename=fqfn.name, path=fqfn.parent)
            except Exception as ex:
                assert False, f'Failed parsing file {fqfn.name} ({ex})'

            ddiff = DeepDiff(
                json_dict,
                # template requires json dump to serialize certain fields
                json.loads(jj.model.json(by_alias=True, exclude_defaults=True, exclude_none=True)),
                ignore_order=True,
            )
            assert ddiff == {}, f'Failed validation of file {fqfn.name}'

    def test_support(self):
        """Validate tcex.json files."""
        self.model_validate('tests/app_config/apps/tc')
