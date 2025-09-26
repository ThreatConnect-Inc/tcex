"""TestJobJsonModel for TcEx App Config JobJson Model Module Testing.

This module contains comprehensive test cases for the TcEx App Config JobJson Model Module,
specifically testing JobJson configuration functionality including model validation,
file parsing, singleton management, and proper configuration behavior across different
JSON file formats and validation scenarios for TcEx application job configuration.

Classes:
    TestJobJsonModel: Test class for TcEx App Config JobJson Model Module functionality

TcEx Module Tested: app.config.job_json
"""


import json
from pathlib import Path

import pytest


from deepdiff import DeepDiff


from tcex.app.config.job_json import JobJson


class TestJobJsonModel:
    """TestJobJsonModel for TcEx App Config JobJson Model Module Testing.

    This class provides comprehensive testing for the TcEx App Config JobJson Model Module,
    covering various JobJson configuration scenarios including model validation,
    file parsing, singleton management, and proper configuration behavior for
    TcEx application job configuration management.
    """

    # @staticmethod
    # def test_dev_testing():
    #     """."""
    #     fqfn = Path('tests/app/config/app/tcpb/app_1/app_1_job.json')
    #     try:
    #         jj = JobJson(filename=fqfn.name, path=fqfn.parent)
    #     except Exception as ex:
    #         assert False, f'Failed parsing file {fqfn.name} ({ex})'

    #     print('\nfilename', fqfn.name)
    #     print('jj.model.allow_on_demand', jj.model.allow_on_demand)

    @staticmethod
    def jj(app_name: str = 'app_1', app_type: str = 'tcpb') -> JobJson:
        """Return job.json instance.

        This method creates and returns a JobJson instance for testing
        configuration scenarios with proper file path management.

        Parameters:
            app_name: The name of the application to test
            app_type: The type of application (e.g., tcpb, tcva)

        Returns:
            JobJson: Configured JobJson instance for testing
        """
        # reset singleton
        JobJson._instances = {}  # noqa: SLF001

        # the job.json file must be prefixed with the app_name
        tj_fqfn = (
            Path('tests') / 'app' / 'config' / 'apps' / app_type / app_name
            / f'{app_name}_job.json'
        )
        fqfn = tj_fqfn
        try:
            return JobJson(filename=fqfn.name, path=fqfn.parent)
        except Exception as ex:
            pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

    @staticmethod
    def model_validate(path: str) -> None:
        """Validate input model in and out.

        This method validates JobJson model configurations by comparing
        input JSON with parsed model output, ensuring proper model
        serialization and deserialization.

        Parameters:
            path: The path to validate JobJson model configurations
        """
        jj_path = Path(path)
        for fqfn_path in jj_path.glob('**/*job.json'):
            # reset singleton
            JobJson._instances = {}  # noqa: SLF001

            fqfn = Path(fqfn_path)
            with fqfn.open() as fh:
                json_dict = json.load(fh)

            try:
                jj = JobJson(filename=fqfn.name, path=fqfn.parent)
            except Exception as ex:
                pytest.fail(f'Failed parsing file {fqfn.name} ({ex})')

            ddiff = DeepDiff(
                json_dict,
                # template requires json dump to serialize certain fields
                json.loads(jj.model.model_dump_json(by_alias=True, exclude_defaults=True, exclude_none=True)),
                ignore_order=True,
            )
            assert not ddiff, f'Failed validation of file {fqfn.name}'

    def test_support(self) -> None:
        """Test Support for TcEx App Config JobJson Model Module.

        This test case validates JobJson configuration files by testing
        model validation across multiple configuration scenarios, ensuring
        proper parsing, validation, and model consistency.

        This test provides comprehensive validation of JobJson
        configuration file support and model integrity.
        """
        self.model_validate('tests/app/config/apps/tc')
