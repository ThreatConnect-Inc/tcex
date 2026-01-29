"""TcEx Framework Module"""


from collections.abc import Callable
from typing import Any

import pytest
from pytest import FixtureRequest

from tcex.api.tc.v3.security.assignee_model import AssigneeModel
from tcex.api.tc.v3.security.assignee_user_group_model import AssigneeUserGroupModel
from tcex.api.tc.v3.security.assignee_user_model import AssigneeUserModel
from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestCaseSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('cases')

    def setup_method(self, method: Callable):
        """Configure setup before all tests."""
        super().setup_method()

        # remove an previous cases with the next test case name as a tag
        cases = self.v3.cases()
        cases.filter.tag(TqlOperator.EQ, method.__name__)
        for case in cases:
            case.delete()

    def test_case_create(self):
        """Test snippet"""
        # Begin Snippet
        case = self.tcex.api.tc.v3.case(
            name='MyCase-0001',
            description='An example case description.',
            resolution='Not Specified',
            severity='Low',
            status='Open',
            xid='MyCase-0001',
        )

        case.create()
        # End Snippet

        # Add cleanup
        case.delete()

    def test_case_stage_artifact(self):
        """Test snippet"""
        # Begin Snippet
        case = self.tcex.api.tc.v3.case(
            name='MyCase-0002',
            description='An example case description.',
            severity='Low',
            status='Open',
            xid='MyCase-0002',
        )

        # Add artifact
        artifact = self.tcex.api.tc.v3.artifact(
            summary='asn999',
            type='ASN',
        )
        case.stage_artifact(artifact)

        case.create()
        # End Snippet

        # Add cleanup
        case.delete()

    def test_case_stage_attribute(self):
        """Test snippet"""
        # Begin Snippet
        case = self.tcex.api.tc.v3.case(
            name='MyCase-0003',
            description='An example case description.',
            severity='Low',
            status='Open',
            xid='MyCase-0003',
        )

        # Add attribute
        attribute = self.tcex.api.tc.v3.case_attribute(
            value='An example description attribute.',
            type='Description',
        )
        case.stage_attribute(attribute)

        case.create()
        # End Snippet

        # Add cleanup
        case.delete()

    def test_case_stage_note(self):
        """Test snippet"""
        # Begin Snippet
        case = self.tcex.api.tc.v3.case(
            name='MyCase-0004',
            description='An example case description.',
            severity='Low',
            status='Open',
            xid='MyCase-0004',
        )

        # Add note
        note = self.tcex.api.tc.v3.note(text='An example note.')
        case.stage_note(note)

        case.create()
        # End Snippet

        # Add cleanup
        case.delete()

    def test_case_stage_tag(self):
        """Test snippet"""
        # Begin Snippet
        case = self.tcex.api.tc.v3.case(
            name='MyCase-0005',
            description='An example case description.',
            severity='Low',
            status='Open',
            xid='MyCase-0005',
        )

        # Add tag
        tag = self.tcex.api.tc.v3.tag(name='Example-Tag')
        case.stage_tag(tag)

        case.create()
        # End Snippet

        # Add cleanup
        case.delete()

    def test_case_stage_task(self):
        """Test snippet"""
        # Begin Snippet
        case = self.tcex.api.tc.v3.case(
            name='MyCase-0006',
            description='An example case description.',
            severity='Low',
            status='Open',
            xid='MyCase-0006',
        )

        # Add task
        task = self.tcex.api.tc.v3.task(description='An example task description.', name='MyTask')
        case.stage_task(task)

        case.create()
        # End Snippet

        # Add cleanup
        case.delete()

    def test_case_delete_by_id(self):
        """Test snippet"""
        case = self.v3_helper.create_case()

        # Begin Snippet
        case = self.tcex.api.tc.v3.case(id=case.model.id)
        case.delete()
        # End Snippet

    def test_case_delete_by_name(self):
        """Test snippet"""
        case = self.v3_helper.create_case(name='MyCase-0007')

        # Begin Snippet
        cases = self.tcex.api.tc.v3.cases()
        cases.filter.name(TqlOperator.EQ, 'MyCase-0007')
        for case in cases:
            # IMPORTANT: this will delete all cases with the name "MyCase-0007"
            case.delete()
        # End Snippet

    def test_case_delete_artifact(self):
        """Test snippet"""
        case = self.v3_helper.create_case(
            name='MyCase-0007', artifacts={'type': 'ASN', 'summary': 'ASN1234'}
        )

        # Begin Snippet
        case = self.tcex.api.tc.v3.case(id=case.model.id)
        case.get(params={'fields': ['artifacts']})
        for artifact in case.artifacts:
            if artifact.model.summary == 'ASN1234':
                # IMPORTANT: this will delete all case artifacts with summary "ASN1234"
                artifact.delete()
        # End Snippet

    def test_case_delete_attribute(self):
        """Test snippet"""
        case = self.v3_helper.create_case(
            name='MyCase-0008',
            attributes={'type': 'Description', 'value': 'An Example Case Description'},
        )

        # Begin Snippet
        case = self.tcex.api.tc.v3.case(id=case.model.id)
        case.get(params={'fields': ['attributes']})
        for attribute in case.attributes:
            if attribute.model.value == 'An Example Case Description':
                # IMPORTANT: this will delete all attributes attached to the case
                # with value "An Example Case Description"
                attribute.delete()
        # End Snippet

    def test_case_delete_note(self):
        """Test snippet"""
        case = self.v3_helper.create_case(
            name='MyCase-0009',
            notes={'text': 'An Example Note'},
        )

        # Begin Snippet
        case = self.tcex.api.tc.v3.case(id=case.model.id)
        case.get(params={'fields': ['notes']})
        for note in case.notes:
            if note.model.text == 'An Example Note':
                # IMPORTANT: this will delete all notes attached to the case
                # with value "An Example Note"
                note.delete()
        # End Snippet

    def test_case_remove_tag(self):
        """Test snippet"""
        case = self.v3_helper.create_case(
            name='MyCase-10',
            tags=[
                {'name': 'Example-Tag'},
            ],
        )

        # Begin Snippet
        case = self.tcex.api.tc.v3.case(id=case.model.id)

        for tag in case.tags:
            if tag.model.name != 'Example-Tag':
                # IMPORTANT: on case management the submitted tags will replace any existing
                # tags on the case.
                case.stage_tag(tag.model)
        case.update()
        # End Snippet

    def test_case_delete_task(self):
        """Test snippet"""
        case = self.v3_helper.create_case(
            name='MyCase-11',
            task={
                'description': 'An Example Task Description',
                'name': 'MyTask',
            },
        )

        # Begin Snippet
        case = self.tcex.api.tc.v3.case(id=case.model.id)
        case.get(params={'fields': ['tasks']})
        for task in case.tasks:
            if task.model.name == 'MyTask':
                # IMPORTANT: this will delete all case tasks with value "MyTask"
                task.delete()
        # End Snippet

    def test_case_iterate(self):
        """Test snippet"""
        case = self.v3_helper.create_case(name='MyCase-12')

        # Begin Snippet
        for case in self.tcex.api.tc.v3.cases():
            print(case.model.model_dump(exclude_none=True))

    def test_case_get_by_name(self):
        """Test snippet"""
        case = self.v3_helper.create_case(name='MyCase-13')

        # Begin Snippet
        cases = self.tcex.api.tc.v3.cases()
        cases.filter.name(TqlOperator.EQ, 'MyCase-13')
        for case in cases:
            # IMPORTANT: this will return all cases with the name "MyCase-13"
            print(case.model.model_dump_json(exclude_none=True))
        # End Snippet

    def test_case_update(self):
        """Test snippet"""
        case = self.v3_helper.create_case(name='MyCase-14')

        # Begin Snippet
        case = self.tcex.api.tc.v3.case(id=case.model.id)
        case.model.name = 'MyUpdatedCase'
        case.update()
        # End Snippet

    @pytest.mark.parametrize(
        'user_id_org,user_id_new,user_or_group,assignee_type',
        [
            pytest.param(10, 11, 'User', dict, id='assignee-as-dict'),
            pytest.param(10, 11, 'User', AssigneeModel, id='assignee-as-model'),
            pytest.param(10, 11, 'User', AssigneeUserModel, id='assignee-as-user-model'),
            pytest.param(
                10, 11, 'Group', AssigneeUserGroupModel, id='assignee-as-user-group-model',
            ),
            pytest.param(10, 11, 'User', UserModel, id='assignee-as-user-only-model'),
            pytest.param(10, 11, 'Group', UserGroupModel, id='assignee-as-user-group-only-model'),
        ]
    )
    def test_case_update_with_assignee(
        self,
        user_id_org: int,
        user_id_new: int,
        user_or_group: str,
        assignee_type: Any,
        request: FixtureRequest
    ):
        """Test case for assignee"""
        case = self.v3_helper.create_case(
            name=request.node.name,
            assignee={'type': 'User', 'data': {'id': user_id_org}}
        )
        if not case.model.assignee:
            pytest.fail('Created case assignee not set')

        assert case.model.assignee.data, 'Created case assignee not set'

        if assignee_type == AssigneeModel:
            assignee = assignee_type(
                **{'type': user_or_group, 'data': {'id': user_id_new, 'user_name': 'blah'}}
            )  # type: ignore[assignment]
        else:
            assignee = assignee_type(**{'id': user_id_new, 'user_name': 'blah'})
        case.stage_assignee(type=user_or_group, data=assignee)
        case.update()

        case.get()
        assert case.model.assignee.data, 'Assignee not set'
        if case.model.assignee.data:
            assert case.model.assignee.data.id == user_id_new, 'Assignee ID not updated'
