# -*- coding: utf-8 -*-
"""ThreatConnect TI Adversary """
from tcex.tcex_ti.mappings.tcex_ti_mappings import TIMappings

try:
    from urllib import quote_plus  # Python 2
except ImportError:
    from urllib.parse import quote_plus  # Python


class Task(TIMappings):
    """Unique API calls for Tasks API Endpoints"""

    def __init__(
        self, tcex, name, status, due_date, reminder_date, escalation_date, owner=None, **kwargs
    ):
        """Initialize Class Properties.

        Valid status:
        + Not Started
        + In Progress
        + Completed
        + Waiting on Someone
        + Deferred

        Args:
            tcex:
            status (str): Not started, In Progress, Completed, Waiting on Someone, Deferred
            due_date: Converted to %Y-%m-%dT%H:%M:%SZ date format
            reminder_date: Converted to %Y-%m-%dT%H:%M:%SZ date format
            escalation_date: Converted to %Y-%m-%dT%H:%M:%SZ date format
            **kwargs:
            name (str): The name for this Group.
        """

        super(Task, self).__init__(tcex, 'Task', 'tasks', None, 'task', None, owner)
        self._data['name'] = name
        if status:
            self._data['status'] = status
        if due_date:
            self._data['dueDate'] = due_date
        if reminder_date:
            self._data['reminderDate'] = reminder_date
        if escalation_date:
            self._data['escalationDate'] = escalation_date

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    @property
    def name(self):
        """Return Task name."""
        return self._data.get('name')

    @name.setter
    def name(self, name):
        """

        Args:
            name:
        """
        self._data['name'] = name

    @staticmethod
    def is_task():
        """
        Indicates that this is a task object
        Returns:

        """
        return True

    def _set_unique_id(self, json_response):
        """

        Args:
            json_response:
        """
        self.unique_id = json_response.get('id', '')

    def status(self, status):
        """
        Valid status:
        + Not Started
        + In Progress
        + Completed
        + Waiting on Someone
        + Deferred

        Args:
            status: Not Started, In Progress, Completed, Waiting on Someone, Deferred
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['status'] = status
        request = {'status': status}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def due_date(self, due_date):
        """
        Sets the task due_date
        Args:
            due_date: Converted to %Y-%m-%dT%H:%M:%SZ date format
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        due_date = self._utils.format_datetime(due_date, date_format='%Y-%m-%dT%H:%M:%SZ')
        self._data['dueDate'] = due_date
        request = {'dueDate': due_date}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def reminder_date(self, reminder_date):
        """
        Sets the task reminder_date
        Args:
            reminder_date: Converted to %Y-%m-%dT%H:%M:%SZ date format
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        reminder_date = self._utils.format_datetime(reminder_date, date_format='%Y-%m-%dT%H:%M:%SZ')
        self._data['reminderDate'] = reminder_date
        request = {'reminderDate': reminder_date}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def escalation_date(self, escalation_date):
        """
        Sets the task escalation_date
        Args:
            escalation_date: Converted to %Y-%m-%dT%H:%M:%SZ date format
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        escalation_date = self._utils.format_datetime(
            escalation_date, date_format='%Y-%m-%dT%H:%M:%SZ'
        )
        self._data['escalationDate'] = escalation_date
        request = {'escalationDate': escalation_date}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def assignees(self):
        """
        Gets the task assignees
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        for a in self.tc_requests.assignees(self.api_type, self.api_sub_type, self.unique_id):
            yield a

    def assignee(self, assignee_id, action='ADD'):
        """
        Adds a assignee to the task

        Args:
            assignee_id: The id of the assignee to be added
            action:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.assignee(
            self.api_type, self.api_sub_type, self.unique_id, assignee_id, action=action
        )

    def add_assignee(self, assignee_id):
        """
        Adds a assignee to the task

        Args:
            assignee_id: The id of the assignee to be added

        """
        return self.assignee(assignee_id)

    def get_assignee(self, assignee_id):
        """
        Gets a assignee from a task

        Args:
            assignee_id: The id of the assignee to be added

        """
        return self.assignee(assignee_id, action='GET')

    def delete_assignee(self, assignee_id):
        """
        Deletes a assignee from a task

        Args:
            assignee_id: The id of the assignee to be added

        """
        return self.assignee(assignee_id, action='DELETE')

    def escalatees(self):
        """
        Gets the task escalatees
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        for e in self.tc_requests.escalatees(self.api_type, self.api_sub_type, self.unique_id):
            yield e

    def escalatee(self, escalatee_id, action='ADD'):
        """
        Adds a assignee to the task

        Args:
            escalatee_id: The id of the escalatee to be added
            action:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.escalatee(
            self.api_type, self.api_sub_type, self.unique_id, escalatee_id, action=action
        )

    def add_escalatee(self, escalatee_id):
        """
        Adds a escalatee to the task

        Args:
            escalatee_id: The id of the escalatee to be added

        """
        return self.assignee(escalatee_id)

    def get_escalatee(self, escalatee_id):
        """
        Gets a escalatee from a task

        Args:
            escalatee_id: The id of the escalatee to be added

        """
        return self.assignee(escalatee_id, action='GET')

    def delete_escalatee(self, escalatee_id):
        """
        Deletes a escalatee from a task

        Args:
            escalatee_id: The id of the escalatee to be added

        """
        return self.assignee(escalatee_id, action='DELETE')

    def add_key_value(self, key, value):
        """
        Converts the value and adds it as a data field.

        Args:
            key:
            value:
        """
        if key == 'unique_id':
            self._unique_id = quote_plus(str(value))
        self._data[key] = value

    def can_create(self):
        """
         If the name has been provided returns that the Task can be created, otherwise
         returns that the Task cannot be created.

         Returns:

         """
        if not self.data.get('name', None):
            return False
        return True
