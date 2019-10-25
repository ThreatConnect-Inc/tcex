# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import os


# pylint: disable=R0201,W0201
class TestUtils:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @staticmethod
    def test_message_tc(tcex):
        """Test token renewal"""
        message_tc_file = os.path.join(tcex.default_args.tc_out_path, 'message.tc')

        # cleanup any previous message.tc file
        os.remove(message_tc_file)

        message = 'test'
        tcex.message_tc(message)

        with open(message_tc_file, 'r') as fh:
            message_tc = fh.read()

        if not message.endswith('\n'):
            # tcex will add a newline if it doesn't exist
            message += '\n'

        assert message == message_tc, 'message.tc did not match message'

    @staticmethod
    def test_message_tc_long_message(tcex):
        """Test token renewal"""
        message_tc_file = os.path.join(tcex.default_args.tc_out_path, 'message.tc')

        # cleanup any previous message.tc file
        os.remove(message_tc_file)

        message = (
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
        )
        tcex.message_tc(message)

        with open(message_tc_file, 'r') as fh:
            message_tc = fh.read()

        if not message.endswith('\n'):
            # tcex will add a newline if it doesn't exist
            message += '\n'

        assert message[-255:] == message_tc, 'message.tc did not match message'

    @staticmethod
    def test_message_tc_multiple_messages(tcex):
        """Test token renewal"""
        message_tc_file = os.path.join(tcex.default_args.tc_out_path, 'message.tc')

        # cleanup any previous message.tc file
        os.remove(message_tc_file)

        message = (
            'word word word word word word word word word word word word word word word word word '
        )
        tcex.message_tc(message)
        tcex.message_tc(message)
        tcex.message_tc(message)
        tcex.message_tc(message)

        message_tc_file = os.path.join(tcex.default_args.tc_out_path, 'message.tc')
        with open(message_tc_file, 'r') as fh:
            message_tc = fh.read()

        message = '\n'.join([message, message, message, message])
        if not message.endswith('\n'):
            # tcex will add a newline if it doesn't exist
            message += '\n'

        assert message[-255:] == message_tc, 'message.tc did not match message'
