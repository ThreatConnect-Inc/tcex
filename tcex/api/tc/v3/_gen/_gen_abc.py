"""TcEx Framework Module"""

# standard library
import json
import os
from abc import ABC
from collections.abc import Generator
from pathlib import Path
from textwrap import TextWrapper

# third-party
from pydantic import ValidationError
from requests import Session
from requests.exceptions import ProxyError

# first-party
from tcex.api.tc.v3._gen.model import PropertyModel
from tcex.input.field_type.sensitive import Sensitive
from tcex.pleb.cached_property import cached_property
from tcex.requests_tc.auth.hmac_auth import HmacAuth
from tcex.util import Util
from tcex.util.render.render import Render
from tcex.util.string_operation import SnakeString


class GenerateABC(ABC):
    """Generate Abstract Base Class"""

    def __init__(self, type_: SnakeString):
        """Initialize instance properties."""
        self.type_ = type_

        # properties
        self._api_server = os.getenv('TC_API_PATH')
        self.api_url: str
        self.i1 = ' ' * 4  # indent level 1
        self.i2 = ' ' * 8  # indent level 2
        self.i3 = ' ' * 12  # indent level 3
        self.i4 = ' ' * 16  # indent level 4
        self.i5 = ' ' * 20  # indent level 5
        self.messages = []
        self.requirements = {}
        self.util = Util()

    @staticmethod
    def _format_description(arg: str, description: str, length: int, indent: str) -> str:
        """Format description for field."""
        # fix descriptions coming from core API endpoint
        if description[-1] not in ('.', '?', '!'):
            description += '.'

        line = f'{arg}: {description}'
        textwrapper = TextWrapper(
            subsequent_indent=indent + '    ',
            width=length - len(indent),
            expand_tabs=True,
            tabsize=len(indent),
            break_long_words=False,
        )
        return '\n'.join(textwrapper.wrap(line))

    def _type_map(self, type_):
        """Return modified type."""
        # special handling of attributes
        if type_ == 'attributes' and self.type_ == 'cases':
            type_ = 'case_attributes'
        elif type_ == 'attributes' and self.type_ == 'groups':
            type_ = 'group_attributes'
        elif type_ == 'attributes' and self.type_ == 'indicators':
            type_ = 'indicator_attributes'
        elif type_ == 'attributes' and self.type_ == 'victims':
            type_ = 'victim_attributes'
        return self.util.snake_string(type_)

    def _module_import_data(self, type_: SnakeString) -> dict[str, str]:
        """Return the model module map data.

        This method provides the logic to build the import module and class dynamically. Using
        the provided type value (e.g., cases, groups, victim_attributes) the module
        (tcex.api.tc.v3.groups.group_filter) and the class (GroupFilter) are returned.

        filter -> the filter Class (CaseFilter)
        model  -> the model and model collection Classes (CaseModel, CasesModel)
        object -> the object and object collection Classes (Case, Cases)
        """
        type_ = self._type_map(type_)

        _base_path = f'{self.tap(type_)}.{type_}'
        return {
            'filter_module': f'{_base_path}.{type_.singular()}_filter',
            'filter_class': f'{type_.pascal_case()}Filter',
            'model_module': f'{_base_path}.{type_.singular()}_model',
            'model_class': f'{type_.singular().pascal_case()}Model',
            'model_collection_class': f'{type_.plural().pascal_case()}Model',
            'object_module': f'{_base_path}.{type_.singular()}',
            'object_class': f'{type_.singular().pascal_case()}',
            'object_collection_class': f'{type_.plural().pascal_case()}',
        }

    @cached_property
    def _prop_contents(self) -> dict:
        """Return defined API endpoint properties for the current type."""
        _properties = {}
        try:
            r = self.session.options(self.api_url, params={'show': 'readOnly'})
            # print(r.request.method, r.request.url, r.text)
            if r.ok:
                _properties = r.json()

                options_data = Path('tcex/api/tc/v3/_gen/options_data')
                options_data.mkdir(parents=True, exist_ok=True)
                options_data = options_data / f'{self.type_}.json'
                with options_data.open(mode='w') as fh:
                    json.dump(r.json(), fh, indent=2)

        except (ConnectionError, ProxyError) as ex:
            Render.panel.failure(f'Failed getting types properties ({ex}).')

        return _properties

    def _prop_contents_data(self, properties: dict) -> Generator:
        """Yield the appropriate data object.

        artifacts": {
            "data": [
                {
                    "description": "a list of Artifacts corresponding to the Case",
                    "type": "Artifact"
                }
            ]
        },
        "assignee": {
            "description": "the user or group Assignee object for the Case",
            "type": "Assignee"
        },
        "attributeTypeMappings": [
            {
                "description": "the mapping of attribute types allowed for indicator types",
                "type": "AttributeTypeMappingApiInt"
            }
        ],
        """
        for field_name, field_data in sorted(properties.items()):
            if isinstance(field_data, dict):
                if 'data' in field_data and isinstance(field_data['data'], list):
                    # some properties have a data key with an array of items.
                    field_data = field_data['data'][0]

                    # if there is a data array, then the type should always be plural.
                    field_data['type'] = self.util.camel_string(field_data['type']).plural()
            elif isinstance(field_data, list):
                # in a few instance like attributeType the value of the properties key/value
                # pair is a list (currently the list only contains a single dict). to be safe
                # we loop over the list and update the type for each item.
                field_data = field_data[0]

                # # handle special case for customAssociationNames, where the data is an array of
                # # string, but the type in the object states 'String'.
                # if field_data['type'] == 'String':
                #     field_data['type'] = 'ListString'
            else:
                raise RuntimeError(
                    f'Invalid type properties data: field-name={field_name}, type={self.type_}'
                )

            field_data['name'] = field_name
            yield field_data

    @property
    def _prop_contents_updated(self) -> dict:
        """Update the properties contents, fixing issues in core data."""
        _properties = self._prop_contents

        # add id field, if missing
        self._prop_content_add_id(_properties)

        # add security label field, if missing
        self._prop_content_add_security_labels(_properties)

        # add webLink field, if missing
        self._prop_content_add_web_link(_properties)

        # fix types
        self._prop_content_fix_types(_properties)

        # remove unused fields, if any
        self._prop_content_remove_unused(_properties)

        # update "bad" data
        self._prop_content_update(_properties)

        # maybe a temp issue?
        if self.type_ == 'indicators':
            _properties['enrichment']['data'][0]['type'] = 'Enrichment'

        # critical fix for breaking API change
        if self.type_ in [
            'case_attributes',
            'group_attributes',
            'indicator_attributes',
            'victim_attributes',
        ]:
            title = 'Attribute Source Type'
            if _properties['source']['type'] != 'String':
                _properties['source']['type'] = 'String'
                self.messages.append(f'- [{self.type_}] - ({title}) - fix required.')
            else:
                self.messages.append(f'- [{self.type_}] - {title} - fix NOT required.')

        if self.type_ == 'groups':
            title = 'Filename Max Length'
            if _properties['fileName']['maxLength'] != 255:
                _properties['fileName']['maxLength'] = 255
                self.messages.append(f'- [{self.type_}] - ({title}) - fix required.')
            else:
                self.messages.append(f'- [{self.type_}] - ({title}) - fix NOT required.')

            title = 'Down Vote Count'
            if 'downVoteCount' in _properties and _properties['downVoteCount']['type'] == 'String':
                _properties['downVoteCount']['type'] = 'Integer'
                self.messages.append(f'- [{self.type_}] - ({title}) - fix required.')
            else:
                self.messages.append(f'- [{self.type_}] - ({title}) - fix NOT required.')

            title = 'Up Vote Count'
            if 'upVoteCount' in _properties and _properties['upVoteCount']['type'] == 'String':
                _properties['upVoteCount']['type'] = 'Integer'
                self.messages.append(f'- [{self.type_}] - ({title}) - fix required.')
            else:
                self.messages.append(f'- [{self.type_}] - ({title}) - fix NOT required.')

        if self.type_ in [
            'cases',
            'tasks',
            'workflow_templates',
        ]:
            if _properties.get('owner'):
                title = 'Read Only Owner Fix'
                if _properties['owner'].get('readOnly') is not True:
                    _properties['owner']['readOnly'] = True
                    self.messages.append(f'- [{self.type_}] - ({title}) - fix required.')
                else:
                    self.messages.append(f'- [{self.type_}] - ({title}) - fix NOT required.')

                title = 'Updatable Owner Fix'
                if _properties['owner'].get('updatable') is not False:
                    _properties['owner']['updatable'] = False
                    self.messages.append(f'- [{self.type_}] - ({title}) - fix required.')
                else:
                    self.messages.append(f'- [{self.type_}] - ({title}) - fix NOT required.')

            if _properties.get('ownerId'):
                title = 'Read Only Owner Id Fix'
                if _properties['ownerId'].get('readOnly') is not True:
                    _properties['ownerId']['readOnly'] = True
                    self.messages.append(f'- [{self.type_}] - ({title}) - fix required.')
                else:
                    self.messages.append(f'- [{self.type_}] - ({title}) - fix NOT required.')

                title = 'Updatable Owner Id Fix'
                if _properties['ownerId'].get('updatable') is not False:
                    _properties['ownerId']['updatable'] = False
                    self.messages.append(f'- [{self.type_}] - ({title}) - fix required.')
                else:
                    self.messages.append(f'- [{self.type_}] - ({title}) - fix NOT required.')

        return _properties

    def _prop_content_add_id(self, properties: dict):
        """Add id field to properties.

        For some reason the core API does not return the id field for some types.
        """
        if 'id' not in properties:
            properties['id'] = {
                'required': False,
                'type': 'Integer',
                'description': 'The id of the **Object**',
                'readOnly': True,
                'updatable': False,
            }
            self.messages.append(f'- [{self.type_}] - The id field is missing.')

    def _prop_content_add_security_labels(self, properties: dict):
        """Add securityLabels field to properties."""
        if self.type_ in ['group_attributes', 'indicator_attributes']:
            if 'securityLabels' not in properties:
                properties['securityLabels'] = {
                    'data': [
                        {
                            'description': (
                                'A list of Security Labels corresponding to the Intel item '
                                '(NOTE: Setting this parameter will replace any existing '
                                'tag(s) with the one(s) specified)'
                            ),
                            'maxSize': 1000,
                            'required': False,
                            'type': 'SecurityLabel',
                        }
                    ]
                }
                self.messages.append(f'- [{self.type_}] - The securityLabels field is missing.')
            else:
                self.messages.append(f'- [{self.type_}] - The securityLabels field is NOT missing.')

    def _prop_content_add_web_link(self, properties: dict):
        """Add webLink field to properties.

        For some reason the core API does not return the webLink field for some types.
        """
        if self.type_ in ['groups', 'indicators']:
            if 'webLink' not in properties:
                properties['webLink'] = {
                    'required': False,
                    'type': 'String',
                    'description': 'The object link.',
                    'readOnly': True,
                    'updatable': False,
                }
                self.messages.append(f'- [{self.type_}] - The webLink field is missing.')
            else:
                self.messages.append(f'- [{self.type_}] - The webLink field is NOT missing.')

    def _prop_content_fix_types(self, _properties: dict):
        """Return modified type."""
        type_ = _properties.get('type')

        if type_ == 'attributes' and self.type_ == 'cases':
            _properties['type'] = 'caseAttributes'
        elif type_ == 'attributes' and self.type_ == 'groups':
            _properties['type'] = 'groupAttributes'
        elif type_ == 'attributes' and self.type_ == 'indicators':
            _properties['type'] = 'indicatorAttributes'
        elif type_ == 'attributes' and self.type_ == 'victims':
            _properties['type'] = 'victimAttributes'

    def _prop_content_remove_unused(self, properties: dict):
        """Remove unused fields from properties."""
        if self.type_ in ['attribute_types']:
            if 'owner' in properties:
                del properties['owner']

        if self.type_ in [
            'attribute_types',
            'case_attributes',
            'group_attributes',
            'indicator_attributes',
            'victim_attributes',
        ]:
            unused_fields = [
                'attributeTypeMappings',
                'ownerId',  # Core Issue: should not be listed for this type
                'ownerName',  # Core Issue: should not be listed for this type
                'settings',
                'tags',  # Core Issue: should not be listed for this type
                'webLink',  # Core Issue: should not be listed for this type
            ]
            for field in unused_fields:
                if field in properties:
                    del properties[field]

        if self.type_ in ['users']:
            unused_fields = [
                'customTqlTimeout',
                'disabled',
                'firstName',
                'jobFunction',
                'jobRole',
                'lastLogin',
                'lastName',
                'lastPasswordChange',
                'locked',
                'logoutIntervalMinutes',
                'owner',
                'ownerRoles',
                'password',
                'passwordResetRequired',
                'pseudonym',
                'systemRole',
                'termsAccepted',
                'termsAcceptedDate',
                'tqlTimeout',
                'twoFactorResetRequired',
                'uiTheme',
            ]
            for field in unused_fields:
                if field in properties:
                    del properties[field]

        if self.type_ in ['victims']:
            unused_fields = [
                'ownerId',  # Core Issue: should not be listed for this type
            ]
            for field in unused_fields:
                if field in properties:
                    del properties[field]

    def _prop_content_update(self, properties: dict):
        """Update "bad" data in properties."""
        if self.type_ in ['groups']:
            # fixed fields that are missing readOnly property
            if 'downVoteCount' in properties:
                properties['downVoteCount']['readOnly'] = True
            if 'upVoteCount' in properties:
                properties['upVoteCount']['readOnly'] = True

        if self.type_ in ['victims']:
            # ownerName is readOnly, but readOnly is not defined in response from OPTIONS endpoint
            properties['ownerName']['readOnly'] = True

    @property
    def _prop_models(self) -> list[PropertyModel]:
        """Return a list of PropertyModel objects."""
        properties_models = []
        for field_data in self._prop_contents_data(self._prop_contents_updated):
            try:
                properties_models.append(PropertyModel(**field_data))
            except ValidationError as ex:
                # print(field_data)
                Render.panel.failure(
                    f'Failed generating property model: data={field_data} ({ex}).',
                )
        return properties_models

    def gen_requirements(self):
        """Generate imports string."""
        # add additional imports when required
        if self.requirements.get('type-checking'):
            self.requirements['standard library'].append('from typing import TYPE_CHECKING')

        indent = ''
        # _libs: list[dict | str] = []
        _libs = []
        for from_, libs in self.requirements.items():
            if not libs:
                # continue if there are no libraries to import
                continue

            if from_ in ['first-party-forward-reference']:
                # skip forward references
                continue

            comment = ''
            if from_ == 'type-checking':
                _libs.append('if TYPE_CHECKING:  # pragma: no cover')
                indent = self.i1
                # this should be fine?
                from_ = 'first-party'
                comment = '  # CIRCULAR-IMPORT'

            _libs.append(f'{indent}# {from_}')

            # manage imports as string and dicts
            _imports = []  # temp store for imports so they can be sorted
            for lib in libs:
                if isinstance(lib, dict):
                    imports = ', '.join(sorted(lib.get('imports')))  # type: ignore
                    _imports.append(
                        f'''{indent}from {lib.get('module')} import {imports}{comment}'''
                    )
                elif isinstance(lib, str):
                    _imports.append(f'{indent}{lib}{comment}')
            _libs.extend(sorted(_imports))  # add imports sorted

            _libs.append('')  # add newline
        _libs.append('')  # add newline

        # This is the last part of the requirements generated.
        return '\n'.join(_libs)  # type: ignore

    @property
    def session(self) -> Session:
        """Return Session configured for TC API."""
        _session = Session()
        _session.auth = HmacAuth(
            os.getenv('TC_API_ACCESS_ID', ''), Sensitive(os.getenv('TC_API_SECRET_KEY', ''))
        )
        return _session

    def tap(self, type_: str):
        """Return the TcEx Api Path."""
        type_ = self.util.snake_string(type_)
        if type_.plural().lower() in [
            'owners',
            'owner_roles',
            'system_roles',
            'users',
            'user_groups',
        ]:
            return 'tcex.api.tc.v3.security'

        if type_.plural().lower() in ['categories', 'results', 'subtypes', 'keyword_sections']:
            return 'tcex.api.tc.v3.intel_requirements'

        return 'tcex.api.tc.v3'
