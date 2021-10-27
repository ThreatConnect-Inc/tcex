"""Case Management PyTest Helper Method"""
# standard library
import inspect
import os

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.utils.utils import Utils
from tests.mock_app import MockApp


class V3Helper:
    """V3 API Helper Module

    Args:
        v3_object: The name of the object (e.g., artifact) being tested.
    """

    def __init__(self, v3_object: str) -> None:
        """Initialize Class Properties"""
        self.app = MockApp(runtime_level='Playbook')
        self.tcex = self.app.tcex
        self.cm = self.tcex.cm
        self.utils = Utils()

        # get the correct cm object
        collection_map = {
            'adversary_asset': 'adversary_assets',
            'artifact': 'artifacts',
            'artifact_type': 'artifact_types',
            'case': 'cases',
            'group': 'groups',
            'indicator': 'indicators',
            'note': 'notes',
            'owner': 'owners',
            'owner_role': 'owner_roles',
            'security_label': 'security_labels',
            'system_role': 'system_roles',
            'tag': 'tags',
            'task': 'tasks',
            'user': 'users',
            'user_group': 'user_groups',
            'victim': 'victims',
            'victim_asset': 'victim_assets',
            'workflow_event': 'workflow_events',
            'workflow_template': 'workflow_templates',
        }
        # get cm obj and obj collection (could append s for collection, but dict is cleaner)
        self.cm_obj = getattr(self.cm, v3_object)()
        self.cm_obj_collection = getattr(self.cm, collection_map.get(v3_object))()

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
        cases = self.cm.cases()
        xid = kwargs.get('xid', f'xid-{inspect.stack()[1].function}')
        cases.filter.xid(TqlOperator.EQ, xid)
        for case in cases:
            case.delete()

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
        # remove cases created by the create_case method
        for case in self.cases:
            case.delete()

        # delete cases by tag
        if os.getenv('TCEX_CLEAN_CM'):
            cases = self.cm.cases()
            cases.filter.tag(TqlOperator.EQ, 'pytest')
            for case in cases:
                case.delete()


class TestCaseManagement:
    """Test TcEx Case Management Base Class"""

    cm = None
    cm_helper = None
    tcex = None
    utils = Utils()

    def obj_api_options(self):
        """Test filter keywords.

        This is an API sanity check. Using the fields returned by the /fields API endpoint
        we can validate that they match the properties returned from the OPTIONS request.
        """
        for f in self.cm_helper.cm_obj.fields:
            # Ignore grouped fields - [synoptsis from conversation with MJ] - analytics
            # turns on more than one property, but is not a property itself.
            if f.get('name') in ['analytics']:
                continue

            if f.get('name') not in self.cm_helper.cm_obj.properties:
                assert (
                    False
                ), f'''{f.get('name')} not in {self.cm_helper.cm_obj.properties.keys()}'''

    def obj_filter_keywords(self):
        """Test filter keywords.

        This is an API sanity check. Using the options returned by the /tql API endpoint
        we can validate that the filter method provides all required filters for the object.
        """
        for keyword in self.cm_helper.cm_obj_collection.tql_keywords:
            # covert camel keyword from API to snake before comparing
            keyword = self.utils.camel_to_snake(keyword)
            if keyword not in self.cm_helper.cm_obj_collection.filter.implemented_keywords:
                assert False, f'Missing TQL keyword {keyword}.'

    def obj_properties(self):
        """Test properties.

        This is an API sanity check. Using the properties returned by the OPTIONS method on
        the API endpoint we can validate that the model has all required properties.
        """
        for prop_string in self.cm_helper.cm_obj.properties:
            assert prop_string in self.cm_helper.cm_obj.model.dict(
                by_alias=True
            ), f'Missing {prop_string} property'

    def obj_properties_extra(self):
        """Check to see if there are any additional properties in obj."""
        for prop in self.cm_helper.cm_obj.model.dict(by_alias=True):
            # [pydantic] - _privates_ does not show up in model using dict()/json(),
            # but it does show up in the model configuration
            if prop in ['_privates_', 'id']:
                continue
            assert prop in self.cm_helper.cm_obj.properties, f'Extra {prop} property.'
