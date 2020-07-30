# -*- coding: utf-8 -*-
"""TcEx Notification Module"""
# standard library
import json


class Notifications:
    """TcEx Notification Class"""

    def __init__(self, tcex):
        """Initialize the Class properties.

        Args:
            tcex (obj): An instance of TcEx object.
        """
        self.tcex = tcex

        # properties
        self._is_organization = False
        self._notification_type = None
        self._recipients = None
        self._priority = 'Low'

    def recipients(self, notification_type, recipients, priority='Low'):
        """Set vars for the passed in data. Used for one or more recipient notification.

        .. code-block:: javascript

            {
                "notificationType": notification_type,
                "priority": priority
                "isOrganization": false,
                "recipients": recipients
            }

        Args:
            notification_type (str): The type of notification being sent.
            recipients (str): A comma delimited string of recipients.
            priority (str): The priority: Low, Medium, High.
        """
        self._notification_type = notification_type
        self._recipients = recipients
        self._priority = priority
        self._is_organization = False

    def org(self, notification_type, priority='Low'):
        """Set vars for the passed in data. Used for org notification.

        .. code-block:: javascript

            {
                "notificationType": notification_type,
                "priority": priority
                "isOrganization": true
            }

        Args:
            notification_type (str): The notification type.
            priority (str): The priority: Low, Medium, High.
        """
        self._notification_type = notification_type
        self._recipients = None
        self._priority = priority
        self._is_organization = True

    def send(self, message):
        """Send our message

        Args:
            message (str): The message to be sent.

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

        self.tcex.log.debug(f'notification body: {json.dumps(body)}')

        # create our tcex resource
        r = self.tcex.session.post('/v2/notifications', json=body)
        if r.status_code == 400:
            # specifically handle unknown users
            self.tcex.log.error(f'Failed to send notification ({r.text})')
        elif not r.ok:  # pragma: no cover
            self.tcex.handle_error(750, [r.status_code, r.text])

        # return response body
        return r.json()
