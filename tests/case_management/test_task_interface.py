# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
# standard library
import os
import time
from datetime import datetime, timedelta
from random import randint

# first-party
from tcex.case_management.tql import TQL

from .cm_helpers import CMHelper, TestCaseManagement


class TestTask(TestCaseManagement):
    """Test TcEx CM Task Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper('task')
        self.cm = self.cm_helper.cm
        self.tcex = self.cm_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_task_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_task_code_gen(self):
        """Generate code and docstring from Options methods.

        This is not truly a test case, but best place to store it for now.
        """
        doc_string, filter_map, filter_class = super().obj_code_gen()
        assert doc_string
        assert filter_map
        assert filter_class

    def test_task_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_task_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_task_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_task_create_by_case_id(self, request):
        """Test Task Creation"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get()

        # run assertions on returned data
        assert task.description == task_data.get('description')
        assert task.name == task_data.get('name')
        assert task.workflow_phase == task_data.get('workflow_phase')
        assert task.workflow_step == task_data.get('workflow_step')

    def test_task_create_by_case_xid(self, request):
        """Test Task Creation"""
        # create case
        case_xid = f'{request.node.name}-{time.time()}'
        self.cm_helper.create_case(xid=case_xid)

        # task data
        task_data = {
            'case_xid': case_xid,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get()

        # run assertions on returned data
        assert task.description == task_data.get('description')
        assert task.name == task_data.get('name')
        assert task.workflow_phase == task_data.get('workflow_phase')
        assert task.workflow_step == task_data.get('workflow_step')

    def test_task_delete_by_id(self, request):
        """Test Artifact Deletion"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get()

        # delete the artifact
        task.delete()

        # test artifact is deleted
        try:
            task.get()
            assert False
        except RuntimeError:
            pass

    def test_task_get_many(self, request):
        """Test Task Get Many"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get()

        # iterate over all tasks looking for needle
        for t in self.cm.tasks():
            if t.name == task_data.get('name'):
                assert task.description == task_data.get('description')
                break
        else:
            assert False

    def test_task_get_single_by_id(self, request):
        """Test Task Get Many"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)

        # add assignee
        assignee_data = {'type': 'User', 'data': {'userName': os.getenv('API_ACCESS_ID')}}
        task.assignee = assignee_data

        # add note
        notes_data = {
            'data': [{'text': 'a note for test_task_get_single_by_id_properties'}],
        }
        task.notes = notes_data

        # submit task
        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get()

        # run assertions on returned data
        assert task.description == task_data.get('description')
        assert task.name == task_data.get('name')
        assert task.workflow_phase == task_data.get('workflow_phase')
        assert task.workflow_step == task_data.get('workflow_step')

    def test_task_update_properties(self, request):
        """Test updating artifacts properties"""
        case = self.cm_helper.create_case()

        task_data = {
            'case_id': case.id,
            'completed_date': datetime.now().isoformat(),
            'description': f'a description from {request.node.name}',
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
            'name': f'name-{request.node.name}',
            'note_text': f'a note for {request.node.name}',
            'status': 'Open',
            # 'workflow_phase': 0,
            # 'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }
        # create artifact
        task = self.cm.task(**task_data)
        task.submit()
        # artifact data updated
        task_data = {
            'assignee': {'user_name': os.getenv('API_ACCESS_ID')},
            'description': f'a updated description from {request.node.name}',
            'due_date': (datetime.now() + timedelta(days=3)).isoformat(),
            'name': f'updated-name-{request.node.name}',
            'status': 'Closed',
            'workflow_phase': 1,
            'workflow_step': 2,
        }
        task.assignee = self.cm.assignee(**task_data.get('assignee'))
        task.description = task_data.get('description')
        task.due_date = task_data.get('due_date')
        task.name = task_data.get('name')
        # task.workflow_phase = task_data.get('workflow_phase')
        # task.workflow_step = task_data.get('workflow_step')
        task.submit()
        task.get(all_available_fields=True)

        assert task.assignee.user_name == task_data.get('assignee').get('user_name')
        assert task.description == task_data.get('description')
        assert task_data.get('due_date')[:10] in task.due_date
        assert task.name == task_data.get('name')
        # assert task.workflow_phase == task_data.get('workflow_phase')
        # assert task.workflow_step == task_data.get('workflow_step')

    def test_task_task_config_mapping(self):
        """Test Task Get Many"""
        # create case
        # task config data
        task_config_data = [
            {
                'artifactType': 'ASN',
                'dataType': 'String',
                'intelType': 'indicator-ASN',
                'name': 'dummy_field',
                'uiElement': 'String',
                'uiLabel': 'ui_label?',
            }
        ]

        # create task
        task_data = {'config_task': task_config_data}
        task = self.cm.task(**task_data)

        counter = 0
        for config_task in task.config_task.config_tasks:
            counter += 1
            assert config_task.as_dict is not None
            assert config_task.body == {}
            assert config_task.artifact_type == 'ASN'
            assert config_task.data_type == 'String'
            assert config_task.intel_type == 'indicator-ASN'
            assert config_task.name == 'dummy_field'
            assert config_task.required is None
            assert config_task.ui_element == 'String'
            assert config_task.ui_label == 'ui_label?'
        assert task.config_task.as_dict is not None
        assert task.config_task.body == {}

        assert counter == 1

    def test_task_get_single_by_id_properties(self, request):
        """Test Task Get Many"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'case_xid': case.xid,
            'completed_date': datetime.now().isoformat(),
            'description': f'a description from {request.node.name}',
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
            'name': f'name-{request.node.name}',
            'note_text': f'a note for {request.node.name}',
            'status': 'Open',
            # 'workflow_phase': 0,
            # 'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task()

        # add properties
        task.case_id = task_data.get('case_id')
        task.case_xid = task_data.get('case_xid')
        task.completed_date = task_data.get('completed_date')
        task.description = task_data.get('description')
        task.due_date = task_data.get('due_date')
        task.name = task_data.get('name')
        task.status = task_data.get('status')
        # task.workflow_phase = task_data.get('workflow_phase')
        # task.workflow_step = task_data.get('workflow_step')
        task.xid = task_data.get('xid')

        # add artifacts
        artifact_data = {
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }
        task.add_artifact(**artifact_data)

        # add assignee
        assignee = self.cm.assignee(type='User', user_name=os.getenv('API_ACCESS_ID'))
        task.assignee = assignee

        # add note
        task.add_note(text=task_data.get('note_text'))

        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get(all_available_fields=True)

        # run assertions on returned data
        assert task.assignee.user_name == os.getenv('API_ACCESS_ID')
        assert task.case_id == task_data.get('case_id')
        assert task.case_xid is None  # note returned with task data
        assert task_data.get('completed_date')[:10] in task.completed_date
        assert task.description == task_data.get('description')
        assert task_data.get('due_date')[:10] in task.due_date
        assert task.name == task_data.get('name')
        for note in task.notes:
            if note.text == task_data.get('note_text'):
                break
        else:
            assert False, 'Note not found'
        assert task.status == task_data.get('status')
        # assert task.workflow_phase == task_data.get('workflow_phase')
        # assert task.workflow_step == task_data.get('workflow_step')
        assert task.xid == task_data.get('xid')

        # assert read-only data
        assert task.completed_by is None  # not returned in the response
        assert task.config_playbook is None  # not returned in the response
        assert task.config_task.config_tasks == []  # not returned in the response
        assert task.dependent_on_id is None  # not returned in the response
        assert task.duration is None  # not returned in the response
        assert task.parent_case.id == task_data.get('case_id')
        assert task.required is False

        # test as_entity
        assert task.as_entity.get('value') == task_data.get('name')

    def test_task_get_by_tql_filter_automated(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.automated(TQL.Operator.EQ, False)

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_case_id(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_case_severity(self, request):
        """Test Task Get by TQL"""
        # create case
        severity = 'Low'
        case = self.cm_helper.create_case(severity=severity)

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.id(TQL.Operator.EQ, task.id)
        tasks.filter.case_severity(TQL.Operator.EQ, severity)
        tasks.filter.case_id(TQL.Operator.EQ, case.id)

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    # unsure if there is a way to set completed by via UI
    def test_task_get_by_tql_filter_completed_by(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_completed_date(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'completed_date': datetime.now().isoformat(),
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.completed_date(
            TQL.Operator.GT, (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        )

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_config_playbook(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_config_task(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_description(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.description(TQL.Operator.EQ, task_data.get('description'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_due_date(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'due_date': (datetime.now() + timedelta(days=1)).isoformat(),
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.due_date(TQL.Operator.GT, datetime.now().strftime('%Y-%m-%d'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    # @mj - looking into a issue where artifact gets added to case and not task
    # artifact
    # def test_task_get_by_tql_filter_has_artifact(self, request):
    #     """Test Task Get by TQL"""
    #     # create case
    #     case = self.cm_helper.create_case()

    #     # task data
    #     task_data = {
    #         'case_id': case.id,
    #         'description': f'a description from {request.node.name}',
    #         'name': f'name-{request.node.name}',
    #         'xid': f'{request.node.name}-{time.time()}',
    #     }

    #     # create task
    #     task = self.cm.task(**task_data)

    #     # add artifacts
    #     artifact_data = {
    #         'intel_type': 'indicator-ASN',
    #         'summary': f'asn{randint(100, 999)}',
    #         'type': 'ASN',
    #     }
    #     task.add_artifact(**artifact_data)

    #     # submit task
    #     task.submit()

    #     my_task = self.cm.task(id=task.id)
    #     my_task.get(all_available_fields=True)

    #     # get artifact id
    #     for artifact in task.artifacts:
    #         artifact_id = artifact.id

    #     # retrieve tasks using TQL
    #     tasks = self.cm.tasks()
    #     tasks.filter.id(TQL.Operator.EQ, task.id)
    #     tasks.filter.has_artifact.id(TQL.Operator.EQ, artifact_id)

    #     for task in tasks:
    #         assert task.description == task_data.get('description')
    #         assert task.name == task_data.get('name')
    #         break
    #     else:
    #         assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_has_case(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.id(TQL.Operator.EQ, task.id)
        tasks.filter.has_case.id(TQL.Operator.EQ, case.id)

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_has_note(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.add_note(text='blah')
        task.submit()

        # get note id
        for note in task.notes:
            note_id = note.id

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.id(TQL.Operator.EQ, task.id)
        tasks.filter.has_note.id(TQL.Operator.EQ, note_id)

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_id(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.id(TQL.Operator.EQ, task.id)
        tasks.filter.description(TQL.Operator.EQ, task_data.get('description'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_name(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.name(TQL.Operator.EQ, task_data.get('name'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_required(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.required(TQL.Operator.EQ, False)

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_status(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'status': 'Open',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.status(TQL.Operator.EQ, task_data.get('status'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_target_id(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        assignee = self.cm.assignee(type='User', user_name=os.getenv('API_ACCESS_ID'))
        task_data = {
            'assignee': assignee,
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'status': 'Open',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.target_id(TQL.Operator.EQ, 5)

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_target_type(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        assignee = self.cm.assignee(type='User', user_name=os.getenv('API_ACCESS_ID'))
        task_data = {
            'assignee': assignee,
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'status': 'Open',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.target_type(TQL.Operator.EQ, 'User')

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_workflow_phase(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'status': 'Open',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.workflow_phase(TQL.Operator.EQ, 0)

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_workflow_step(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'status': 'Open',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.workflow_step(TQL.Operator.EQ, 1)

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_xid(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve tasks using TQL
        tasks = self.cm.tasks()
        tasks.filter.xid(TQL.Operator.EQ, task_data.get('xid'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
