# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import os


class TestUtils:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @staticmethod
    def test_message_tc1(tcex):
        """Test message tc method.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        # get the current out path from tcex
        message_tc_file = os.path.join(tcex.default_args.tc_out_path, 'message.tc')

        # cleanup any previous message.tc file
        if os.path.isfile(message_tc_file):
            os.remove(message_tc_file)

        # create and write a test message
        message = 'test'
        tcex.message_tc(message)

        # assert the file exists
        if not os.path.isfile(message_tc_file):
            assert False, f'The message.tc file {message_tc_file} could not be found.'

        # read contents of file for assert
        with open(message_tc_file, 'r') as fh:
            message_tc = fh.read()

        # add a new line if not already there (tcex will add a newline if it doesn't exist)
        if not message.endswith('\n'):
            message += '\n'

        # assert message is correct
        assert message == message_tc, 'message.tc did not match message'

    @staticmethod
    def test_message_tc_long_message(tcex):
        """Test long provided to message.tc method.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        # get the current out path from tcex
        message_tc_file = os.path.join(tcex.default_args.tc_out_path, 'message.tc')

        # cleanup any previous message.tc file
        if os.path.isfile(message_tc_file):
            os.remove(message_tc_file)

        # create and write a test message
        message = (
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
        )
        tcex.message_tc(message)

        # assert the file exists
        if not os.path.isfile(message_tc_file):
            assert False, f'The message.tc file {message_tc_file} could not be found.'

        # read contents of file for assert
        with open(message_tc_file, 'r') as fh:
            message_tc = fh.read()

        # add a new line if not already there (tcex will add a newline if it doesn't exist)
        if not message.endswith('\n'):
            message += '\n'

        # assert message is correct
        assert message[-255:] == message_tc, 'message.tc did not match message'

    @staticmethod
    def test_message_tc_multiple_messages(tcex):
        """Test long provided to message.tc method.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        # get the current out path from tcex
        message_tc_file = os.path.join(tcex.default_args.tc_out_path, 'message.tc')

        # cleanup any previous message.tc file
        if os.path.isfile(message_tc_file):
            os.remove(message_tc_file)

        message = (
            'word word word word word word word word word word word word word word word word word '
        )
        tcex.message_tc(message)
        tcex.message_tc(message)
        tcex.message_tc(message)
        tcex.message_tc(message)

        # assert the file exists
        if not os.path.isfile(message_tc_file):
            assert False, f'The message.tc file {message_tc_file} could not be found.'

        # read contents of file for assert
        with open(message_tc_file, 'r') as fh:
            message_tc = fh.read()

        # add a new line if not already there (tcex will add a newline if it doesn't exist)
        message = '\n'.join([message, message, message, message])
        if not message.endswith('\n'):
            message += '\n'

        assert message[-255:] == message_tc, 'message.tc did not match message'
