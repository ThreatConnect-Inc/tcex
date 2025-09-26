"""TestMessageTc for TcEx Exit Message TC Module Testing.

This module contains comprehensive test cases for the TcEx Exit Message TC Module, specifically
testing the message.tc file functionality that writes exit messages to the ThreatConnect
platform including basic messages, long messages, and multiple message handling scenarios.

Classes:
    TestMessageTc: Test class for TcEx Exit Message TC Module functionality

TcEx Module Tested: exit.exit
"""




import pytest


from tcex import TcEx


class TestMessageTc:
    """TestMessageTc for TcEx Exit Message TC Module Testing.

    This class provides comprehensive testing for the TcEx Exit Message TC Module, covering
    various message.tc file scenarios including basic message writing, long message handling,
    multiple message processing, and file cleanup operations for the ThreatConnect platform.
    """

    def setup_class(self) -> None:
        """Configure setup before all tests.

        This method is called once before all test methods in the class to perform
        any necessary setup or configuration for the test suite.
        """

    @staticmethod
    def test_message_tc(tcex: TcEx) -> None:
        """Test Message TC Basic Functionality for TcEx Exit Message TC Module.

        This test case verifies that the basic message.tc functionality works correctly
        by writing a simple test message to the message.tc file, ensuring proper file
        creation, message writing, and content validation.

        Fixtures:
            tcex: TcEx instance with exit functionality configured
        """
        # get the current out path from tcex
        message_tc_file = tcex.inputs.model.tc_out_path / 'message.tc'

        # cleanup any previous message.tc file
        if message_tc_file.is_file():
            message_tc_file.unlink()

        # create and write a test message
        message = 'test'
        tcex.exit._message_tc(message)  # noqa: SLF001

        # assert the file exists
        if not message_tc_file.is_file():
            pytest.fail(f'The message.tc file {message_tc_file} could not be found.')

        # read contents of file for assert
        with message_tc_file.open() as fh:
            message_tc = fh.read()

        # add a new line if not already there (tcex will add a newline if it doesn't exist)
        if not message.endswith('\n'):
            message += '\n'

        # assert message is correct
        assert message == message_tc, 'message.tc did not match message'

    @staticmethod
    def test_message_tc_long_message(tcex: TcEx) -> None:
        """Test Message TC Long Message Handling for TcEx Exit Message TC Module.

        This test case verifies that the message.tc functionality correctly handles long
        messages by truncating them to the maximum allowed length (255 characters) and
        preserving the last portion of the message as specified by the platform requirements.

        Fixtures:
            tcex: TcEx instance with exit functionality configured
        """
        # get the current out path from tcex
        message_tc_file = tcex.inputs.model.tc_out_path / 'message.tc'

        # cleanup any previous message.tc file
        if message_tc_file.is_file():
            message_tc_file.unlink()

        # create and write a test message
        message = (
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
            'word word word word word word word word word word word word word word word word word '
        )
        tcex.exit._message_tc(message)  # noqa: SLF001

        # assert the file exists
        if not message_tc_file.is_file():
            pytest.fail(f'The message.tc file {message_tc_file} could not be found.')

        # read contents of file for assert
        with message_tc_file.open() as fh:
            message_tc = fh.read()

        # add a new line if not already there (tcex will add a newline if it doesn't exist)
        if not message.endswith('\n'):
            message += '\n'

        # assert message is correct
        assert message[-255:] == message_tc, 'message.tc did not match message'

    @staticmethod
    def test_message_tc_multiple_messages(tcex: TcEx) -> None:
        """Test Message TC Multiple Message Handling for TcEx Exit Message TC Module.

        This test case verifies that the message.tc functionality correctly handles multiple
        consecutive message calls by processing each message and ensuring that only the
        last message is preserved in the file, maintaining the expected behavior for
        multiple message scenarios.

        Fixtures:
            tcex: TcEx instance with exit functionality configured
        """
        # get the current out path from tcex
        message_tc_file = tcex.inputs.model.tc_out_path / 'message.tc'

        # cleanup any previous message.tc file
        if message_tc_file.is_file():
            message_tc_file.unlink()

        message = (
            'word word word word word word word word word word word word word word word word word '
        )
        tcex.exit._message_tc(message)  # noqa: SLF001
        tcex.exit._message_tc(message)  # noqa: SLF001
        tcex.exit._message_tc(message)  # noqa: SLF001
        tcex.exit._message_tc(message)  # noqa: SLF001

        # assert the file exists
        if not message_tc_file.is_file():
            pytest.fail(f'The message.tc file {message_tc_file} could not be found.')

        # read contents of file for assert
        with message_tc_file.open() as fh:
            message_tc = fh.read()

        assert f'{message[-255:]}\n' == message_tc, 'message.tc did not match message'
