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

    def test_create(self):
        """Test Case Creation"""
        severity = 'Low'
        status = 'Open'
        case = self.cm.case(name=__name__, severity=severity, status=status)
        case.submit()

        # retrieve case for asserts
        case = self.cm.case(id=case.id)
        case.get()

        # run assertions on returned data
        assert case.name == __name__
        assert case.status == status
        assert case.severity == severity

        # cleanup case
        case.delete()

    def test_delete(self):
        """Test Case Deletion"""
        case = self.cm_helper.create_case(case_name=__name__)

        cases = self.cm.cases()
        cases.filter.name(TQL.Operator.EQ, __name__)
        for case in cases:
            if case.name == __name__:
                break
        else:
            # if this hit case was not deleted
            assert False

    def test_create_with_metadata(self):
        """Test Case Creation"""
        case_data = {
            'artifacts': {
                'asn4455': {'intel_type': 'indicator-ASN', 'type': 'ASN'},
                'asn5544': {'intel_type': 'indicator-ASN', 'type': 'ASN'},
            },
            'case_severity': 'Low',
            'case_status': 'Open',
            'notes': [f'A note for pytest test {__name__}'],
            'tags': [f'{__name__}-1', f'{__name__}-1'],
            'tasks': {'task-1': {'description': 'task description', 'status': 'Pending'}},
        }

        # create case
        case = self.cm.case(
            name=__name__,
            severity=case_data.get('case_severity'),
            status=case_data.get('case_status'),
        )

        # add artifacts
        for artifact, artifact_data in case_data.get('artifacts', {}).items():
            case.add_artifact(
                summary=artifact,
                intel_type=artifact_data.get('intel_type'),
                type=artifact_data.get('type'),
            )

        # add notes
        for note in case_data.get('notes', []):
            case.add_note(text=note)

        # add tags
        for tag in case_data.get('tags', []):
            case.add_tag(name=tag)

        # add task
        for task, task_data in case_data.get('tasks', {}).items():
            case.add_task(
                name=task, description=task_data.get('description'), status=task_data.get('status')
            )

        # submit case
        case.submit()

        # retrieve case for asserts
        case = self.cm.case(id=case.id)
        case.get(all_available_fields=True)

        # run assertions on returned data
        assert case.id
        assert case.name == __name__
        assert case.severity == case_data.get('case_severity')
        assert case.status == case_data.get('case_status')

        # assert len(case.artifacts) == 2
        for artifact in case.artifacts:
            assert artifact.summary in case_data.get('artifacts', [])
            # assert artifact.intel_type == 'indicator-ASN'
            assert artifact.type == 'ASN'

        # assert len(case.tags) == 2
        for tag in case.tags:
            assert tag.name in case_data.get('tags', [])

        # assert len(case.notes) == 1
        for note in case.notes:
            assert note.text in case_data.get('notes', [])

        # assert len(case.tasks) == 1
        for task in case.tasks:
            assert task.name in case_data.get('tasks', [])

        # cleanup case
        case.delete()

    def test_get_single_by_id(self):
        """Test Case get by ID"""
        # create case
        case = self.cm_helper.create_case(case_name=__name__)

        case = self.cm.case(id=case.id)
        case.get()

        # run assertions on returned data
        assert case.name == __name__

    def test_get_many(self):
        """Test Case get many"""
        # create cases
        self.cm_helper.create_case(case_name=f'{__name__}-1')
        self.cm_helper.create_case(case_name=f'{__name__}-2')

        # specifically match the count of the cases created.
        case_count = 0
        for case in self.cm.cases():
            if case.name.startswith(__name__):
                case_count += 1

        # run assertions on case count
        assert case_count == 2

    # def test_get_by_tql_filter_tag(self):
    #     """Test Artifact Get by TQL"""
    #     # create case
    #     case_data = {
    #         # 'artifacts': {'asn7777': {'intel_type': 'indicator-ASN', 'type': 'ASN'},},
    #         'case_name': __name__,
    #         'case_severity': 'Low',
    #         'case_status': 'Open',
    #         # 'notes': [f'A note for pytest test {__name__}'],
    #         # 'tags': [f'{__name__}-1', f'{__name__}-1'],
    #         # 'tasks': {'task-1': {'description': 'task description', 'status': 'Pending'}},
    #     }
    #     case = self.cm_helper.create_case(**case_data)

    #     # create artifact
    #     artifact_data = {
    #         'artifact_intel_type': 'indicator-ASN',
    #         'artifact_summary': 'asn7777',
    #         'artifact_type': 'ASN',
    #         'case_id': case.id,
    #     }
    #     artifact = self.cm_helper.create_artifact(**artifact_data)

    #     # retrieve cases using TQL
    #     cases = self.cm.cases()
    #     cases.filter.artifact(TQL.Operator.EQ, artifact.id)

    #     # assert len(cases.as_dict) == 1
    #     for case in cases:
    #         print(case)
    #         assert case.name == case_data.get('case_name')
