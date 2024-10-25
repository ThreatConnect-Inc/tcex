"""TcEx Framework Module"""

# standard library
from collections.abc import Callable

# first-party
from tests.mock_app import MockApp


class TestInputsFileParams:
    """Test TcEx File Params Inputs."""

    @staticmethod
    def test_file_params(playbook_app: Callable[..., MockApp]):
        """Test reading input file for service Apps."""
        # additional input params to pass to MockApp
        config_data = {
            'one': '1',
            'two': '2',
        }
        tcex = playbook_app(config_data=config_data).tcex

        # assert args
        assert tcex.inputs.model.one == config_data.get('one')  # type: ignore
        assert tcex.inputs.model.two == config_data.get('two')  # type: ignore
