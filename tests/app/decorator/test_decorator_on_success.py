"""TcEx Framework Module"""
# standard library
from collections.abc import Callable

# first-party
from tcex.app.decorator.on_success import OnSuccess
from tests.mock_app import MockApp


class TestOnSuccessDecorators:
    """Test the TcEx Decorators."""

    args = None
    exit_message = None
    tcex = None

    @OnSuccess(exit_msg='on_success method passed')  # type: ignore
    def on_success(self):
        """Test on success decorator."""

    def test_on_success(self, playbook_app: Callable[..., MockApp]):
        """Test OnSuccess decorator."""
        self.tcex = playbook_app().tcex

        # call method with decorator
        self.on_success()
        assert self.exit_message == 'on_success method passed'
