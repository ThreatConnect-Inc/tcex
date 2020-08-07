"""Test the TcEx Threat Intel Module."""
# standard library
import os
import random
from datetime import datetime, timedelta

from .ti_helpers import TestThreatIntelligence, TIHelper


class TestTask(TestThreatIntelligence):
    """Test TcEx Threat Groups."""

    owner = os.getenv('TC_OWNER')
    ti = None
    ti_helper = None
    tcex = None

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper('Task')
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.ti_helper.cleanup()

    def tests_ti_task_create(self):
        """Create a task using specific interface."""
        task_data = {
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.task(**task_data)
        r = ti.create()
        assert ti.as_entity
        assert ti.as_dict

        # assert response
        assert r.status_code == 201

        # retrieve task for asserts
        task_data['unique_id'] = ti.unique_id
        ti = self.ti.task(**task_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get(ti.api_entity) == task_data.get(ti.api_entity)

        # cleanup task
        r = ti.delete()
        assert r.status_code == 200

    def tests_ti_task_add_attribute(self, request):
        """Test task add attribute."""
        helper_ti = self.ti_helper.create_task()

        attribute_data = {
            'attribute_type': 'Description',
            'attribute_value': request.node.name,
            'source': request.node.name,
            'displayed': True,
        }
        r = helper_ti.add_attribute(**attribute_data)
        response_data = r.json()
        ti_data = response_data.get('data', {}).get('attribute')

        # assert response
        assert r.status_code == 201
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('type') == attribute_data.get('attribute_type')
        assert ti_data.get('value') == attribute_data.get('attribute_value')
        assert ti_data.get('displayed') == attribute_data.get('displayed')

    def tests_ti_task_add_label(self):
        """Test task add label."""
        helper_ti = self.ti_helper.create_task()

        r = helper_ti.add_label(label='TLP:GREEN')
        response_data = r.json()

        # assert response
        assert r.status_code == 201
        assert response_data.get('status') == 'Success'

    def tests_ti_task_add_tag(self, request):
        """Test task add tag."""
        helper_ti = self.ti_helper.create_task()

        r = helper_ti.add_tag(request.node.name)
        response_data = r.json()

        # assert response
        assert r.status_code == 201
        assert response_data.get('status') == 'Success'

    def tests_ti_task_delete(self):
        """Test task delete."""
        helper_ti = self.ti_helper.create_task()

        # task for delete
        task_data = {
            # 'name': helper_ti.name,
            'owner': helper_ti.owner,
            'unique_id': helper_ti.unique_id,
        }
        ti = self.ti.task(**task_data)
        r = ti.delete()
        response_data = r.json()

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

    def tests_ti_task_get(self):
        """Test task get with generic task method."""
        helper_ti = self.ti_helper.create_task()

        # retrieve the task
        task_data = {
            'owner': helper_ti.owner,
            'unique_id': helper_ti.unique_id,
        }
        ti = self.ti.task(**task_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('name') == helper_ti.name, (
            f"task value ({ti_data.get('name')}) doe not match"
            f'expected value of ({helper_ti.name})'
        )

    def tests_ti_task_get_filter(self):
        """Test task get with filter."""
        helper_ti = self.ti_helper.create_task()

        # retrieve the tasks
        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        tasks = self.ti.task(owner=helper_ti.owner)
        filters = self.ti.filters()
        filters.add_filter('name', '=', helper_ti.name)
        # coverage
        filters.add_filter('temp', '=', helper_ti.name)
        filters.remove_filter('temp')
        for task in tasks.many(filters=filters, params=parameters):
            if task.get('name') == helper_ti.name:
                break
        else:
            assert False, f'task {helper_ti.name} was not found.'

    def tests_ti_task_get_includes(self, request):
        """Test task get with includes."""
        attribute_data = {
            'attribute_type': 'Description',
            'attribute_value': request.node.name,
        }
        label_data = {'label': 'TLP:RED'}
        tag_data = {'name': request.node.name}
        helper_ti = self.ti_helper.create_task(
            attributes=attribute_data, labels=label_data, tags=tag_data
        )

        # retrieve the task
        task_data = {
            'owner': helper_ti.owner,
            'unique_id': helper_ti.unique_id,
        }
        ti = self.ti.task(**task_data)
        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        r = ti.single(params=parameters)
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('name') == helper_ti.name, (
            f"task value ({ti_data.get('name')}) doe not match"
            f'expected value of ({helper_ti.name})'
        )

        # validate metadata
        assert ti_data.get('attribute')[0].get('value') == attribute_data.get('attribute_value'), (
            f"attribute value {ti_data.get('attribute')[0].get('value')} does not match"
            f"expected value {attribute_data.get('attribute_value')}"
        )
        assert ti_data.get('securityLabel')[0].get('name') == label_data.get('label'), (
            f"label value {ti_data.get('securityLabel')[0].get('name')} does not match"
            f"expected value {label_data.get('label')}"
        )
        for tag in ti_data.get('tag'):
            if tag.get('name') == tag_data.get('name'):
                break
        else:
            assert False, f"Could not find tag {tag_data.get('name')}"

    def tests_ti_task_get_attribute(self, request):
        """Test task get attribute."""
        attribute_data = {
            'attribute_type': 'Description',
            'attribute_value': request.node.name,
        }
        helper_ti = self.ti_helper.create_task(attributes=attribute_data)

        # retrieve the task
        task_data = {
            'name': helper_ti.name,
            'owner': helper_ti.owner,
            'unique_id': helper_ti.unique_id,
        }
        ti = self.ti.task(**task_data)
        for attribute in ti.attributes():
            if attribute.get('value') == request.node.name:
                break
        else:
            assert False, f'Could not find attribute with value {request.node.name}'

    def tests_ti_task_get_label(self):
        """Test task get label."""
        label_data = {'label': 'TLP:RED'}
        helper_ti = self.ti_helper.create_task(labels=label_data)

        # retrieve the task
        task_data = {
            'name': helper_ti.name,
            'owner': helper_ti.owner,
            'unique_id': helper_ti.unique_id,
        }
        ti = self.ti.task(**task_data)
        for label in ti.labels():
            if label.get('name') == label_data.get('label'):
                break
        else:
            assert False, f"Could not find tag with value {label_data.get('label')}"

    def tests_ti_task_get_tag(self, request):
        """Test task get tag."""
        tag_data = {'name': request.node.name}
        helper_ti = self.ti_helper.create_task(tags=tag_data)

        # retrieve the task
        task_data = {
            'name': helper_ti.name,
            'owner': helper_ti.owner,
            'unique_id': helper_ti.unique_id,
        }
        ti = self.ti.task(**task_data)
        for tag in ti.tags():
            if tag.get('name') == request.node.name:
                break
        else:
            assert False, f'Could not find tag with value {request.node.name}'

    def tests_ti_task_update(self, request):
        """Test updating task metadata."""
        helper_ti = self.ti_helper.create_task()

        # update task
        task_data = {
            'name': request.node.name,
            'owner': self.owner,
            'unique_id': helper_ti.unique_id,
        }
        # add optional and required fields
        ti = self.ti.task(**task_data)
        r = ti.update()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        expected_status_code = 200
        expected_status = 'Success'
        assert r.status_code == expected_status_code, (
            f'status code ({r.status_code}) does not match '
            f'expected code of ({expected_status_code}).'
            f'({r.text}).'
        )
        assert response_data.get('status') == expected_status, (
            f"status ({response_data.get('status')}) does not "
            f'match expected status of ({expected_status})'
        )

        # validate ti data
        assert ti_data.get('name') == request.node.name, (
            f"task value ({ti_data.get('name')}) doe not match"
            f'expected value of ({request.node.name})'
        )

    #
    # Custom test cases
    #
    def tests_ti_task_assignees(self):
        """Test retrieving all task assignees."""
        helper_ti = self.ti_helper.create_task()
        assignees_len = 0
        helper_ti.add_assignee(os.getenv('API_ACCESS_ID'))
        for assignee in helper_ti.assignees():
            assert assignee.get('userName') == os.getenv('API_ACCESS_ID')
            assignees_len += 1
        assert assignees_len == 1, f'{assignees_len} assignees got added instead of 1.'

    def tests_ti_task_assignees_invalid(self):
        """Test retrieving all task assignees without task id."""
        task_data = {
            'owner': self.owner,
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        }
        ti = self.ti.task(**task_data)
        try:
            ti.assignees()
            assert False, 'failed to catch assignees fetch on an task with no id.'
        except RuntimeError:
            assert True, 'caught assignees fetch on an task with no id.'

    def tests_ti_task_assignee_add(self):
        """Test adding assignee to a task."""
        helper_ti = self.ti_helper.create_task()
        r = helper_ti.add_assignee(os.getenv('API_ACCESS_ID'))
        assert r.status_code == 200

    def tests_ti_task_assignee_add_invalid(self):
        """Test adding assignee to a task without task id."""
        task_data = {
            'owner': self.owner,
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        }
        ti = self.ti.task(**task_data)
        try:
            ti.add_assignee(os.getenv('API_ACCESS_ID'))
            assert False, 'failed to catch assignee add on an task with no id.'
        except RuntimeError:
            assert True, 'caught assignee add on an task with no id.'

    def tests_ti_task_assignee_delete(self):
        """Test deleting assignee of a task."""
        helper_ti = self.ti_helper.create_task()
        helper_ti.add_assignee(os.getenv('API_ACCESS_ID'))
        r = helper_ti.delete_assignee(os.getenv('API_ACCESS_ID'))
        assert r.status_code == 200

    def tests_ti_task_assignee_delete_invalid(self):
        """Test deleting assignee of a task without task id."""
        task_data = {
            'owner': self.owner,
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        }
        ti = self.ti.task(**task_data)
        try:
            ti.delete_assignee(os.getenv('API_ACCESS_ID'))
            assert False, 'failed to catch assignee delete on an task with no id.'
        except RuntimeError:
            assert True, 'caught assignee delete on an task with no id.'

    def tests_ti_task_assignee_get(self):
        """Test retrieving assignee of a task."""
        helper_ti = self.ti_helper.create_task()
        helper_ti.add_assignee(os.getenv('API_ACCESS_ID'))
        r = helper_ti.get_assignee(os.getenv('API_ACCESS_ID'))
        assert r.status_code == 200

    def tests_ti_task_assignee_get_invalid(self):
        """Test retrieving assignee of a task without task id."""
        task_data = {
            'owner': self.owner,
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        }
        ti = self.ti.task(**task_data)
        try:
            ti.get_assignee(os.getenv('API_ACCESS_ID'))
            assert False, 'failed to catch assignee get on an task with no id.'
        except RuntimeError:
            assert True, 'caught assignee get on an task with no id.'

    def tests_ti_task_due_date(self):
        """Test updating due date of a task."""
        helper_ti = self.ti_helper.create_task()
        due_date = (datetime.now() + timedelta(days=2)).isoformat()
        r = helper_ti.due_date(due_date)
        assert r.status_code == 200
        ti_data = r.json().get('data', {}).get(helper_ti.api_entity)
        assert ti_data.get('dueDate')[:10] == due_date[:10]

    def tests_ti_task_due_date_invalid(self):
        """Test updating due date of a task without task id."""
        task_data = {
            'owner': self.owner,
        }
        ti = self.ti.task(**task_data)
        try:
            due_date = (datetime.now() + timedelta(days=2)).isoformat()
            ti.due_date(due_date)
            assert False, 'failed to catch due_date update on an task with no id.'
        except RuntimeError:
            assert True, 'caught due_date update on an task with no id.'

    def tests_ti_task_escalatees(self):
        """Test retrieving all task escalatees."""
        helper_ti = self.ti_helper.create_task()
        escalatees_len = 0
        helper_ti.add_escalatee(os.getenv('API_ACCESS_ID'))
        for escalatee in helper_ti.escalatees():
            assert escalatee.get('userName') == os.getenv('API_ACCESS_ID')
            escalatees_len += 1
        assert escalatees_len == 1, f'{escalatees_len} got created instead of 1.'

    def tests_ti_task_escalatees_invalid(self):
        """Test retrieving all task escalatees without task id."""
        task_data = {
            'owner': self.owner,
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        }
        helper_ti = self.ti.task(**task_data)
        try:
            print('before call')
            helper_ti.escalatees()
            assert False, 'failed to catch escalatees fetch on an task with no id.'
        except RuntimeError:
            assert True, 'caught escalatees fetch on an task with no id.'

    def tests_ti_task_escalatee_add(self):
        """Test adding escalatee to a task."""
        helper_ti = self.ti_helper.create_task()
        r = helper_ti.add_escalatee(os.getenv('API_ACCESS_ID'))
        assert r.status_code == 200
        for escalatee in helper_ti.escalatees():
            assert escalatee.get('userName') == os.getenv('API_ACCESS_ID')

    def tests_ti_task_escalatee_add_invalid(self):
        """Test adding escalatee to a task without task id."""
        task_data = {
            'owner': self.owner,
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        }
        ti = self.ti.task(**task_data)
        try:
            ti.add_escalatee(os.getenv('API_ACCESS_ID'))
            assert False, 'failed to catch escalatee add on an task with no id.'
        except RuntimeError:
            assert True, 'caught escalatee add on an task with no id.'

    def tests_ti_task_escalatee_delete(self):
        """Test deleting escalatee of a task."""
        helper_ti = self.ti_helper.create_task()
        helper_ti.add_escalatee(os.getenv('API_ACCESS_ID'))
        r = helper_ti.delete_escalatee(os.getenv('API_ACCESS_ID'))
        assert r.status_code == 200
        escalatees_len = 0
        for escalatee in helper_ti.escalatees():  # pylint: disable=unused-variable
            escalatees_len += 1
        assert escalatees_len == 0, f'{escalatees_len} are present instead of 0.'

    def tests_ti_task_escalatee_delete_invalid(self):
        """Test deleting escalatee of a task without task id."""
        task_data = {
            'owner': self.owner,
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        }
        ti = self.ti.task(**task_data)
        try:
            ti.delete_escalatee(os.getenv('API_ACCESS_ID'))
            assert False, 'failed to catch escalatee delete on an task with no id.'
        except RuntimeError:
            assert True, 'caught escalatee delete on an task with no id.'

    def tests_ti_task_escalatee_get(self):
        """Test retrieving escalatee of a task."""
        helper_ti = self.ti_helper.create_task()
        helper_ti.add_escalatee(os.getenv('API_ACCESS_ID'))
        r = helper_ti.get_escalatee(os.getenv('API_ACCESS_ID'))
        assert r.status_code == 200

    def tests_ti_task_escalatee_get_invalid(self):
        """Test retrieving escalatee of a task without task id."""
        task_data = {
            'owner': self.owner,
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        }
        ti = self.ti.task(**task_data)
        try:
            ti.get_escalatee(os.getenv('API_ACCESS_ID'))
            assert False, 'failed to catch escalatee get on an task with no id.'
        except RuntimeError:
            assert True, 'caught escalatee get on an task with no id.'

    def tests_ti_task_escalation_date(self):
        """Test updating escalation date of a task."""
        helper_ti = self.ti_helper.create_task()
        escalation_date = (datetime.now() + timedelta(days=2)).isoformat()
        r = helper_ti.escalation_date(escalation_date)
        assert r.status_code == 200
        ti_data = r.json().get('data', {}).get(helper_ti.api_entity)
        assert ti_data.get('escalationDate')[:10] == escalation_date[:10]

    def tests_ti_task_escalation_date_invalid(self):
        """Test updating escalation date of a task without task id."""
        task_data = {
            'owner': self.owner,
        }
        ti = self.ti.task(**task_data)
        try:
            escalation_date = (datetime.now() + timedelta(days=2)).isoformat()
            ti.escalation_date(escalation_date)
            assert False, 'failed to catch escalation_date update on an task with no id.'
        except RuntimeError:
            assert True, 'caught escalation_date update on an task with no id.'

    def tests_ti_task_invalid_create(self):
        """Test attempted create without name set."""
        task_data = {
            'owner': self.owner,
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
        }
        ti = self.ti.task(**task_data)
        try:
            ti.create()
            assert False, 'failed to catch name not set on create.'
        except RuntimeError:
            assert True, 'caught  name not set on create.'

    def tests_ti_task_reminder_date_invalid(self):
        """Test updating reminder date of a task without task id."""
        task_data = {
            'owner': self.owner,
        }
        ti = self.ti.task(**task_data)
        try:
            reminder_date = (datetime.now() + timedelta(days=2)).isoformat()
            ti.reminder_date(reminder_date)
            assert False, 'failed to catch reminder_date update on an task with no id.'
        except RuntimeError:
            assert True, 'caught reminder_date update on an task with no id.'

    def tests_ti_task_reminder_date(self):
        """Test updating reminder date of a task."""
        helper_ti = self.ti_helper.create_task()
        reminder_date = (datetime.now() + timedelta(days=2)).isoformat()
        r = helper_ti.reminder_date(reminder_date)
        assert r.status_code == 200
        ti_data = r.json().get('data', {}).get(helper_ti.api_entity)
        assert ti_data.get('reminderDate')[:10] == reminder_date[:10]

    def tests_ti_task_status_invalid(self):
        """Test updating status of a task without task id."""
        task_data = {
            'owner': self.owner,
        }
        ti = self.ti.task(**task_data)
        try:
            status = random.choice(
                ['Not Started', 'In Progress', 'Completed', 'Waiting on Someone', 'Deferred']
            )
            ti.status(status)
            assert False, 'failed to catch status update on an task with no id.'
        except RuntimeError:
            assert True, 'caught status update on an task with no id.'

    def tests_ti_task_status(self):
        """Test updating status of a task."""
        helper_ti = self.ti_helper.create_task()
        status = random.choice(
            ['Not Started', 'In Progress', 'Completed', 'Waiting on Someone', 'Deferred']
        )
        r = helper_ti.status(status)
        assert r.status_code == 200
        ti_data = r.json().get('data', {}).get(helper_ti.api_entity)
        assert ti_data.get('status') == status
