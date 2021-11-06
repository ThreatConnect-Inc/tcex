"""Test the TcEx Inputs Config Module."""
# standard library
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFileParams:
    """Test TcEx File Params Inputs."""

    @staticmethod
    def test_file_params(playbook_app: 'MockApp'):
        """Test reading input file for service Apps.

        Args:
            service_app (fixture): An instance of MockApp.
        """
        # additional input params to pass to MockApp
        config_data = {
            'one': '1',
            'two': '2',
        }
        tcex = playbook_app(config_data=config_data).tcex

        # assert args
        assert tcex.inputs.data.one == config_data.get('one')
        assert tcex.inputs.data.two == config_data.get('two')
