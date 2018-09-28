# -*- coding: utf-8 -*-
""" TcEx Notification Module """
import json


class TcExNotificationV2(object):
    """TcEx Notification Class"""

    def __init__(self, tcex):
        """ Initialize the Class properties.

        Args:
            tcex (obj): An instance of TcEx object.
        """
        self._tcex = tcex
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
            'message': message
        }

        if self._recipients:
            body['recipients'] = self._recipients

        self._tcex.log.debug('notification body: {}'.format(json.dumps(body)))

        # create our tcex resource
        resource = resource = self._tcex.resource('Notification')
        resource.http_method = 'POST'
        resource.body = json.dumps(body)

        results = resource.request()  # do the request
        if results.get('response').status_code == 200:
            # everything worked
            response = results.get('response').json()
        elif results.get('response').status_code == 400:
            # failed..but known... user doesn't exist
            # just return and let calling app handle it
            err = 'Failed to send notification ({})'.format(results.get('response').text)
            self._tcex.log.error(err)
            response = results.get('response').json()
        else:
            # somekind of unknown error...raise
            err = 'Failed to send notification ({})'.format(results.get('response').text)
            self._tcex.log.error(err)
            raise RuntimeError(err)
        return response
