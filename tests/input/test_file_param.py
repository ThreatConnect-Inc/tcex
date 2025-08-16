"""TestInputsFileParams for file parameter input validation.

This module contains test cases for the TcEx Framework file parameter functionality,
specifically testing the ability to read and process input files for service applications
with additional configuration data.

Classes:
    TestInputsFileParams: Test cases for file parameter input validation

TcEx Module Tested: tcex.input.file_params
"""

# standard library
from collections.abc import Callable

# first-party
from tests.mock_app import MockApp


class TestInputsFileParams:
    """TestInputsFileParams for file parameter input validation.

    This class provides test coverage for file parameter functionality within the TcEx Framework,
    including validation of input file reading capabilities and configuration data processing
    for service applications.

    Fixtures:
        playbook_app: Provides configured test application instance with MockApp
    """

    @staticmethod
    def test_file_params(playbook_app: Callable[..., MockApp]) -> None:
        """Test file parameter input reading for service applications.

        Validates the ability to read input files and process additional configuration data
        through the TcEx Framework. Tests that configuration parameters passed to MockApp
        are properly accessible through the tcex.inputs.model interface.

        Playbook Data Type: File parameters with configuration data
        Validation: Input model data access and configuration parameter retrieval

        Args:
            playbook_app: Mock app fixture for testing file parameter functionality

        Fixtures:
            playbook_app: Provides configured test application instance with MockApp
        """
        # additional input params to pass to MockApp
        config_data = {
            'one': '1',
            'two': '2',
        }
        tcex = playbook_app(config_data=config_data).tcex

        # assert args
        assert tcex.inputs.model.one == config_data.get('one')  # type: ignore
        assert tcex.inputs.model.two == config_data.get('two')  # type: ignore
