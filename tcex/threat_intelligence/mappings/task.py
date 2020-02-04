# -*- coding: utf-8 -*-
"""ThreatConnect TI Adversary """
from urllib.parse import quote_plus

from .mappings import Mappings


class Task(Mappings):
    """Unique API calls for Tasks API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """Initialize Class Properties.

        Valid status:
        + Not Started
        + In Progress
        + Completed
        + Waiting on Someone
        + Deferred

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
            status (str, kwargs): Not started, In Progress, Completed, Waiting on Someone, Deferred
            due_date (str, kwargs): Converted to %Y-%m-%dT%H:%M:%SZ date format
            reminder_date (str, kwargs): Converted to %Y-%m-%dT%H:%M:%SZ date format
            escalation_date (str, kwargs): Converted to %Y-%m-%dT%H:%M:%SZ date format
        """

        super().__init__(
            tcex,
            main_type='Task',
            api_type='tasks',
            sub_type=None,
            api_entity='task',
            api_branch=None,
            owner=kwargs.pop('owner'),
        )
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
        Return:

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

        due_date = self._utils.datetime.format_datetime(due_date, date_format='%Y-%m-%dT%H:%M:%SZ')
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

        reminder_date = self._utils.datetime.format_datetime(
            reminder_date, date_format='%Y-%m-%dT%H:%M:%SZ'
        )
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

        escalation_date = self._utils.datetime.format_datetime(
            escalation_date, date_format='%Y-%m-%dT%H:%M:%SZ'
        )
        self._data['escalationDate'] = escalation_date
        request = {'escalationDate': escalation_date}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def assignees(self):
        """
        Get the task assignees
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        yield from self.tc_requests.assignees(self.api_type, self.unique_id)

    def assignee(self, assignee_id, action='ADD'):
        """
        Add a assignee to the task

        Args:
            assignee_id: The id of the assignee to be added
            action:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.assignee(self.api_type, self.unique_id, assignee_id, action=action)

    def add_assignee(self, assignee_id):
        """
        Add a assignee to the task

        Args:
            assignee_id: The id of the assignee to be added

        """
        return self.assignee(assignee_id)

    def get_assignee(self, assignee_id):
        """
        Get a assignee from a task

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
        Get the task escalatees
        """
        print('after call')
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        yield from self.tc_requests.escalatees(self.api_type, self.unique_id)

    def escalatee(self, escalatee_id, action='ADD'):
        """
        Add a assignee to the task

        Args:
            escalatee_id: The id of the escalatee to be added
            action:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.escalatee(
            self.api_type, self.unique_id, escalatee_id, action=action
        )

    def add_escalatee(self, escalatee_id):
        """
        Add a escalatee to the task

        Args:
            escalatee_id: The id of the escalatee to be added

        """
        return self.escalatee(escalatee_id)

    def get_escalatee(self, escalatee_id):
        """
        Get a escalatee from a task

        Args:
            escalatee_id: The id of the escalatee to be added

        """
        return self.escalatee(escalatee_id, action='GET')

    def delete_escalatee(self, escalatee_id):
        """
        Deletes a escalatee from a task

        Args:
            escalatee_id: The id of the escalatee to be added

        """
        return self.escalatee(escalatee_id, action='DELETE')

    @property
    def _metadata_map(self):
        """Return metadata map for Group objects."""
        return {
            'due_date': 'dueDate',
            'reminder_date': 'reminderDate',
            'escalation_date': 'escalationDate',
        }

    def add_key_value(self, key, value):
        """
        Converts the value and adds it as a data field.

        Args:
            key:
            value:
        """
        key = self._metadata_map.get(key, key)
        if key == 'unique_id':
            self._unique_id = quote_plus(str(value))
        elif key in ['dueDate', 'reminderDate', 'escalationDate']:
            self._data[key] = self._utils.datetime.format_datetime(
                value, date_format='%Y-%m-%dT%H:%M:%SZ'
            )
        else:
            self._data[key] = value

    def can_create(self):
        """
         If the name has been provided returns that the Task can be created, otherwise
         returns that the Task cannot be created.

         Return:

         """
        if self.data.get('name'):
            return True
        return False
