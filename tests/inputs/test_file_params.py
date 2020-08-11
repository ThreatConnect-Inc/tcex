"""Test the TcEx Inputs Config Module."""


class TestInputsFileParams:
    """Test TcEx File Params Inputs."""

    @staticmethod
    def test_file_params(service_app):
        """Test reading input file for service Apps.

        Args:
            service_app (MockApp, fixture): An instantiated instance of MockApp.
        """
        config_data = {
            'one': '1',
            'two': '2',
        }
        tcex = service_app(config_data=config_data).tcex

        # assert args
        assert tcex.args.one == config_data.get('one')
        assert tcex.args.two == config_data.get('two')
