# -*- coding: utf-8 -*-
"""Test the TcEx Notification Module."""


# pylint: disable=no-self-use
class TestNotification:
    """Test the TcEx Notification Module."""

    @staticmethod
    def test_notification_organization(tcex):
        """Test Org notifications

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        notification = tcex.notification()
        notification.org(notification_type='PyTest notification', priority='Low')
        status = notification.send(message='High alert send to organization.')
        assert status.get('status') == 'Success'

    @staticmethod
    def test_notification_recipients(tcex):
        """Test recipient notifications

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        notification = tcex.notification()
        notification.recipients(
            notification_type='PyTest recipients notification',
            recipients='pytest@tci.ninja',
            priority='High',
        )
        status = notification.send(message='High alert send to recipients.')
        assert status.get('status') == 'Success'

    @staticmethod
    def test_notification_invalid_recipients(tcex):
        """Test invalid recipient notifications

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        notification = tcex.notification()
        notification.recipients(
            notification_type='PyTest recipients notification',
            recipients='bob@tci.ninja',
            priority='High',
        )
        status = notification.send(message='High alert send to recipients.')
        assert status.get('status') == 'Failure'
