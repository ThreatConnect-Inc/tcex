"""Case Management PyTest Helper Method"""
# standard library
import inspect
import os

from ..mock_app import MockApp


class CMHelper:
    """Case Management Helper Module

    Args:
        cm_object (str): The name of the object (e.g., artifact) being tested.
    """

    def __init__(self, cm_object):
        """Initialize Class Properties"""
        self.app = MockApp(runtime_level='Playbook')
        self.tcex = self.app.tcex
        self.cm = self.tcex.cm

        # get the correct cm object
        collection_map = {
            'artifact': 'artifacts',
            'artifact_type': 'artifact_types',
            'case': 'cases',
            'note': 'notes',
            'tag': 'tags',
            'task': 'tasks',
            'workflow_event': 'workflow_events',
            'workflow_template': 'workflow_templates',
        }
        # get cm obj and obj collection (could append s for collection, but dict is cleaner)
        self.cm_obj = getattr(self.cm, cm_object)()
        self.cm_obj_collection = getattr(self.cm, collection_map.get(cm_object))()

        # cleanup values
        self.cases = []

    def create_case(self, **kwargs):
        """Create an case.

        If a case_name is not provide a dynamic case name will be used.

        Args:
            assignee (str, kwargs): Optional assignee.
            date_added (str, kwargs): Optional date_added.
            description (str, kwargs): Optional description.
            name (str, kwargs): Optional case name.
            resolution (str, kwargs): Optional case resolution.
            severity (str, kwargs): Optional case severity.
            status (str, kwargs): Optional case status.
            tags (dict|list, kwargs): Optional case tags.
            xid (str, kwargs): Optional case XID.

        Returns:
            CaseManagement.Case: A CM case object.
        """
        case_data = {
            'assignee': kwargs.get('assignee'),
            'date_added': kwargs.get('date_added'),
            'description': kwargs.get(
                'description', f'A description for {inspect.stack()[1].function}'
            ),
            'name': kwargs.get('name', inspect.stack()[1].function),
            'resolution': kwargs.get('resolution', 'Not Specified'),
            'severity': kwargs.get('severity', 'Low'),
            'status': kwargs.get('status', 'Open'),
            'xid': kwargs.get('xid', f'xid-{inspect.stack()[1].function}'),
        }

        artifacts = kwargs.get('artifacts', {})
        notes = kwargs.get('notes', [])
        tags = kwargs.get('tags', [])
        tasks = kwargs.get('tasks', {})

        # create case
        case = self.cm.case(**case_data)

        # add artifacts
        for artifact, artifact_data in artifacts.items():
            case.add_artifact(
                summary=artifact,
                intel_type=artifact_data.get('intel_type'),
                type=artifact_data.get('type'),
            )

        # add notes
        for note in notes:
            case.add_note(text=note)

        # add tags
        case.add_tag(name='pytest')
        if isinstance(tags, dict):
            tags = [tags]
        for tag in tags:
            case.add_tag(**tag)

        # add task
        for task, task_data in tasks.items():
            case.add_task(
                name=task, description=task_data.get('description'), status=task_data.get('status')
            )

        # submit task
        case.submit()

        # store case id for cleanup
        self.cases.append(case)

        return case

    def cleanup(self):
        """Remove all cases and child data."""
        for case in self.cases:
            case.delete()

        # delete by tag
        if os.getenv('TCEX_CLEAN_CM'):
            # first-party
            from tcex.case_management.tql import TQL

            cases = self.cm.cases()
            cases.filter.tag(TQL.Operator.EQ, 'pytest')
            for case in cases:
                case.delete()

        # delete by name starts with

        # cases = self.cm.cases()
        # for case in cases:
        #     if case.name.startswith('tests.case_man'):
        #         case.delete(


class TestCaseManagement:
    """Test TcEx Case Management Base Class"""

    cm = None
    cm_helper = None
    tcex = None

    def obj_api_options(self):
        """Test filter keywords."""
        for f in self.cm_helper.cm_obj.fields:
            if f.get('name') not in self.cm_helper.cm_obj.properties:
                assert False, f"{f.get('name')} not in {self.cm_helper.cm_obj.properties.keys()}"

    def obj_code_gen(self):
        """Generate code and docstring from Options methods.

        This is not truly a test case, but best place to store it for now.
        """
        doc_string = self.cm_helper.cm_obj._doc_string
        filter_map = self.cm_helper.cm_obj_collection._filter_map_method
        filter_class = self.cm_helper.cm_obj_collection._filter_class

        return doc_string, filter_map, filter_class

    def obj_filter_keywords(self):
        """Test filter keywords."""
        for keyword in self.cm_helper.cm_obj_collection.filter.keywords:
            # covert camel keyword from API to snake before comparing
            keyword = self.tcex.utils.camel_to_snake(keyword)
            if keyword not in self.cm_helper.cm_obj_collection.filter.implemented_keywords:
                assert False, f'Missing TQL keyword {keyword}.'

    def obj_properties(self):
        """Test properties."""
        for prop_string, prop_data in self.cm_helper.cm_obj.properties.items():
            prop_read_only = prop_data.get('read-only', False)
            prop_string = self.cm_helper.tcex.utils.camel_to_snake(prop_string)

            # ensure class has property
            assert hasattr(
                self.cm_helper.cm_obj, prop_string
            ), f'Missing {prop_string} property. read-only: {prop_read_only}'

    def obj_properties_extra(self):
        """Check to see if there are any additional properties in obj."""

        for prop in self.cm_helper.cm_obj.implemented_properties:
            prop_camel = self.tcex.utils.snake_to_camel(prop)

            # handle additional properties
            if prop in ['id']:
                continue

            # ensure class has property
            assert prop_camel in self.cm_helper.cm_obj.properties, f'Extra {prop} property.'
