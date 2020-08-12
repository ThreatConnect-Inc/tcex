# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
# standard library
import os
import random
import time
from datetime import datetime, timedelta

# third-party
from dateutil.parser import parse

# first-party
from tcex.case_management.tql import TQL

from .cm_helpers import CMHelper, TestCaseManagement


class TestCase(TestCaseManagement):
    """Test TcEx CM Case Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper('case')
        self.cm = self.cm_helper.cm
        self.tcex = self.cm_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_case_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_case_code_gen(self):
        """Generate code and docstring from Options methods.

        This is not truly a test case, but best place to store it for now.
        """
        doc_string, filter_map, filter_class = super().obj_code_gen()
        assert doc_string
        assert filter_map
        assert filter_class

    def test_case_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_case_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_case_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_case_create(self, request):
        """Test Case Creation"""
        case_data = {
            'name': request.node.name,
            'severity': 'Low',
            'status': 'Open',
        }
        case = self.cm.case(**case_data)
        case.submit()

        # retrieve case for asserts
        case = self.cm.case(id=case.id)
        case.get()

        # run assertions on returned data
        assert case.name == case_data.get('name')
        assert case.severity == case_data.get('severity')
        assert case.status == case_data.get('status')

        # cleanup case
        case.delete()

    def test_case_delete(self, request):
        """Test Case Deletion"""
        case = self.cm_helper.create_case()

        cases = self.cm.cases()
        cases.filter.name(TQL.Operator.EQ, request.node.name)
        for case in cases:
            if case.name == request.node.name:
                break
        else:
            # if this hit case was not deleted
            assert False, 'No case was return from TQL filter.'

    def test_case_create_with_metadata(self, request):
        """Test Case Creation"""
        case_data = {
            'name': request.node.name,
            'severity': 'Low',
            'status': 'Open',
        }

        # create case
        case = self.cm.case(**case_data)

        # artifact data
        artifact_data = [
            {'summary': 'asn4455', 'intel_type': 'indicator-ASN', 'type': 'ASN'},
            {'summary': 'asn5544', 'intel_type': 'indicator-ASN', 'type': 'ASN'},
        ]

        # add artifacts
        for artifact in artifact_data:
            case.add_artifact(**artifact)

        # note data
        note_data = [f'A note for pytest test {__name__}']

        # add notes
        for note in note_data:
            case.add_note(text=note)

        # tag data
        tag_data = [{'name': f'{__name__}-1'}, {'name': f'{__name__}-2'}]

        # add tags
        for tag in tag_data:
            case.add_tag(**tag)

        # task data
        task_data = [{'name': 'task-1', 'description': 'task description', 'status': 'Pending'}]

        # add task
        for task in task_data:
            case.add_task(**task)

        # submit case
        case.submit()

        # retrieve case for asserts
        case = self.cm.case(id=case.id)
        case.get(all_available_fields=True)

        # run assertions on returned data
        assert case.id
        assert case.name == request.node.name
        assert case.severity == case_data.get('severity')
        assert case.status == case_data.get('status')

        for artifact in case.artifacts:
            assert artifact.summary in [a.get('summary') for a in artifact_data]
            assert artifact.intel_type == 'indicator-ASN'
            assert artifact.type == 'ASN'

        for tag in case.tags:
            assert tag.name in [t.get('name') for t in tag_data]

        for note in case.notes:
            assert note.text in note_data

        for task in case.tasks:
            assert task.name in [t.get('name') for t in task_data]

        # cleanup case
        case.delete()

    def test_case_get_single_by_id(self, request):
        """Test Case get by ID"""
        # create case
        case = self.cm_helper.create_case()

        # retrieve case for asserts
        case = self.cm.case(id=case.id)
        case.get()

        # run assertions on returned data
        assert case.name == request.node.name

    def test_case_get_single_by_id_properties(self, request):
        """Test Case get single by id"""
        # create case
        case_data = {
            'description': f'case description for {request.node.name}',
            'name': f'case-{request.node.name}',
            'resolution': random.choice(
                [
                    'Containment Achieved',
                    'Deferred / Delayed',
                    'Escalated',
                    'False Positive',
                    'In Progress / Investigating',
                    'Not Specified',
                    'Rejected',
                    'Restoration Achieved',
                ]
            ),
            'severity': random.choice(['Low', 'Medium', 'High']),
            'status': random.choice(['Open', 'Closed']),
            'xid': f'{request.node.name}-{time.time()}',
        }
        # User data
        user_data = {
            'user_name': 'user name',
            'role': 'user role',
            'pseudonym': 'user pseudonym',
            'last_name': 'user last name',
            'id': 1,
            'first_name': 'user first name',
        }
        case = self.cm.case(**case_data)
        case.submit()

        file_data = (
            'RmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )
        # task data
        user = self.cm.user()
        user.user_name = os.getenv('API_ACCESS_ID')
        case.user_access.users.append(user)
        case.user_access.users = [user]
        case.assignee = self.cm.assignee(type='User', user_name=os.getenv('API_ACCESS_ID'))
        user_2 = self.cm.user()
        user_2.user_name = user_data.get('user_name')
        assert user_2.user_name == user_data.get('user_name')
        user_2.role = user_data.get('role')
        assert user_2.role == user_data.get('role')
        user_2.pseudonym = user_data.get('pseudonym')
        assert user_2.pseudonym == user_data.get('pseudonym')
        user_2.last_name = user_data.get('last_name')
        assert user_2.last_name == user_data.get('last_name')
        user_2.id = user_data.get('id')
        assert user_2.id == user_data.get('id')
        user_2.first_name = user_data.get('first_name')
        assert user_2.first_name == user_data.get('first_name')
        assert str(user_2)

        artifact_data = {
            'source': 'artifact source',
            'file_data': f'{file_data}',
            'summary': 'pytest test file artifact',
            'type': 'Certificate File',
        }
        note_data = {'text': 'Note text'}
        task_data = {
            'description': f'a description from {request.node.name}',
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
            'name': f'name-{request.node.name}',
            'status': 'Open',
        }
        tag_data = {'name': f'tag-{request.node.name}'}

        case.add_artifact(**artifact_data)
        case.add_note(**note_data)
        case.add_task(**task_data)
        case.add_tag(**tag_data)

        case.submit()
        # add properties

        case.artifacts = [artifact_data]
        case.tags = [tag_data]
        case.notes = [note_data]
        case.tasks = [task_data]
        case.xid = case.xid
        case.user_access = case.user_access
        case.description = case_data.get('description')
        case.name = case_data.get('name')
        case.resolution = case_data.get('resolution')
        case.severity = case_data.get('severity')
        case.status = case_data.get('status')
        # get task from API to use in asserts
        case = self.cm.case(id=case.id)
        case.get(all_available_fields=True)

        # run assertions on returned data
        assert case.description == case_data.get('description')
        assert case.name == case_data.get('name')
        assert case.resolution == case_data.get('resolution')
        assert case.severity == case_data.get('severity')
        assert case.status == case_data.get('status')
        assert len(case.tasks) == 1
        assert len(case.notes) == 1
        assert len(case.tags) == 1
        assert len(case.artifacts) == 1
        for task in case.tasks:
            assert task.description == task_data.get('description')
            assert task_data.get('due_date')[:10] in task.due_date
            assert task.name == task_data.get('name')
            assert task.status == task_data.get('status')
        for note in case.notes:
            assert note.text == note_data.get('text')
        for artifact in case.artifacts:
            assert artifact.source == artifact_data.get('source')
            assert artifact.summary == artifact_data.get('summary')
            assert artifact.type == artifact_data.get('type')
        for tag in case.tags:
            assert tag.name == tag_data.get('name')
        assert case.assignee.user_name == os.getenv('API_ACCESS_ID')
        assert len(case.user_access.users) == 1
        assert case.user_access.users[0].user_name == os.getenv('API_ACCESS_ID')
        assert case.created_by.user_name == os.getenv('API_ACCESS_ID')
        try:
            parse(case.date_added)
        except ValueError:
            assert False, 'Invalid date added'
        assert case.owner == os.getenv('API_DEFAULT_ORG')
        assert case.xid == case_data.get('xid')

        assert case.as_entity.get('value') == case_data.get('name')

    def test_case_get_many(self, request):
        """Test Case get many"""
        # create cases
        self.cm_helper.create_case(
            name=f'{request.node.name}-1', xid=f'{request.node.name}-{random.randint(1000, 9999)}'
        )
        self.cm_helper.create_case(
            name=f'{request.node.name}-2', xid=f'{request.node.name}-{random.randint(1000, 9999)}'
        )

        # add a small delay in case tc is busy
        time.sleep(1)

        # specifically match the count of the cases created.
        case_count = 0
        for case in self.cm.cases():
            if case.name.startswith(request.node.name):
                case_count += 1

        # run assertions on case count
        assert case_count == 2

    def test_case_get_by_tql_filter_created_by(self, request):
        """Test Case Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.created_by(TQL.Operator.EQ, os.getenv('API_ACCESS_ID'))

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_created_by_id(self, request):
        """Test Case Get by TQL

        # This method is geared more for the UI as we won't have easy access to user id
        """
        # create case
        case = self.cm_helper.create_case()

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.created_by_id(TQL.Operator.EQ, 5)

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_date_added(self, request):
        """Test Case Get by TQL"""
        # create case
        self.cm_helper.create_case()
        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.date_added(TQL.Operator.GT, (datetime.now() - timedelta(days=2)).isoformat())

        found = False
        for case in cases:
            if case.name == request.node.name:
                found = True
        assert found, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_description(self, request):
        """Test Case Get by TQL"""
        description = f'a test description for {request.node.name}'

        # create case
        case = self.cm_helper.create_case(description=description)

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.description(TQL.Operator.EQ, description)

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_update_properties(self, request):
        """Test updating artifacts properties"""
        case = self.cm_helper.create_case()

        # updated case data
        case_data = {
            'description': f'case description for {request.node.name}',
            'name': f'case-{request.node.name}',
            'assignee': {'user_name': os.getenv('API_ACCESS_ID')},
            'user_access': {'data': []},
            'resolution': random.choice(
                [
                    'Containment Achieved',
                    'Deferred / Delayed',
                    'Escalated',
                    'False Positive',
                    'In Progress / Investigating',
                    'Not Specified',
                    'Rejected',
                    'Restoration Achieved',
                ]
            ),
            'severity': random.choice(['Low', 'Medium', 'High']),
            'status': random.choice(['Open', 'Closed']),
        }

        case.assignee = self.cm.assignee(**case_data.get('assignee'))
        case.description = case_data.get('description')
        case.name = case_data.get('name')
        case.resolution = case_data.get('resolution')
        case.severity = case_data.get('severity')
        case.status = case_data.get('status')
        user = self.cm.user()
        user.user_name = os.getenv('API_ACCESS_ID')
        case.user_access.users.append(user)
        case.user_access.users = [user]

        case.submit()
        case.get(all_available_fields=True)

        assert case.assignee.user_name == case_data.get('assignee').get('user_name')
        assert case.description == case_data.get('description')
        assert case.name == case_data.get('name')
        assert case.resolution == case_data.get('resolution')
        assert case.severity == case_data.get('severity')
        assert case.status == case_data.get('status')
        assert len(case.user_access.users) == 1
        assert case.user_access.users[0].user_name == os.getenv('API_ACCESS_ID')
        assert case.as_dict

    def test_case_get_by_tql_filter_has_artifact(self, request):
        """Test Case Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        file_data = (
            'RmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )
        # task data
        artifact_data = {
            'case_id': case.id,
            'case_xid': case.xid,
            'source': 'artifact source',
            'file_data': f'{file_data}',
            'summary': f'artifact {request.node.name}',
            'type': 'Certificate File',
            'note_text': 'artifact note text',
        }

        # create task
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.has_artifact.summary(TQL.Operator.EQ, artifact_data.get('summary'))

        assert len(cases) == 1
        for case in cases:
            assert case.name == request.node.name
            assert case.id == artifact_data.get('case_id')
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_has_note(self, request):
        """Test Case Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'note_text - {request.node.name}',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.has_note.id(TQL.Operator.EQ, note.id)

        assert len(cases) == 1
        for case in cases:
            assert case.name == request.node.name
            assert case.id == note_data.get('case_id')
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_has_tag(self, request):
        """Test Case Get by TQL"""
        tag_data = {
            'name': f'tag-{request.node.name}',
            'description': f'a description for tag on {request.node.name}',
        }
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # create case
        case = self.cm_helper.create_case(tags=tag_data)

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.has_tag.id(TQL.Operator.EQ, tag.id)

        assert len(cases) == 1
        for case in cases:
            assert case.name == request.node.name
            assert case.id == case.id
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_has_task(self, request):
        """Test Case Get by TQL"""
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

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.has_task.id(TQL.Operator.EQ, task.id)

        assert len(cases) == 1
        for case in cases:
            assert case.name == request.node.name
            assert case.id == task_data.get('case_id')
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_id(self, request):
        """Test Case Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_name(self, request):
        """Test Case Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.name(TQL.Operator.EQ, case.name)

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_owner(self, owner_id, request):
        """Test Case Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.owner(TQL.Operator.EQ, owner_id(os.getenv('TC_OWNER')))

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_owner_name(self, request):
        """Test Case Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.owner_name(TQL.Operator.EQ, os.getenv('TC_OWNER'))

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_resolution(self, request):
        """Test Case Get by TQL"""
        resolution = 'Escalated'

        # create case
        case = self.cm_helper.create_case(resolution=resolution)

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.resolution(TQL.Operator.EQ, resolution)

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_severity(self, request):
        """Test Case Get by TQL"""
        severity = 'Low'
        # create case
        case = self.cm_helper.create_case(severity=severity)

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.severity(TQL.Operator.EQ, severity)

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_status(self, request):
        """Test Case Get by TQL"""
        status = 'Closed'
        # create case
        case = self.cm_helper.create_case(status=status)

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.status(TQL.Operator.EQ, status)

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_tag(self, request):
        """Test Case Get by TQL"""
        # create case
        tag_data = {'name': request.node.name}
        case = self.cm_helper.create_case(tags=tag_data)

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.tag(TQL.Operator.EQ, tag_data.get('name'))

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_target_id(self, request):
        """Test Case Get by TQL"""
        # create case
        assignee = self.cm.assignee(type='User', user_name=os.getenv('API_ACCESS_ID'))
        case = self.cm_helper.create_case(assignee=assignee)

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.target_id(TQL.Operator.EQ, 5)

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_target_type(self, request):
        """Test Case Get by TQL"""
        # create case
        assignee = self.cm.assignee(type='User', user_name=os.getenv('API_ACCESS_ID'))
        case = self.cm_helper.create_case(assignee=assignee)

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.target_type(TQL.Operator.EQ, 'User')

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'

    def test_case_get_by_tql_filter_xid(self, request):
        """Test Case Get by TQL"""
        # create case
        xid = request.node.name
        case = self.cm_helper.create_case(xid=xid)

        # retrieve note using TQL
        cases = self.cm.cases()
        cases.filter.id(TQL.Operator.EQ, case.id)
        cases.filter.xid(TQL.Operator.EQ, xid)

        for case in cases:
            assert case.name == request.node.name
            break
        else:
            assert False, 'No cases returned for TQL'
