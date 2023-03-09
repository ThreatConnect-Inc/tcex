"""Test the TcEx Notification Module."""

# first-party
from tcex.tcex import TcEx


class TestNotification:
    """Test the TcEx Notification Module."""

    @staticmethod
    def test_notification_organization(tcex: TcEx):
        """Test Org notification

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        notification = tcex.api.tc.v2.notification
        notification.org(notification_type='PyTest notification', priority='Low')
        status = notification.send(message='High alert send to organization.')
        assert status.get('status') == 'Success'

    @staticmethod
    def test_notification_recipients(tcex: TcEx):
        """Test recipient notification

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        notification = tcex.api.tc.v2.notification
        notification.recipients(
            notification_type='PyTest recipients notification',
            recipients='rsparkles',
            priority='High',
        )
        status = notification.send(message='High alert send to recipients.')
        assert status.get('status') == 'Success'

    @staticmethod
    def test_notification_invalid_recipients(tcex: TcEx):
        """Test invalid recipient notification

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        notification = tcex.api.tc.v2.notification
        notification.recipients(
            notification_type='PyTest recipients notification',
            recipients='bob@tci.ninja',
            priority='High',
        )
        status = notification.send(message='High alert send to recipients.')
        assert status.get('status') == 'Failure'
