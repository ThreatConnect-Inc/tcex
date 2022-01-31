"""Case Management PyTest Helper Method"""
# standard library
import importlib
import inspect
import os
from datetime import datetime
from random import randint
from typing import Any, Dict, Optional

# third-party
from pydantic import BaseModel

# first-party
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
            'attribute_types': {
                'module': 'tcex.api.tc.v3.attribute_types.attribute_type',
                'class_name': 'AttributeType',
                'collection_class_name': 'AttributeTypes',
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
            'case_attributes': {
                'module': 'tcex.api.tc.v3.case_attributes.case_attribute',
                'class_name': 'CaseAttribute',
                'collection_class_name': 'CaseAttributes',
            },
            'cases': {
                'module': 'tcex.api.tc.v3.cases.case',
                'class_name': 'Case',
                'collection_class_name': 'Cases',
            },
            'group_attributes': {
                'module': 'tcex.api.tc.v3.group_attributes.group_attribute',
                'class_name': 'GroupAttribute',
                'collection_class_name': 'GroupAttributes',
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
            'indicator_attributes': {
                'module': 'tcex.api.tc.v3.indicator_attributes.indicator_attribute',
                'class_name': 'IndicatorAttribute',
                'collection_class_name': 'IndicatorAttributes',
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
            'victim_attributes': {
                'module': 'tcex.api.tc.v3.victim_attributes.victim_attribute',
                'class_name': 'VictimAttribute',
                'collection_class_name': 'VictimAttributes',
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

    @staticmethod
    def assert_generator(model: 'BaseModel', object_name: str) -> None:
        """Print assert statements for the provided model.

        self.v3_helper.assert_generator(owner.model, 'owners')
        """
        for key, value in model:
            if isinstance(value, BaseModel):
                print('skipping nested model')
                continue

            if isinstance(value, str):
                value = f'\'{value}\''
            print(f'''{' ' * 8}assert {object_name}.model.{key} == {value}''')

    def tql_generator(self, model: 'BaseModel', object_name: str) -> None:
        """Print TQL filter.

        group.get(params={'fields': ['_all_']})
        self.v3_helper.tql_generator(group.model, 'groups')
        """

        def get_model_keyword(keyword: str):
            keyword_map = {
                # attribute are not consistent on tql filter and field name
                'displayed': 'default',
                # "type" is the id of the type, while type name is the name that is returned
                'type_name': 'type',
                # break "type" lookup since it is never returned
                'type': 'unknown',
            }
            return keyword_map.get(keyword, keyword)

        def get_value(keyword: str, value: str):
            """Return the appropriate value."""
            # format the value
            operator = 'EQ'

            if isinstance(value, datetime):
                value = '1 day ago'
                operator = 'GT'

            if isinstance(value, str):
                value = f'\'{value}\''

            if keyword == 'id':
                value = f'{object_name}.model.id'

            return operator, value

        print(f'''{'-' * 20} Field Values {'-' * 20}''')
        for key, value in model:
            if isinstance(value, BaseModel):
                continue
            print(f'''{key} == {value}''')

        # Generate TQL statements
        model_data = model.dict()
        tql_filters = {
            'found': [],
            'missing': [],
        }
        for keyword in self.v3_obj_collection.tql_keywords:
            keyword = self.utils.camel_to_snake(keyword)
            if keyword.startswith('has'):
                continue
            operator, value = get_value(keyword, model_data.get(get_model_keyword(keyword)))

            # print TQL filters
            tql_filter = f'''{object_name}.filter.{keyword}(TqlOperator.{operator}, {value})'''
            tql_filter_type = 'missing'
            if value is not None:
                tql_filter_type = 'found'
            # add the filter to the tql dict
            tql_filters[tql_filter_type].append(tql_filter)

        print(f'''{'-' * 20} Found TQL {'-' * 20}''')
        for found_tracker in tql_filters['found']:
            print(found_tracker)

        print(f'''{'-' * 20} Missing TQL {'-' * 20}''')
        for missing_tracker in tql_filters['missing']:
            print(missing_tracker)

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
        # Use the test case name in xid and to control delete
        test_case_name = inspect.stack()[1].function

        # create case
        case_data = {
            'assignee': kwargs.get('assignee'),
            'date_added': kwargs.get('date_added'),
            'description': kwargs.get('description', f'A description for {test_case_name}'),
            'name': kwargs.get('name', test_case_name),
            'resolution': kwargs.get('resolution', 'Not Specified'),
            'severity': kwargs.get('severity', 'Low'),
            'status': kwargs.get('status', 'Open'),
            'xid': kwargs.get('xid', f'xid-{test_case_name}').replace('_', '-'),
        }

        artifacts = self._to_list(kwargs.get('artifacts', []))
        attributes = self._to_list(kwargs.get('attributes', []))
        notes = self._to_list(kwargs.get('notes', []))
        tags = self._to_list(kwargs.get('tags', []))
        tasks = self._to_list(kwargs.get('tasks', []))

        # create case
        case = self.v3.case(**case_data)

        # add artifacts
        for artifact in artifacts:
            case.stage_artifact(self.v3.artifact(**artifact))

        # add attributes
        for attribute in attributes:
            case.stage_attribute(self.v3.case_attribute(**attribute))

        # add notes
        for note in notes:
            case.stage_note(self.v3.note(**note))

        # add tags
        case.stage_tag(self.v3.tag(name=test_case_name))
        for tag in tags:
            case.stage_tag(self.v3.tag(**tag))

        # add task
        for task in tasks:
            case.stage_task(self.v3.task(**task))

        # create object
        case.create()

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
            file_name (str, kwargs): Optional Document/Report file name.
            name (str, kwargs): Optional name for the group.
            security_labels (dict|list, kwargs): Optional group security labels.
            source (str, kwargs): Optional source.
            tags (dict|list, kwargs): Optional tags.
            xid (str, kwargs): Optional XID.

        Returns:
            V3.Group: A group object.
        """
        # Use the test case name in xid and to control delete
        test_case_name = inspect.stack()[1].function

        # use incoming name or test case name
        name = kwargs.get('name', test_case_name)

        # create group
        group_data = {
            'file_name': kwargs.get('file_name'),
            'name': name,
            'type': type_,
            'xid': kwargs.get('xid', f'xid-{test_case_name}'),
        }
        # add source
        if kwargs.get('source') is not None:
            group_data['source'] = kwargs.get('source')

        # create indicator
        group = self.v3.group(**group_data)

        associated_groups = self._to_list(kwargs.get('associated_groups', []))
        associated_indicators = self._to_list(kwargs.get('associated_indicators', []))
        attributes = self._to_list(kwargs.get('attributes', []))
        security_labels = self._to_list(kwargs.get('security_labels', []))
        tags = self._to_list(kwargs.get('tags', []))

        # add associations
        for associated_group in associated_groups:
            group.stage_associated_group(self.v3.group(**associated_group))

        # add indicators
        for associated_indicator in associated_indicators:
            group.stage_associated_indicator(self.v3.indicator(**associated_indicator))

        # add attributes
        for attribute in attributes:
            group.stage_attribute(self.v3.group_attribute(**attribute))

        # add security labels
        for security_label in security_labels:
            group.stage_security_label(self.v3.security_label(**security_label))

        # add tags
        group.stage_tag(self.v3.tag(name=test_case_name))
        for tag in tags:
            group.stage_tag(self.v3.tag(**tag))

        # create object
        group.create()

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
        # Use the test case name in xid and to control delete
        test_case_name = inspect.stack()[1].function

        # create indicator
        value_1 = kwargs.get('value1', f'123.{randint(1,255)}.{randint(1,255)}.{randint(1,255)}')

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
        attributes = self._to_list(kwargs.get('attributes', []))
        security_labels = self._to_list(kwargs.get('security_labels', []))
        tags = self._to_list(kwargs.get('tags', []))

        # add associations
        for associated_group in associated_groups:
            indicator.stage_associated_group(self.v3.group(**associated_group))

        # add attributes
        for attribute in attributes:
            indicator.stage_attribute(self.v3.indicator_attribute(**attribute))

        # add security labels
        for security_label in security_labels:
            indicator.stage_security_label(self.v3.security_label(**security_label))

        # add tags
        indicator.stage_tag(self.v3.tag(name=test_case_name))
        for tag in tags:
            indicator.stage_tag(self.v3.tag(**tag))

        # create object
        indicator.create()

        # store case id for cleanup
        self._v3_objects.append(indicator)

        return indicator

    def create_victim(self, **kwargs):
        """Create a group.

        Args:
            assets (VictimAssets, kwargs): A list of victim assets corresponding to the Victim.
            associated_groups (Groups, kwargs): A list of groups that this indicator is associated
                with.
            attributes (VictimAttributes, kwargs): A list of Attributes corresponding to the
                Victim.
            description (str, kwargs): The indicator description text.
            name (str, kwargs): Name of the Victim.
            nationality (str, kwargs): Nationality of the Victim.
            org (str, kwargs): Org of the Victim.
            id (int, kwargs): The ID of the Victim.
            owner_name (str, kwargs): The name of the Organization, Community, or Source that the
                item belongs to.
            security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
                Intel item (NOTE: Setting this parameter will replace any existing tag(s) with the
                one(s) specified).
            suborg (str, kwargs): Suborg of the Victim.
            tags (Tags, kwargs): A list of Tags corresponding to the item (NOTE: Setting this
                parameter will replace any existing tag(s) with the one(s) specified)
            work_location (str, kwargs): Work Location of the Victim.

        Returns:
            V3.Victim: A victim object.
        """
        # Use the test case name in xid and to control delete
        test_case_name = inspect.stack()[1].function

        # create victim
        victim_data = {
            'name': kwargs.get('name', test_case_name),
            'description': kwargs.get('description') or 'Example Victim Description',
            'nationality': kwargs.get('nationality') or 'American',
            'org': kwargs.get('org') or 'TCI',
            'owner_name': kwargs.get('owner_name') or 'TCI',
            'suborg': kwargs.get('suborg') or 'Example Sub Org',
            'work_location': kwargs.get('work_location') or 'Home',
        }

        # create indicator
        victim = self.v3.victim(**victim_data)

        # associated_groups = self._to_list(kwargs.get('associated_groups', []))
        attributes = self._to_list(kwargs.get('attributes', []))
        security_labels = self._to_list(kwargs.get('security_labels', []))
        tags = self._to_list(kwargs.get('tags', []))
        assets = self._to_list(kwargs.get('assets', []))

        # TODO: [low] @bpurdy - victims don't have direct associations?
        # add associations
        # for associated_group in associated_groups:
        #     victim.stage_associated_group(self.v3.group(**associated_group))

        # add attributes
        for attribute in attributes:
            victim.stage_attribute(self.v3.victim_attribute(**attribute))

        # add security labels
        for security_label in security_labels:
            victim.stage_security_label(self.v3.security_label(**security_label))

        # add assets
        for asset in assets:
            victim.stage_victim_asset(self.v3.victim_asset(**asset))

        # add tags
        victim.stage_tag(self.v3.tag(name=test_case_name))
        for tag in tags:
            victim.stage_tag(self.v3.tag(**tag))

        # create object
        victim.create()

        # store case id for cleanup
        self._v3_objects.append(victim)

        return victim

    def cleanup(self):
        """Remove all cases and child data."""
        # remove cases created by the create_case method
        for obj in self._v3_objects:
            try:
                obj.delete()
            except Exception:
                pass


class TestV3:
    """Test TcEx V3 Base Class"""

    v3_helper = None
    tcex = None
    utils = Utils()

    def teardown_method(self):
        """Clean up resources"""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.v3_helper.cleanup()

        # clean up monitor thread
        self.v3_helper.tcex.token.shutdown = True

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
            # convert camel keyword from API to snake before comparing
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
