"""Case Management PyTest Helper Method"""
# standard library
import importlib
import inspect
from random import randint
from typing import Any, Dict, Optional

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
        self.v3 = self.tcex.v3
        self.utils = Utils()

        # get v3 obj and obj collection (could append s for collection, but dict is cleaner)
        module_data = self._module_map(v3_object)
        self.v3_obj = self._import_model(module_data.get('module'), module_data.get('class_name'))
        self.v3_obj_collection = self._import_model(
            module_data.get('module'), module_data.get('collection_class_name')
        )

        # cleanup values
        self._v3_objects = []

    @staticmethod
    def _to_list(value: Any) -> list:
        """Wrap value in list if required."""
        if not isinstance(value, list):
            value = [value]
        return value

    def _import_model(self, module, class_name) -> Any:
        """Import the appropriate model."""
        # print(f'method=import_module, module={module}, class_name={class_name}')
        v3_class = getattr(importlib.import_module(module), class_name)
        # print(f'method=import_module, v3-class-type={type(v3_class)}')
        v3_obj = v3_class(session=self.tcex.session_tc)
        # print(f'method=import_module, v3-obj-type={type(v3_obj)}')
        return v3_obj

    @staticmethod
    def _module_map(module: str) -> Dict:
        """Return the module map data."""
        _modules = {
            'adversary_assets': {
                'module': 'tcex.api.tc.v3.adversary_assets.adversary_asset',
                'class_name': 'AdversaryAsset',
                'collection_class_name': 'AdversaryAssets',
            },
            'artifacts': {
                'module': 'tcex.api.tc.v3.artifacts.artifact',
                'class_name': 'Artifact',
                'collection_class_name': 'Artifacts',
            },
            'artifact_types': {
                'module': 'tcex.api.tc.v3.artifact_types.artifact_type',
                'class_name': 'ArtifactType',
                'collection_class_name': 'ArtifactTypes',
            },
            'cases': {
                'module': 'tcex.api.tc.v3.cases.case',
                'class_name': 'Case',
                'collection_class_name': 'Cases',
            },
            'groups': {
                'module': 'tcex.api.tc.v3.groups.group',
                'class_name': 'Group',
                'collection_class_name': 'Groups',
            },
            'indicators': {
                'module': 'tcex.api.tc.v3.indicators.indicator',
                'class_name': 'Indicator',
                'collection_class_name': 'Indicators',
            },
            'notes': {
                'module': 'tcex.api.tc.v3.notes.note',
                'class_name': 'Note',
                'collection_class_name': 'Notes',
            },
            'owner_roles': {
                'module': 'tcex.api.tc.v3.security.owner_roles.owner_role',
                'class_name': 'OwnerRole',
                'collection_class_name': 'OwnerRoles',
            },
            'owners': {
                'module': 'tcex.api.tc.v3.security.owners.owner',
                'class_name': 'Owner',
                'collection_class_name': 'Owners',
            },
            'security_labels': {
                'module': 'tcex.api.tc.v3.security_labels.security_label',
                'class_name': 'SecurityLabel',
                'collection_class_name': 'SecurityLabels',
            },
            'system_roles': {
                'module': 'tcex.api.tc.v3.security.system_roles.system_role',
                'class_name': 'SystemRole',
                'collection_class_name': 'SystemRoles',
            },
            'tags': {
                'module': 'tcex.api.tc.v3.tags.tag',
                'class_name': 'Tag',
                'collection_class_name': 'Tags',
            },
            'tasks': {
                'module': 'tcex.api.tc.v3.tasks.task',
                'class_name': 'Task',
                'collection_class_name': 'Tasks',
            },
            'users': {
                'module': 'tcex.api.tc.v3.security.users.user',
                'class_name': 'User',
                'collection_class_name': 'Users',
            },
            'user_groups': {
                'module': 'tcex.api.tc.v3.security.user_groups.user_group',
                'class_name': 'UserGroup',
                'collection_class_name': 'UserGroups',
            },
            'victims': {
                'module': 'tcex.api.tc.v3.victims.victim',
                'class_name': 'Victim',
                'collection_class_name': 'Victims',
            },
            'victim_assets': {
                'module': 'tcex.api.tc.v3.victim_assets.victim_asset',
                'class_name': 'VictimAsset',
                'collection_class_name': 'VictimAssets',
            },
            'workflow_events': {
                'module': 'tcex.api.tc.v3.workflow_events.workflow_event',
                'class_name': 'WorkflowEvent',
                'collection_class_name': 'WorkflowEvents',
            },
            'workflow_templates': {
                'module': 'tcex.api.tc.v3.workflow_templates.workflow_template',
                'class_name': 'WorkflowTemplate',
                'collection_class_name': 'WorkflowTemplates',
            },
        }
        return _modules.get(module)

    def create_case(self, **kwargs):
        """Create an case.

        If a case_name is not provide a dynamic case name will be used.

        Args:
            assignee (str, kwargs): Optional assignee.
            date_added (str, kwargs): Optional date_added.
            description (str, kwargs): Optional description.
            name (str, kwargs): Optional name.
            resolution (str, kwargs): Optional resolution.
            severity (str, kwargs): Optional severity.
            status (str, kwargs): Optional status.
            tags (dict|list, kwargs): Optional tags.
            xid (str, kwargs): Optional XID.

        Returns:
            CaseManagement.Case: A CM case object.
        """
        cases = self.v3.cases()
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
        tags = self._to_list(kwargs.get('tags', []))
        tasks = kwargs.get('tasks', {})

        # create case
        case = self.v3.case(**case_data)

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
        for tag in tags:
            case.add_tag(**tag)

        # add task
        for task, task_data in tasks.items():
            case.add_task(
                name=task, description=task_data.get('description'), status=task_data.get('status')
            )

        # submit object
        case.submit()

        # store case id for cleanup
        self._v3_objects.append(case)

        return case

    def create_group(self, type_: Optional[str] = 'Adversary', **kwargs):
        """Create a group.

        Args:
            active (bool, kwargs): Optional active bool.
            associated_groups (dict|list, kwargs): Optional group associations.
            associated_indicator (dict|list, kwargs): Optional indicator associations.
            attributes (dict|list, kwargs): Optional group attributes.
            name (str, kwargs): Optional name for the group.
            security_labels (dict|list, kwargs): Optional group security labels.
            source (str, kwargs): Optional source.
            tags (dict|list, kwargs): Optional tags.
            xid (str, kwargs): Optional XID.

        Returns:
            V3.Group: A group object.
        """
        group_data = {
            'name': kwargs.get('name', inspect.stack()[1].function),
            'type': type_,
            # 'xid': kwargs.get('xid', f'xid-{inspect.stack()[1].function}'),
        }
        # if kwargs.get('size') is not None:
        #     group_data['size'] = kwargs.get('size')
        # add source
        if kwargs.get('source') is not None:
            group_data['source'] = kwargs.get('source')

        # create indicator
        group = self.v3.group(**group_data)

        associated_groups = self._to_list(kwargs.get('associated_groups', []))
        associated_indicators = self._to_list(kwargs.get('associated_indicators', []))
        attributes = self._to_list(kwargs.get('attribute', []))
        security_labels = self._to_list(kwargs.get('security_labels', []))
        tags = self._to_list(kwargs.get('tags', []))

        # add associations
        for associated_group in associated_groups:
            group.add_associated_group(**associated_group)

        # add indicators
        for associated_indicator in associated_indicators:
            group.add_associated_indicator(**associated_indicator)

        # add attributes
        for attribute in attributes:
            group.add_attribute(**attribute)

        # add security labels
        for security_label in security_labels:
            group.add_security_label(**security_label)

        # add tags
        group.add_tag(name='pytest')
        for tag in tags:
            group.add_tag(**tag)

        # submit object
        group.submit()

        # store case id for cleanup
        self._v3_objects.append(group)

        return group

    def create_indicator(self, type_: Optional[str] = 'Address', **kwargs):
        """Create a indicator.

        Args:
            active (bool, kwargs): Optional active bool.
            associated_groups (dict|list, kwargs): Optional group associations.
            attributes (dict|list, kwargs): Optional indicator attributes.
            confidence (int, kwargs): Optional rating.
            rating (int, kwargs): Optional rating.
            security_labels (dict|list, kwargs): Optional indicator security labels.
            size (dict|list, kwargs): Optional indicator size for File indicators.
            source (str, kwargs): Optional source.
            tags (dict|list, kwargs): Optional tags.
            value_1 (str, kwargs): Optional indicator value 1.
            value_2 (str, kwargs): Optional indicator value 2.
            value_3 (str, kwargs): Optional indicator value 3.

        Returns:
            V3.Indicator: A indicator object.
        """
        value_1 = kwargs.get('value1', f'123.{randint(1,255)}.{randint(1,255)}.{randint(1,255)}')
        # indicators = self.v3.indicators()
        # indicators.filter.tag(TqlOperator.EQ, 'pytest')
        # for indicator in indicators:
        #     indicator.delete()

        def value_1_map():
            """Return the appropriate indicator field name."""
            value_1_mapping = {
                'Address': 'ip',
                'EmailAddress': 'address',
                'File': 'md5',
                'Host': 'hostName',
                'URL': 'text',
            }
            return value_1_mapping.get(type_, 'value1')

        def value_2_map():
            """Return the appropriate indicator field name."""
            value_1_mapping = {
                'File': 'sha1',
            }
            return value_1_mapping.get(type_, type_)

        def value_3_map():
            """Return the appropriate indicator field name."""
            value_1_mapping = {
                'File': 'sha256',
            }
            return value_1_mapping.get(type_, type_)

        indicator_data = {
            'active': kwargs.get('active', True),
            'confidence': kwargs.get('confidence', 0),
            'description': 'TcEx Testing',
            'ownerName': kwargs.get('ownerName'),
            'rating': kwargs.get('rating'),
            'type': type_,
        }
        # add "primary" indicator field
        indicator_data[value_1_map()] = value_1
        # add "secondary" indicator field
        if kwargs.get('value_2') is not None:
            indicator_data[value_2_map()] = value_1
        # add "tertiary" indicator field
        if kwargs.get('value_2') is not None:
            indicator_data[value_3_map()] = value_1
        # add size for file
        if kwargs.get('size') is not None:
            indicator_data['size'] = kwargs.get('size')
        # add source
        if kwargs.get('source') is not None:
            indicator_data['source'] = kwargs.get('source')

        # create indicator
        indicator = self.v3.indicator(**indicator_data)

        associated_groups = self._to_list(kwargs.get('associated_groups', []))
        attributes = self._to_list(kwargs.get('attribute', []))
        security_labels = self._to_list(kwargs.get('security_labels', []))
        tags = self._to_list(kwargs.get('tags', []))

        # add associations
        for associated_group in associated_groups:
            indicator.add_associated_group(**associated_group)

        # add attributes
        for attribute in attributes:
            indicator.add_attribute(**attribute)

        # add security labels
        for security_label in security_labels:
            indicator.add_security_label(**security_label)

        # add tags
        indicator.add_tag(name='pytest')
        for tag in tags:
            indicator.add_tag(**tag)

        # submit object
        indicator.submit()

        # store case id for cleanup
        self._v3_objects.append(indicator)

        return indicator

    def cleanup(self):
        """Remove all cases and child data."""
        # remove cases created by the create_case method
        for obj in self._v3_objects:
            try:
                obj.delete()
            except:
                pass

        # # delete cases by tag
        # if os.getenv('TCEX_CLEAN_CM'):
        #     cases = self.v3_obj.cases()
        #     cases.filter.tag(TqlOperator.EQ, 'pytest')
        #     for case in cases:
        #         case.delete()


