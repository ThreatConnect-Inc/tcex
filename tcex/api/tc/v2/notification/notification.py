"""TcEx Framework Module"""

# standard library
import json
import logging

# third-party
from requests import Session

# first-party
from tcex.exit.error_code import handle_error
from tcex.logger.trace_logger import TraceLogger

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class Notification:
    """TcEx Notification Class"""

    def __init__(self, session_tc: Session):
        """Initialize the Class properties.

        Args:
            session_tc: An configured instance of request.Session with TC API Auth.
        """
        self.session_tc = session_tc

        # properties
        self._is_organization = False
        self._notification_type = None
        self._recipients = None
        self._priority = 'Low'
        self.log = _logger

    def recipients(self, notification_type: str, recipients: str, priority='Low'):
        """Set vars for the passed in data. Used for one or more recipient notification.

        .. code-block:: javascript

            {
                "notificationType": notification_type,
                "priority": priority
                "isOrganization": false,
                "recipients": recipients
            }

        Args:
            notification_type: The type of notification being sent.
            recipients: A comma delimited string of recipients.
            priority: The priority: Low, Medium, High.
        """
        self._notification_type = notification_type
        self._recipients = recipients
        self._priority = priority
        self._is_organization = False

    def org(self, notification_type: str, priority: str = 'Low'):
        """Set vars for the passed in data. Used for org notification.

        .. code-block:: javascript

            {
                "notificationType": notification_type,
                "priority": priority
                "isOrganization": true
            }

        Args:
            notification_type: The notification type.
            priority: The priority: Low, Medium, High.
        """
        self._notification_type = notification_type
        self._recipients = None
        self._priority = priority
        self._is_organization = True

    def send(self, message: str):
        """Send our message

        Args:
            message: The message to be sent.

        Returns:
            requests.models.Response: The response from the request.

        """
        body = {
            'notificationType': self._notification_type,
            'priority': self._priority,
            'isOrganization': self._is_organization,
            'message': message,
        }

        if self._recipients:
            body['recipients'] = self._recipients

        self.log.debug(f'notification body: {json.dumps(body)}')

        # create our tcex resource
        r = self.session_tc.post('/v2/notifications', json=body)
        if r.status_code == 400:
            # specifically handle unknown users
            self.log.error(f'Failed to send notification ({r.text})')
        elif not r.ok:  # pragma: no cover
            handle_error(750, [r.status_code, r.text])

        # return response body
        return r.json()
