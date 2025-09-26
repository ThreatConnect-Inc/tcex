"""TcEx Framework Module"""


import os
from collections.abc import Callable
from datetime import datetime, timedelta
from random import randint


import pytest
from _pytest.fixtures import FixtureRequest


from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestCases(TestV3):
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

    def test_case_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_case_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_case_object_properties(self):
        """Test properties."""
        super().obj_properties()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_case_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_indicator_associations(self):
        """Test Case -> Indicator Associations"""

        self.v3_helper.tql_clear(['MyCase-19'], self.v3.cases(), 'name')

        indicator = self.v3.indicator(
            **{
                'ip': '43.24.65.37',
                'type': 'Address',
            }
        )
        indicator.create()
        indicator_2 = self.v3.indicator(
            **{
                'ip': '43.24.65.38',
                'type': 'Address',
            }
        )
        indicator_2.create()
        indicator_3 = {'ip': '43.24.65.39', 'type': 'Address'}

        # [Pre-Requisite] - create case
        case = self.v3.case(**{'name': 'MyCase-19', 'severity': 'Low', 'status': 'Open'})

        self.v3_helper._associations(case, indicator, indicator_2, indicator_3)

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_group_associations(self):
        """Test Case -> Group Associations"""
        # [Pre-Requisite] - clean up past runs.
        self.v3_helper.tql_clear(['MyCase-11'], self.v3.cases(), 'name')
        self.v3_helper.tql_clear(
            ['MyAdversary-13', 'StagedGroup-12', 'StagedGroup-13'], self.v3.groups()
        )

        case = self.v3.case(**{'name': 'MyCase-11', 'severity': 'Low', 'status': 'Open'})

        group_2 = self.v3_helper.create_group(name='StagedGroup-12', xid='staged_group_12-xid')
        group_3 = self.v3_helper.create_group(name='StagedGroup-13', xid='staged_group_13-xid')

        association_data = {'name': 'MyAdversary-13', 'type': 'Adversary'}

        self.v3_helper._associations(case, group_2, group_3, association_data)

    @pytest.mark.xfail(reason='Remove XFail once core fixes PLAT-4695')
    def test_case_associations(self):
        """Test Case -> Case Associations"""
        # [Pre-Requisite] - clean up past runs.
        self.v3_helper.tql_clear(
            ['MyCase-10', 'MyCase-11', 'MyCase-12', 'MyCase-13'], self.v3.cases(), 'name'
        )

        # [Pre-Requisite] - create cas
        case_2 = self.v3_helper.create_case(name='MyCase-10')
        case_3 = self.v3_helper.create_case(name='MyCase-11')

        # [Create Testing] define object data
        case = self.v3.case(**{'name': 'MyCase-12', 'severity': 'Low', 'status': 'Open'})

        association_data = {'name': 'MyCase-13', 'severity': 'Low', 'status': 'Open'}

        self.v3_helper._associations(case, case_2, case_3, association_data)

    def test_case_create_and_retrieve_nested_types(self, request: FixtureRequest):
        """Test Object Creation

        A single test case to hit all sub-type creation (e.g., Notes).
        """
        assignee = {'type': 'User', 'data': {'user_name': 'bpurdy@threatconnect.com'}}

        case_data = {
            'name': request.node.name,
            'description': f'A description for {request.node.name}',
            'owner': 'TCI',
            'resolution': 'Not Specified',
            'assignee': assignee,
            'severity': 'Low',
            'status': 'Open',
            'xid': self.xid(request),
        }

        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case(**case_data)

        # [Create Testing] define task data
        task_data = {
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
        }

        # [Create Testing] define artifact data
        artifact_data = {
            'summary': f'ASN{randint(100, 999)}',
            'type': 'ASN',
        }

        # [Create Testing] define artifact data
        attribute_data = {
            'source': 'Pytest',
            'type': 'Description',
            'value': 'Pytest value',
        }

        # [Create Testing] define tag
        tag_data = {
            'description': 'will this update the tags description',
            'name': 'Pytest',
        }

        # [Create Testing] define nested note data
        note_data = {'text': f'sample note for {request.node.name} test case.'}

        # [Create Testing] create the object object
        case.stage_tag(tag_data)

        # [Create Testing] create the object object
        case.stage_attribute(attribute_data)

        # [Create Testing] create the object object
        case.stage_task(task_data)

        # [Create Testing] add the note data to the object
        case.stage_note(note_data)

        # [Create Testing] add the artifact data to the object
        case.stage_artifact(artifact_data)

        # [Create Testing] update the object to the TC API
        case.update()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        case = self.v3.case(id=case.model.id)
        assert case.model.id is not None, 'Case ID is None.'

        # [Retrieve Testing] get the object from the API
        case.get(params={'fields': ['notes', 'artifacts', 'tasks', 'tags', 'attributes']})

        # [Retrieve Testing] test "notes" method
        notes = self.v3.notes()
        notes.filter.case_id(TqlOperator.EQ, case.model.id)
        assert len(notes) == 1, 'Note was not added/retrieved from case object.'
        for note in case.notes:
            # only a single note was added so text should match
            assert note.model.text == note_data.get('text')

        # [Retrieve Testing] run assertions on the nested note data, which
        # is only available due to params being added to the get() method.
        assert case.model.notes.data is not None, 'Notes data is None.'
        assert case.model.notes.data[0].text == note_data.get('text')

        # [Retrieve Testing] test "artifacts" method
        artifacts = self.v3.artifacts()
        artifacts.filter.case_id(TqlOperator.EQ, case.model.id)
        assert len(artifacts) == 1, 'Case was not added/retrieved from case object.'
        for artifact in case.artifacts:
            # only a single artifact was added so summary should match
            assert artifact.model.summary == artifact_data.get('summary')

        # [Retrieve Testing] run assertions on the nested artifact data, which
        # is only available due to params being added to the get() method.
        assert case.model.artifacts.data is not None, 'Artifacts data is None.'
        assert case.model.artifacts.data[0].summary == artifact_data.get('summary')

        # [Retrieve Testing] test "artifacts" method
        tasks = self.v3.tasks()
        tasks.filter.case_id(TqlOperator.EQ, case.model.id)
        assert len(tasks) == 1, 'Case was not added/retrieved from case object.'
        for task in case.tasks:
            # only a single artifact was added so summary should match
            assert task.model.name == task_data.get('name')

        # [Retrieve Testing] run assertions on the nested artifact data, which
        # is only available due to params being added to the get() method.
        assert case.model.tasks.data is not None, 'Artifacts data is None.'
        assert case.model.tasks.data[0].name == task_data.get('name')

        attributes_found = 0
        for attribute in case.attributes:
            attributes_found += 1
            assert attribute.model.type == attribute_data.get('type')
            assert attribute.model.source == attribute_data.get('source')
            # assert attribute.model.default == attribute_data.get('default')
            assert attribute.model.value == attribute_data.get('value')
        assert attributes_found == 1, f'Invalid amount of attributes {attributes_found} retrieved.'

        # [Retrieve Testing] run assertions on the nested artifact data, which
        assert case.model.assignee.type == assignee.get('type')
        assert case.model.assignee.data is not None, 'Assignee data is None.'
        # TODO: [low] - fix this assertion
        # assert case.model.assignee.data.user_name == assignee['data']['user_name']

        # [Retrieve Testing] run assertions on returned data
        assert case.as_entity == {'type': 'Case', 'id': case.model.id, 'value': case.model.name}
        assert case.model.name == case_data.get('name')
        assert case.model.description == case_data.get('description')
        assert case.model.owner == case_data.get('owner')
        assert case.model.resolution == case_data.get('resolution')
        assert case.model.severity == case_data.get('severity')
        assert case.model.status == case_data.get('status')
        # assert case.model.xid == case_data.get('xid')
        assert case.model.created_by.user_name == os.getenv('TC_API_ACCESS_ID')
        # variable
        assert case.model.case_open_user.user_name == os.getenv('TC_API_ACCESS_ID')
        # env variable

        # cleanup
        case.delete()

    def test_case_nested_objects(self, request: FixtureRequest):
        """Test nested objects on a Case"""
        # [Pre-Requisite] - create case with artifact data
        artifact_data = {
            'summary': f'ASN{randint(100, 999)}',
            'type': 'ASN',
        }
        case_data = {
            'name': request.node.name,
            'description': f'A description for {request.node.name}',
            'owner': 'TCI',
            'resolution': 'Not Specified',
            'artifacts': {'data': [artifact_data]},
            'attributes': {'data': [{'type': 'Description', 'value': 'Description 1'}]},
            'tags': {'data': [{'name': request.node.name}]},
            'severity': 'Low',
            'status': 'Open',
            'xid': self.xid(request),
        }
        case = self.tcex.api.tc.v3.case(**case_data)
        case.create()

        # [Retrieve Testing] Verify that the attribute was created.
        attributes_found = 0
        for attribute in case.attributes:
            attributes_found += 1
            assert attribute.model.value == 'Description 1'
        assert attributes_found == 1, 'No artifacts were created on the case'

        # This is not currently supported
        # case.update(mode='delete')
        # attributes_found = 0
        # for _ in case.attributes:
        #     attributes_found += 1
        # assert attributes_found == 0, 'Attributes were still found'

        # [Retrieve Testing] Verify that the artifact was created.
        artifacts_found = 0
        for artifact in case.artifacts:
            artifacts_found += 1
            assert artifact.model.summary == artifact_data.get('summary')
        assert artifacts_found == 1, 'No artifacts were created on the case'

        # [Retrieve Testing] Verify that the tag was created.
        tags_found = 0
        for tag in case.tags:
            tags_found += 1
            assert tag.model.name and tag.model.name.lower() in [request.node.name]
        assert tags_found == 1, 'No tags were created on the case'

        # [Stage Testing] Add a new tag to the Case
        case.stage_tag({'name': f'{request.node.name}-2'})
        case.update()

        # [Retrieve Testing] Verify that both tags exist now on the case.
        tags_found = 0
        for tag in case.tags:
            tags_found += 1
            assert tag.model.name and tag.model.name.lower() in [
                request.node.name,
                f'{request.node.name}-2',
            ]
        assert tags_found == 2, 'No tags were created on the case'

        # [Stage Testing] Refetch the case and stage a new tag on it.
        case = self.v3.case(id=case.model.id)
        case.stage_tag({'name': f'{request.node.name}-3'})
        case.update(mode='Replace')

        # [Retrieve Testing] Verify that only the 1 new tag gets re-added to the case, replacing
        # all other tags.
        tags_found = 0
        for tag in case.tags:
            tags_found += 1
            assert tag.model.name in [f'{request.node.name}-3']
        assert tags_found == 1, 'The existing tags were not replaced'

        # [Stage Testing] Stage another artifact onto the case.
        artifact_data_2 = {
            'summary': f'ASN{randint(100, 999)}',
            'type': 'ASN',
        }
        case.stage_artifact(artifact_data_2)
        case.update()

        # [Retrieve Testing] Verify that both artifacts exist under the case now.
        artifacts_found = 0
        for artifact in case.artifacts:
            artifacts_found += 1
            assert artifact.model.summary in [
                artifact_data.get('summary'),
                artifact_data_2.get('summary'),
            ]
        assert artifacts_found == 2, 'Incorrect amount of artifacts were created on the case.'

        # [Update Testing] Make no changes and resubmit the case, ensure that duplicate artifacts
        # are not created.
        case.update()

        # [Retrieve Testing] Verify that duplicate artifacts were not created
        artifacts_found = 0
        for _ in case.artifacts:
            artifacts_found += 1
        assert artifacts_found == 2, 'Incorrect amount of artifacts were created on the case.'

        # cleanup
        case.delete()

    def test_case_all_filters(self, request: FixtureRequest):
        """Test TQL Filters for case on a Case"""

        case_open_time = datetime.now() - timedelta(days=15)
        case_close_time = datetime.now() - timedelta(days=10)
        case_detection_time = datetime.now() - timedelta(days=15)
        case_occurrence_time = datetime.now() - timedelta(days=20)

        assignee = {'type': 'User', 'data': {'user_name': os.getenv('TC_API_ACCESS_ID')}}
        # assignee = {'type': 'Group', 'data': {'name': 'TcEx Testing'}}

        # [Create Testing] define case data
        case_data = {
            'name': request.node.name,
            'description': f'A description for {request.node.name}',
            'owner': 'TCI',
            'resolution': 'Not Specified',
            'severity': 'Low',
            'assignee': assignee,
            'status': 'Open',
            'case_open_time': case_open_time,
            'case_detection_time': case_detection_time,
            'case_occurrence_time': case_occurrence_time,
        }

        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case(**case_data)
        case.model.case_close_time = case_close_time
        case.model.status = 'Closed'

        # [Create Testing] define nested note data
        note_data = {'text': f'sample note for {request.node.name} test case.'}
        artifact_data = {
            'intel_type': 'indicator-ASN',
            'summary': f'ASN{randint(100, 999)}',
            'type': 'ASN',
        }
        # [Create Testing] define task data
        task_data = {
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
        }
        # [Create Testing] define artifact data
        attribute_data = {
            'source': 'Pytest',
            'type': 'Description',
            'value': 'Pytest value',
        }
        # [Create Testing] define tag
        tag_data = {
            'description': 'will this update the tags description',
            'name': 'Pytest',
        }

        # [Create Testing] create the object
        case = self.v3.case(**case_data)

        # [Create Testing] add the note data to the object
        case.stage_note(note_data)

        # [Create Testing] add the task data to the object
        case.stage_task(task_data)

        # [Create Testing] add the tag data to the object
        case.stage_tag(tag_data)

        # [Create Testing] add the attribute data to the object
        case.stage_attribute(attribute_data)

        # [Create Testing] add the artifact data to the object
        case.stage_artifact(artifact_data)

        # [Create Testing] create the object to the TC API
        case.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        case = self.v3.case(id=case.model.id)

        # [Retrieve Testing] get the object from the API
        case.get(params={'fields': ['_all_']})
        assert case.model.id is not None, 'id can not be none'
        assert case.model.owner is not None, 'owner can not be none'
        assert case.model.xid is not None, 'id can not be none'
        assert case.model.notes.data is not None, 'data can not be none'
        note_id = case.model.notes.data[0].id
        assert note_id is not None, 'id can not be none'
        assert case.model.tasks.data is not None, 'data can not be none'
        task_id = case.model.tasks.data[0].id
        assert task_id is not None, 'id can not be none'
        assert case.model.tags.data is not None, 'data can not be none'
        tag_id = case.model.tags.data[0].id
        assert tag_id is not None, 'id can not be none'
        # attribute_id = case.model.attributes.data[0].id
        assert case.model.artifacts.data is not None, 'data can not be none'
        artifact_id = case.model.artifacts.data[0].id
        assert artifact_id is not None, 'id can not be none'

        # [Retrieve Testing] retrieve object using tql filters
        cases = self.v3.cases()

        # [Filter Testing]
        cases.filter.assigned_to_user_or_group(TqlOperator.EQ, assignee['type'])
        # TODO: [PLAT-????] This is a filter type "Assignee". We currently do not have a Assignee
        #  filter object.
        # cases.filter.assignee_name(TqlOperator.EQ, assignee.get('data').get('user_name'))
        # cases.filter.attribute(...)
        # cases.filter.case_close_time(TqlOperator.GT, (case_close_time - timedelta(days=1)))
        # cases.filter.case_close_user(...)
        cases.filter.case_detection_time(TqlOperator.GT, (case_detection_time - timedelta(days=1)))
        # cases.filter.case_detection_user(...)
        cases.filter.case_occurrence_time(
            TqlOperator.GT, (case_occurrence_time - timedelta(days=1))
        )
        # cases.filter.case_occurrence_user(...)
        cases.filter.case_open_time(TqlOperator.GT, (case_open_time - timedelta(days=1)))
        # cases.filter.case_open_user(...)
        # cases.filter.created_by(...)
        # cases.filter.created_by_id(...)
        assert case.model.date_added is not None, 'date_added can not be none'
        cases.filter.date_added(TqlOperator.GT, (case.model.date_added - timedelta(days=1)))
        cases.filter.description(TqlOperator.EQ, case_data['description'])
        cases.filter.has_artifact.id(TqlOperator.EQ, artifact_id)
        # cases.filter.has_group.id(...)
        # cases.filter.has_indicator.id(...)
        cases.filter.has_note.id(TqlOperator.EQ, note_id)
        cases.filter.has_tag.id(TqlOperator.EQ, tag_id)
        cases.filter.has_task.id(TqlOperator.EQ, task_id)
        # cases.filter.has_workflow_template(...)
        cases.filter.id(TqlOperator.EQ, case.model.id)
        cases.filter.id_as_string(TqlOperator.EQ, str(case.model.id))
        cases.filter.name(TqlOperator.EQ, case_data['name'])
        # cases.filter.owner(...)
        cases.filter.owner_name(TqlOperator.EQ, case.model.owner)
        cases.filter.resolution(TqlOperator.EQ, case_data['resolution'])
        cases.filter.severity(TqlOperator.EQ, case_data['severity'])
        cases.filter.status(TqlOperator.EQ, case_data['status'])
        # cases.filter.tag(...)
        # cases.filter.target_id(...)
        # cases.filter.target_type(...)
        # cases.filter.typename(...)
        cases.filter.xid(TqlOperator.EQ, case.model.xid)
        for case in cases:
            assert case.model.name == case_data['name']
            break
        else:
            assert False, f'No case found for tql -> {cases.tql.as_str}'

        # cleanup
        case.delete()

    def test_case_get_by_tql_filter_fail_tql(self):
        """Test Case Get by TQL"""
        # retrieve object using TQL
        cases = self.v3.cases()
        cases.filter.tql = 'Invalid TQL'

        # [Fail Testing] assert RuntimeError is raised and error message contains the correct code.
        with pytest.raises(RuntimeError, match='950'):
            for _ in cases:
                pass

        # check status code
        assert cases.request.status_code == 400

    def test_case_delete_by_id(self):
        """Test Case Deletion"""
        # [Pre-Requisite] - create case and provide a unique xid
        case = self.v3_helper.create_case()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        case = self.v3.case(id=case.model.id)

        # [Delete Testing] remove the object
        case.delete()

        # [Delete Testing] assert RuntimeError is raised and
        #     error message contains the correct code.
        with pytest.raises(RuntimeError, match='952'):
            case.get()

    # def test_case_get_many(self):
    #     """Test Case Get Many"""
    #     # [Pre-Requisite] - create case
    #     case = self.v3_helper.create_case()
    #     case_count = 10
    #     case_ids = []
    #     for _ in range(0, case_count):
    #         # [Create Testing] define case data
    #         case_data = {
    #             'case_id': case.model.id,
    #             'description': 'a description from pytest test',
    #             'name': f'name-{randint(100, 999)}',
    #         }
    #
    #         # [Create Testing] create the object
    #         case = self.v3.case(**case_data)
    #
    #         # [Create Testing] create the object to the TC API
    #         case.create()
    #         case_ids.append(case.model.id)
    #
    #     # [Retrieve Testing] iterate over all object looking for needle
    #     cases = self.v3.cases(params={'resultLimit': 5})
    #     cases.filter.case_id(TqlOperator.EQ, case.model.id)
    #     for case in cases:
    #         assert case.model.id in case_ids
    #         case_ids.remove(case.model.id)
    #
    #     assert len(cases) == case_count
    #     assert not case_ids, 'Not all cases were returned.'
    #
    # def test_case_get_single_by_id_properties(self, request: FixtureRequest):
    #     """Test Case get single attached to case by id"""
    #     # [Pre-Requisite] - create case
    #     case = self.v3_helper.create_case()
    #
    #     # [Pre-Requisite] - create a case which the main case is dependent on
    #     case_data = {
    #         'case_id': case.model.id,
    #         'description': 'a description from pytest test',
    #         'name': 'name-depended_case',
    #         'workflow_phase': 0,
    #         'workflow_step': 1,
    #     }
    #     case_2 = self.v3.case(**case_data)
    #     case_2.create()
    #
    #     # [Pre-Requisite] - construct some timestamps in the future
    #     #    for completed and due by fields.
    #     future_1 = datetime.now() + timedelta(days=10)
    #     future_2 = datetime.now() + timedelta(days=5)
    #
    #     # [Pre-Requisite] construct the artifacts model
    #     artifact_count = 10
    #     artifact_summaries = []
    #     artifact_data = {'data': []}
    #     for _ in range(0, artifact_count):
    #         # [Pre-Requisite] define artifact data
    #         summary = f'ASN{randint(100, 999)}'
    #         artifact_data.get('data').append(
    #             {
    #                 'intel_type': 'indicator-ASN',
    #                 'summary': summary,
    #                 'type': 'ASN',
    #                 'note_text': 'artifact note text',
    #             }
    #         )
    #         artifact_summaries.append(summary)
    #
    #     # [Pre-Requisite] construct the notes model
    #     note_count = 10
    #     notes_text = []
    #     note_data = {'data': []}
    #     for _ in range(0, note_count):
    #         # [Pre-Requisite] define note data
    #         text = f'sample note generated: {time.time()} for {request.node.name} test case.'
    #         note_data.get('data').append({'text': text})
    #
    #         notes_text.append(text)
    #
    #     assignee = {'type': 'User', 'data': {'userName': 'bpurdy@threatconnect.com'}}
    #     # [Create Testing] define case data
    #     case_data = {
    #         'case_id': case.model.id,
    #         'artifacts': artifact_data,
    #         'assignee': assignee,
    #         'completed_date': future_2,
    #         'dependent_on_id': case_2.model.id,
    #         'description': f'a description from {request.node.name}',
    #         'due_date': future_1,
    #         'name': f'name-{request.node.name}',
    #         'notes': note_data,
    #         'status': 'Pending',  # It is always pending because of the depended on case
    #         'required': False,
    #         'workflow_phase': 0,
    #     }
    #
    #     # [Create Testing] add the note data to the object
    #     case = self.v3.case()
    #
    #     # [Create Testing] testing setters on model
    #     case.model.artifacts = case_data.get('artifacts')
    #     case.model.assignee = case_data.get('assignee')
    #     case.model.case_id = case_data.get('case_id')
    #     case.model.dependent_on_id = case_data.get('dependent_on_id')
    #     case.model.description = case_data.get('description')
    #     case.model.due_date = case_data.get('due_date')
    #     case.model.completed_date = case_data.get('completed_date')
    #     case.model.name = case_data.get('name')
    #     case.model.notes = case_data.get('notes')
    #     case.model.required = case_data.get('required')
    #     case.model.status = case_data.get('status')
    #     case.model.workflow_phase = case_data.get('workflow_phase')
    #
    #     # [Create Testing] create the object to the TC API
    #     case.create()
    #
    #     # [Retrieve Testing] create the object with id filter,
    #     # using object id from the object created above
    #     case = self.v3.case(id=case.model.id)
    #
    #     # [Retrieve Testing] get the object from the API
    #     case.get(params={'fields': ['_all_']})
    #
    #     # [Retrieve Testing] run assertions on returned data
    #     assert case.model.case_id == case.model.id
    #     assert case.model.name == case_data.get('name')
    #     assert case.model.required == case_data.get('required')
    #     assert case.model.status == case_data.get('status')
    #     assert case.model.workflow_phase == case_data.get('workflow_phase')
    #     assert case.model.assignee.type == assignee.get('type')
    #     assert case.model.assignee.data.user_name == assignee.get('data').get('user_name')
    #     for note in case.model.notes.data:
    #         assert note.text in notes_text
    #         notes_text.remove(note.text)
    #     assert not notes_text, 'Incorrect amount of notes were retrieved'
    #     for artifact in case.model.artifacts.data:
    #         assert artifact.summary in artifact_summaries
    #         artifact_summaries.remove(artifact.summary)
    #     assert not artifact_summaries, 'Incorrect amount of artifacts were retrieved'
    #
    # def test_case_update_properties(self, request: FixtureRequest):
    #     """Test updating artifacts properties"""
    #     # [Pre-Requisite] - create case
    #     case = self.v3_helper.create_case()
    #
    #     # [Pre-Requisite] define assignee data
    #     assignee = {'type': 'User', 'data': {'user_name': 'bpurdy@threatconnect.com'}}
    #
    #     # [Pre-Requisite] - create a case which the main case is dependent on
    #     case_data = {
    #         'assignee': assignee,
    #         'case_id': case.model.id,
    #         'description': 'a description from pytest test',
    #         'name': 'name-depended_case',
    #     }
    #     case = self.v3.case(**case_data)
    #     case.create()
    #
    #     # This was tested locally since no Groups are on the system by default
    #     assignee = {'type': 'Group', 'data': {'name': 'temp_user_group'}}
    #
    #     # [Update Testing] update object properties
    #     case_data = {
    #         # 'assignee': assignee,
    #         'description': f'a description from {request.node.name}',
    #         'name': f'name-{request.node.name}',
    #     }
    #
    #     # case.model.assignee = assignee
    #     case.model.description = case_data.get('description')
    #     case.model.name = case_data.get('name')
    #
    #     # [Update Testing] update the object to the TC API
    #     case.update()
    #
    #     # [Retrieve Testing] get the object from the API
    #     case.get(params={'fields': ['_all_']})
    #
    #     # [Retrieve Testing] run assertions on returned data
    #     # assert case.model.assignee.type == assignee.get('type')
    #     # assert case.model.assignee.data.name == assignee.get('data').get('name')
    #     assert case.model.description == case_data.get('description')
    #     assert case.model.name == case_data.get('name')
