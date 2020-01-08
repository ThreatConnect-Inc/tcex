# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os
from tcex.case_management.tql import TQL

from ..tcex_init import tcex
from .cm_helpers import CMHelper


# pylint: disable=W0201
class TestCaseIndicators:
    """Test TcEx Address Indicators."""

    cm = None
    cm_helper = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper(self.cm)

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

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
        artifact_data = {
            'asn4455': {'intel_type': 'indicator-ASN', 'type': 'ASN'},
            'asn5544': {'intel_type': 'indicator-ASN', 'type': 'ASN'},
        }

        # add artifacts
        for artifact, a_data in artifact_data.items():
            case.add_artifact(
                summary=artifact, intel_type=a_data.get('intel_type'), type=a_data.get('type'),
            )

        # note data
        note_data = [f'A note for pytest test {__name__}']

        # add notes
        for note in note_data:
            case.add_note(text=note)

        # tag data
        tag_data = [f'{__name__}-1', f'{__name__}-1']

        # add tags
        for tag in tag_data:
            case.add_tag(name=tag)

        # task data
        task_data = {'task-1': {'description': 'task description', 'status': 'Pending'}}

        # add task
        for task, t_data in task_data.items():
            case.add_task(
                name=task, description=t_data.get('description'), status=t_data.get('status')
            )

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
            assert artifact.summary in artifact_data.keys()
            # assert artifact.intel_type == 'indicator-ASN'
            assert artifact.type == 'ASN'

        for tag in case.tags:
            assert tag.name in tag_data

        for note in case.notes:
            assert note.text in note_data

        for task in case.tasks:
            assert task.name in task_data

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

    def test_case_get_many(self, request):
        """Test Case get many"""
        # create cases
        self.cm_helper.create_case(name=f'{request.node.name}-1', xid=f'{request.node.name}-1')
        self.cm_helper.create_case(name=f'{request.node.name}-2', xid=f'{request.node.name}-2')

        # specifically match the count of the cases created.
        case_count = 0
        for case in self.cm.cases():
            if case.name.startswith(request.node.name):
                case_count += 1

        # run assertions on case count
        assert case_count == 2

    def test_case_get_by_tql_filter_artifact_id(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_filter_created_by_id(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_filter_description(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_id(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_owner_name(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_resolution(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_severity(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_status(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_tag(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_target_id(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_target_type(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_task(self, request):
        """Test Case Get by TQL"""

    def test_case_get_by_tql_xid(self, request):
        """Test Case Get by TQL"""
