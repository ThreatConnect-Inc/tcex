# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex
from tcex.case_management.tql import TQL


# pylint: disable=W0201
class TestCaseIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm

    def test_get_single(self):
        case = self.test_create('case_name', delete=False)
        self.test_create('case_name_2', delete=False)

        case = self.cm.case(id=case.id)
        case.get()
        assert case.name == 'case_name'

        self.test_delete('case_name', create=False)
        self.test_delete('case_name_2', create=False)

    def test_get_many(self):
        ...

    def test_tql(self):
        ...

    def test_delete(self, name='case_name', create=True):
        if create:
            self.test_create(name, delete=False)
        cases = self.cm.cases()
        cases.name_filter(TQL.Operator.EQ, name)
        for case in cases:
            case.delete()

    def test_create(self, name='case_name', status='Open', severity='Low', delete=True):
        case = self.cm.case(name=name, status=status, severity=severity)
        case.submit()

        assert case.name == name
        assert case.status == status
        assert case.severity == severity

        if delete:
            self.test_delete(name, create=False)

        return case

    def test_create_1(self):
        case = self.cm.case(name='case_1', status='Open', severity='Low')
        case.add_artifact(
            summary='Artifact Summary 1', type='Artifact 2', intel_type='indicator-ASN'
        )
        case.add_artifact(
            summary='Artifact Summary 2', type='Artifact 2', intel_type='indicator-ASN'
        )
        case.add_tag(name='New Tag 1')
        case.add_tag(name='New Tag 2')
        case.add_note(text='Note Text', summary='Note Summary')
        case.add_task(name='Task Name', description='Task Description', status='Pending')
        case.submit()

        assert case.id
        assert case.name == 'case_1'
        assert case.status == 'Open'
        assert case.severity == 'Low'

        assert len(case.artifacts) == 2
        for artifact in case.artifacts:
            assert artifact.summary in ['Artifact Summary 1', 'Artifact Summary 2']
            # assert artifact.intel_type == 'indicator-ASN'
            assert artifact.type == 'Artifact 2'

        assert len(case.tags) == 2
        for tag in case.tags:
            assert tag.name in ['New Tag 1', 'New Tag 2']

        assert len(case.notes) == 1
        for note in case.notes:
            assert note.text == 'Note Text'

        assert len(case.tasks) == 1
        for task in case.tasks:
            assert task.name == 'Task Name'
            assert task.description == 'Task Description'
            assert task.status == 'Pending'
