"""Test the TcEx API Snippets."""
# third-party
import pytest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


@pytest.mark.xdist_group(name='case-snippets')
class TestCaseSnippets(TestV3):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self, method: callable):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('cases')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

        # remove an previous cases with the next test case name as a tag
        cases = self.v3.cases()
        cases.filter.tag(TqlOperator.EQ, method.__name__)
        for case in cases:
            case.delete()

    def test_case_create(self):
        """Test snippet"""
        # Begin Snippet
        case = self.tcex.v3.case(
            name='MyCase',
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
        case = self.tcex.v3.case(
            name='MyCase',
            description='An example case description.',
            severity='Low',
            status='Open',
            xid='MyCase-0001',
        )

        # Add artifact
        artifact = self.tcex.v3.artifact(
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
        case = self.tcex.v3.case(
            name='MyCase',
            description='An example case description.',
            severity='Low',
            status='Open',
            xid='MyCase-0001',
        )

        # Add attribute
        attribute = self.tcex.v3.case_attribute(
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
        case = self.tcex.v3.case(
            name='MyCase',
            description='An example case description.',
            severity='Low',
            status='Open',
            xid='MyCase-0001',
        )

        # Add note
        note = self.tcex.v3.note(text='An example note.')
        case.stage_note(note)

        case.create()
        # End Snippet

        # Add cleanup
        case.delete()

    def test_case_stage_tag(self):
        """Test snippet"""
        # Begin Snippet
        case = self.tcex.v3.case(
            name='MyCase',
            description='An example case description.',
            severity='Low',
            status='Open',
            xid='MyCase-0001',
        )

        # Add tag
        tag = self.tcex.v3.tag(name='Example-Tag')
        case.stage_tag(tag)

        case.create()
        # End Snippet

        # Add cleanup
        case.delete()

    def test_case_stage_task(self):
        """Test snippet"""
        # Begin Snippet
        case = self.tcex.v3.case(
            name='MyCase',
            description='An example case description.',
            severity='Low',
            status='Open',
            xid='MyCase-0001',
        )

        # Add task
        task = self.tcex.v3.task(description='An example task description.', name='MyTask')
        case.stage_task(task)

        case.create()
        # End Snippet

        # Add cleanup
        case.delete()

    def test_case_delete_by_id(self):
        """Test snippet"""
        case = self.v3_helper.create_case()

        # Begin Snippet
        case = self.tcex.v3.case(id=case.model.id)
        case.delete()
        # End Snippet

    def test_case_delete_by_name(self):
        """Test snippet"""
        case = self.v3_helper.create_case(name='MyCase')

        # Begin Snippet
        cases = self.tcex.v3.cases()
        cases.filter.name(TqlOperator.EQ, 'MyCase')
        for case in cases:
            # IMPORTANT: this will delete all cases with the name "MyCase"
            case.delete()
        # End Snippet

    def test_case_delete_artifact(self):
        """Test snippet"""
        case = self.v3_helper.create_case(
            name='MyCase', artifacts={'type': 'ASN', 'summary': 'ASN1234'}
        )

        # Begin Snippet
        case = self.tcex.v3.case(id=case.model.id)
        case.get(params={'fields': ['artifacts']})
        for artifact in case.artifacts:
            if artifact.model.summary == 'ASN1234':
                # IMPORTANT: this will delete all case artifacts with summary "ASN1234"
                artifact.delete()
        # End Snippet

    def test_case_delete_attribute(self):
        """Test snippet"""
        case = self.v3_helper.create_case(
            name='MyCase',
            attributes={'type': 'Description', 'value': 'An Example Case Description'},
        )

        # Begin Snippet
        case = self.tcex.v3.case(id=case.model.id)
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
            name='MyCase',
            notes={'text': 'An Example Note'},
        )

        # Begin Snippet
        case = self.tcex.v3.case(id=case.model.id)
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
            name='MyCase',
            tags=[
                {'name': 'Example-Tag'},
            ],
        )

        # Begin Snippet
        case = self.tcex.v3.case(id=case.model.id)

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
            name='MyCase',
            task={
                'description': 'An Example Task Description',
                'name': 'MyTask',
            },
        )

        # Begin Snippet
        case = self.tcex.v3.case(id=case.model.id)
        case.get(params={'fields': ['tasks']})
        for task in case.tasks:
            if task.model.name == 'MyTask':
                # IMPORTANT: this will delete all case tasks with value "MyTask"
                task.delete()
        # End Snippet

    def test_case_iterate(self):
        """Test snippet"""
        case = self.v3_helper.create_case(name='MyCase')

        # Begin Snippet
        for case in self.tcex.v3.cases():
            print(case.model.dict(exclude_none=True))

    def test_case_get_by_name(self):
        """Test snippet"""
        case = self.v3_helper.create_case(name='MyCase')

        # Begin Snippet
        cases = self.tcex.v3.cases()
        cases.filter.name(TqlOperator.EQ, 'MyCase')
        for case in cases:
            # IMPORTANT: this will return all cases with the name "MyCase"
            print(case.model.json(exclude_none=True))
        # End Snippet

    def test_case_update(self):
        """Test snippet"""
        case = self.v3_helper.create_case(name='MyCase')

        # Begin Snippet
        case = self.tcex.v3.case(id=case.model.id)
        case.model.name = 'MyUpdatedCase'
        case.update()
        # End Snippet
