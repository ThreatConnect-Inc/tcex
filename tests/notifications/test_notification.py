# -*- coding: utf-8 -*-
"""Test the TcEx Notification Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestNotification:
    """Test the TcEx Notification Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @staticmethod
    def test_notification_organization():
        """Test org notification."""
        notification = tcex.notification()
        notification.org(notification_type='PyTest notification', priority='Low')
        status = notification.send(message='High alert send to organization.')
        assert status.get('status') == 'Success'

    @staticmethod
    def test_notification_recipients():
        """Test org notification."""
        notification = tcex.notification()
        notification.recipients(
            notification_type='PyTest recipients notification',
            recipients='pytest@tci.ninja',
            priority='High',
        )
        status = notification.send(message='High alert send to recipients.')
        assert status.get('status') == 'Success'
