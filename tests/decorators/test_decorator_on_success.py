# -*- coding: utf-8 -*-
"""Test the TcEx Debug Decorator."""
from tcex import OnSuccess


# pylint: disable=no-self-use
class TestOnSuccessDecorators:
    """Test the TcEx Decorators."""

    args = None
    exit_message = None
    tcex = None

    @OnSuccess(exit_msg='on_success method passed')
    def on_success(self):
        """Test on success decorator."""

    def test_on_success(self, playbook_app):
        """Test OnSuccess decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        self.tcex = playbook_app().tcex

        # call method with decorator
        self.on_success()
        assert self.exit_message == 'on_success method passed'
