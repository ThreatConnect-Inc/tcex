# -*- coding: utf-8 -*-
"""ThreatConnect TI Adversary """
# standard library
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
            owner=kwargs.pop('owner', None),
        )
        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    def _set_unique_id(self, json_response):
        """Set the unique id of the Group."""
        self.unique_id = json_response.get('id', '')

    @property
    def _metadata_map(self):
        """Return metadata map for Group objects."""
        return {
            'due_date': 'dueDate',
            'reminder_date': 'reminderDate',
            'escalation_date': 'escalationDate',
        }

    @property
    def as_entity(self):
        """Return the entity representation of the Task."""
        return {
            'type': 'Task',
            'value': self.name,
            'id': int(self.unique_id) if self.unique_id else None,
        }

    @property
    def name(self):
        """Return Task name."""
        return self._data.get('name')

    @name.setter
    def name(self, name):
        """Set the Group name."""
        self._data['name'] = name

    @staticmethod
    def is_task():
        """Return True if object is a task."""
        return True

    def add_assignee(self, assignee):
        """Add the desired assignee from the Task.

        Args:
            assignee (str): The assignee username

        Return:
            obj: The response of the POST.

        """
        return self.assignee(assignee)

    def add_key_value(self, key, value):
        """Convert the value and adds it as a data field.

        Args:
            key:
            value:
        """
        key = self._metadata_map.get(key, key)
        if key in ['unique_id', 'id']:
            self._unique_id = quote_plus(str(value))
        elif key in ['dueDate', 'reminderDate', 'escalationDate']:
            self._data[key] = self._utils.datetime.format_datetime(
                value, date_format='%Y-%m-%dT%H:%M:%SZ'
            )
        else:
            self._data[key] = value

    def add_escalatee(self, escalatee):
        """Add the desired escalatee from the Task.

        Args:
            escalatee (str): The escalatee username

        Return:
            obj: The response of the POST.

        """
        return self.escalatee(escalatee)

    def assignee(self, assignee, action='ADD'):
        """General method to perform actions on assignees

        Valid Actions:
        + ADD
        + GET
        + DELETE

        Args:
            assignee (str): The username of the assignee.
            action: [ADD, DELETE, GET] the action to be done on the escalatee. Defaults to
                ADD if not provided.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.assignee(self.api_type, self.unique_id, assignee, action=action)

    def assignees(self):
        """Yield the Assignee Users"""
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.assignees(self.api_type, self.unique_id)

    def can_create(self):
        """Return True if the Object can be created.

        Return:
            bool: Boolean value indicating whether the object can be created.
        """
        if self.data.get('name'):
            return True
        return False

    def delete_assignee(self, assignee):
        """Delete the desired assignee from the Task.

        Args:
            assignee (str): The assignee username

        Return:
            obj: The response of the DELETE.

        """
        return self.assignee(assignee, action='DELETE')

    def delete_escalatee(self, escalatee):
        """Delete the desired escalatee from the Task.

        Args:
            escalatee (str): The escalatee username

        Return:
            obj: The response of the DELETE.

        """
        return self.escalatee(escalatee, action='DELETE')

    def due_date(self, due_date):
        """Update the task due_date

        Args:
            due_date: Converted to %Y-%m-%dT%H:%M:%SZ date format
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        due_date = self._utils.datetime.format_datetime(due_date, date_format='%Y-%m-%dT%H:%M:%SZ')
        self._data['dueDate'] = due_date
        request = {'dueDate': due_date}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def escalatee(self, escalatee, action='ADD'):
        """General method to perform actions on escalatees

        Valid Actions:
        + ADD
        + GET
        + DELETE

        Args:
            escalatee (str): The username of the escalatee.
            action: [ADD, DELETE, GET] the action to be done on the escalatee. Defaults to
                ADD if not provided.

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.escalatee(self.api_type, self.unique_id, escalatee, action=action)

    def escalatees(self):
        """Yield the Escalatees Users"""
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.escalatees(self.api_type, self.unique_id)

    def escalation_date(self, escalation_date):
        """Update the task escalation_date

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

    def get_assignee(self, assignee):
        """Retrieve the desired assignee from the Task.

        Args:
            assignee (str): The assignee username

        Return:
            obj: The response of the GET.

        """
        return self.assignee(assignee, action='GET')

    def get_escalatee(self, escalatee):
        """Retrieve the desired escalatee from the Task.

        Args:
            escalatee (str): The escalatee username

        Return:
            obj: The response of the GET.

        """
        return self.escalatee(escalatee, action='GET')

    def reminder_date(self, reminder_date):
        """Update the task reminder_date

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

    def status(self, status):
        """Update the Task Status

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