class TestCaseManagement:
    """Test TcEx Case Management Base Class"""

    v3_helper = None
    tcex = None
    utils = Utils()

    def obj_api_options(self):
        """Test filter keywords.

        This is an API sanity check. Using the fields returned by the /fields API endpoint
        we can validate that they match the properties returned from the OPTIONS request.
        """
        for f in self.v3_helper.v3_obj.fields:
            # fields that are returned in OPT /v3/<obj>/filters endpoint, but not OPT /v3/<obj>
            if f.get('name') in [
                # case ignore
                'analytics',  # per MJ this is a special field that enables returning all analytics
                # group ignore
                'victimAssets',
                # indicator ignore
                'files',
                'fileAction',
                # Returns custom indicator fields as value1/value2/value3
                # instead of their custom names
                'genericCustomIndicatorValues',
                'groups',
                'indicators',
                'owner',
                'threatAssess',
            ]:
                continue

            if f.get('name') not in self.v3_helper.v3_obj.properties:
                assert (
                    False
                ), f'''{f.get('name')} not in {self.v3_helper.v3_obj.properties.keys()}'''

    def obj_filter_keywords(self):
        """Test filter keywords.

        This is an API sanity check. Using the options returned by the /tql API endpoint
        we can validate that the filter method provides all required filters for the object.
        """
        for keyword in self.v3_helper.v3_obj_collection.tql_keywords:
            # covert camel keyword from API to snake before comparing
            keyword = self.utils.camel_to_snake(keyword)
            if keyword not in self.v3_helper.v3_obj_collection.filter.implemented_keywords:
                assert False, f'Missing TQL keyword {keyword}.'

    def obj_properties(self):
        """Test properties.

        This is an API sanity check. Using the properties returned by the OPTIONS method on
        the API endpoint we can validate that the model has all required properties.
        """
        for prop_string in self.v3_helper.v3_obj.properties:
            assert prop_string in self.v3_helper.v3_obj.model.dict(
                by_alias=True
            ), f'Missing {prop_string} property'

    def obj_properties_extra(self):
        """Check to see if there are any additional properties in obj."""
        for prop in self.v3_helper.v3_obj.model.dict(by_alias=True):
            # Ignore extra properties
            # * id - not define, by API endpoint
            # * webLink - not define, by API endpoint (Core Issue)
            if prop in ['id', 'webLink']:
                continue
            assert prop in self.v3_helper.v3_obj.properties, f'Extra {prop} property.'
