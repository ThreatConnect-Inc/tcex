"""TcEx Framework Module"""

# standard library
import json
from collections.abc import Generator
from pathlib import Path

# third-party
from pydantic import ValidationError
from requests.exceptions import ProxyError

# first-party
from tcex.api.tc.v3._gen._options_abc import OptionsABC
from tcex.api.tc.v3._gen.model import PropertyModel
from tcex.pleb.cached_property import cached_property
from tcex.util.render.render import Render
from tcex.util.util import Util

# The OptionsData class is used to download the options data for a given object type and
# correct and/or update the data to ensure it is usable for the code generation process.
# The "plan" is to have a single class that handles downloading the data and updating it.
# The contents* methods download, update, and load to the model. The content_models method
# is typically the entry point to this class.


class OptionsDataObject(OptionsABC):
    """Gen Model Download Options Class"""

    def __init__(self, api_url: str, object_type: str):
        """Initialize instance properties."""
        self.api_url = api_url
        self.object_type = object_type

        # properties
        self.messages = []

    @cached_property
    def contents(self) -> dict:
        """Return defined API endpoint properties for the current type."""
        _properties = {}
        try:
            r = self.session.options(self.api_url, params={'show': 'readOnly'})
            # print(r.request.method, r.request.url, r.text)
            if r.ok:
                _properties = r.json()

        except (ConnectionError, ProxyError) as ex:
            Render.panel.failure(f'Failed getting types properties ({ex}).')

        return _properties

    @property
    def contents_updated(self) -> Generator:
        """Return the updated contents."""
        properties_comparison = []
        for field_name, field_data in self._contents_update(self.contents).items():
            field_data_ = field_data
            if isinstance(field_data_, dict):
                if 'data' in field_data_ and isinstance(field_data_['data'], list):
                    # some properties have a data key with an array of items.
                    field_data_ = field_data_['data'][0]

                    # if there is a data array, then the type should always be plural.
                    field_data_['type'] = Util.camel_string(field_data_['type']).plural()
            elif isinstance(field_data_, list):
                # in a few instance like attributeType the value of the properties key/value
                # pair is a list (currently the list only contains a single dict). to be safe
                # we loop over the list and update the type for each item.
                field_data_ = field_data_[0]
            else:
                Render.panel.failure(
                    'Invalid type properties data: field-name='
                    f'{field_name}, type={self.object_type}'
                )
            field_data_['name'] = field_name

            # capture input/output data for troubleshooting
            properties_comparison.append(
                {
                    'field_name': field_name,
                    'input_data': self.contents.get(field_name),
                    'output_data': field_data_,
                }
            )

            yield field_data_

        # write comparison data for troubleshooting
        self._write_comparison_data(properties_comparison)

    @property
    def content_models(self) -> Generator[PropertyModel, None, None]:
        """Return a list of PropertyModel objects."""
        for field_data in self.contents_updated:
            try:
                property_model = PropertyModel(**field_data)
            except ValidationError as ex:
                Render.panel.failure(
                    f'Failed generating property model: data={field_data} ({ex}).',
                )
            else:
                yield property_model

    @cached_property
    def properties_data_directory(self) -> Path:
        """Return the properties for the current type."""
        path = Path('tcex/api/tc/v3/_gen/properties_data')
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _contents_update(self, properties: dict) -> dict:
        """Update the properties contents, fixing issues in core data."""

        # add id field, if missing
        self._content_add_id(properties)

        # add security label field, if missing
        self._content_add_security_labels(properties)

        # add webLink field, if missing
        self._content_add_web_link(properties)

        # fix types
        self._content_fix_types(properties)

        # remove unused fields, if any
        self._content_remove_unused(properties)

        # update "bad" data
        self._content_update(properties)

        # maybe a temp issue?
        if self.object_type == 'indicators':
            properties['enrichment']['data'][0]['type'] = 'Enrichment'

        # critical fix for breaking API change
        if self.object_type in [
            'case_attributes',
            'group_attributes',
            'indicator_attributes',
            'victim_attributes',
        ]:
            self._content_update_fix_attribute_source_type(properties)

        if self.object_type == 'groups':
            self._content_update_fix_filename_max_length(properties)
            self._content_update_fix_down_vote_count(properties)
            self._content_update_fix_up_vote_count(properties)

        if self.object_type in [
            'cases',
            'tasks',
            'workflow_templates',
        ]:
            if properties.get('owner'):
                self._content_update_fix_read_only_owner(properties)
                self._content_update_fix_updatable_owner(properties)

            if properties.get('ownerId'):
                self._content_update_fix_read_only_owner_id(properties)
                self._content_update_fix_updatable_owner_id(properties)

        return properties

    def _content_update_fix_attribute_source_type(self, properties: dict):
        """."""
        title = 'Attribute Source Type'
        if properties['source']['type'] != 'String':
            properties['source']['type'] = 'String'
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix required.')
        else:
            self.messages.append(f'- [{self.object_type}] - {title} - fix NOT required.')

    def _content_update_fix_filename_max_length(self, properties: dict):
        """."""
        filename_max_length = 255
        title = 'Filename Max Length'
        if properties['fileName']['maxLength'] != filename_max_length:
            properties['fileName']['maxLength'] = filename_max_length
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix required.')
        else:
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix NOT required.')

    def _content_update_fix_down_vote_count(self, properties: dict):
        """."""
        title = 'Down Vote Count'
        if 'downVoteCount' in properties and properties['downVoteCount']['type'] == 'String':
            properties['downVoteCount']['type'] = 'Integer'
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix required.')
        else:
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix NOT required.')

    def _content_update_fix_up_vote_count(self, properties: dict):
        """."""
        title = 'Up Vote Count'
        if 'upVoteCount' in properties and properties['upVoteCount']['type'] == 'String':
            properties['upVoteCount']['type'] = 'Integer'
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix required.')
        else:
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix NOT required.')

    def _content_update_fix_read_only_owner(self, properties: dict):
        """."""
        title = 'Read Only Owner Fix'
        if properties['owner'].get('readOnly') is not True:
            properties['owner']['readOnly'] = True
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix required.')
        else:
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix NOT required.')

    def _content_update_fix_updatable_owner(self, properties: dict):
        """."""
        title = 'Updatable Owner Fix'
        if properties['owner'].get('updatable') is not False:
            properties['owner']['updatable'] = False
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix required.')
        else:
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix NOT required.')

    def _content_update_fix_read_only_owner_id(self, properties: dict):
        """."""
        title = 'Read Only Owner Id Fix'
        if properties['ownerId'].get('readOnly') is not True:
            properties['ownerId']['readOnly'] = True
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix required.')
        else:
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix NOT required.')

    def _content_update_fix_updatable_owner_id(self, properties: dict):
        """."""
        title = 'Updatable Owner Id Fix'
        if properties['ownerId'].get('updatable') is not False:
            properties['ownerId']['updatable'] = False
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix required.')
        else:
            self.messages.append(f'- [{self.object_type}] - ({title}) - fix NOT required.')

    def _content_add_id(self, properties: dict):
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
            self.messages.append(f'- [{self.object_type}] - The id field is missing.')

    def _content_add_security_labels(self, properties: dict):
        """Add securityLabels field to properties."""
        if self.object_type in ['group_attributes', 'indicator_attributes']:
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
                self.messages.append(
                    f'- [{self.object_type}] - The securityLabels field is missing.'
                )
            else:
                self.messages.append(
                    f'- [{self.object_type}] - The securityLabels field is NOT missing.'
                )

    def _content_add_web_link(self, properties: dict):
        """Add webLink field to properties.

        For some reason the core API does not return the webLink field for some types.
        """
        if self.object_type in ['groups', 'indicators']:
            if 'webLink' not in properties:
                properties['webLink'] = {
                    'required': False,
                    'type': 'String',
                    'description': 'The object link.',
                    'readOnly': True,
                    'updatable': False,
                }
                self.messages.append(f'- [{self.object_type}] - The webLink field is missing.')
            else:
                self.messages.append(f'- [{self.object_type}] - The webLink field is NOT missing.')

    def _content_fix_types(self, _properties: dict):
        """Return modified type."""
        type_ = _properties.get('type')

        if type_ == 'attributes':
            if self.object_type == 'cases':
                _properties['type'] = 'caseAttributes'
            elif self.object_type == 'groups':
                _properties['type'] = 'groupAttributes'
            elif self.object_type == 'indicators':
                _properties['type'] = 'indicatorAttributes'
            elif self.object_type == 'victims':
                _properties['type'] = 'victimAttributes'

    def _content_remove_unused(self, properties: dict):
        """Remove unused fields from properties."""
        if self.object_type in ['attribute_types'] and 'owner' in properties:
            del properties['owner']

        if self.object_type in [
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

        if self.object_type in ['users']:
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

        if self.object_type in ['victims']:
            unused_fields = [
                'ownerId',  # Core Issue: should not be listed for this type
            ]
            for field in unused_fields:
                if field in properties:
                    del properties[field]

    def _content_update(self, properties: dict):
        """Update "bad" data in properties."""
        if self.object_type in ['groups']:
            # fixed fields that are missing readOnly property
            if 'downVoteCount' in properties:
                properties['downVoteCount']['readOnly'] = True
            if 'upVoteCount' in properties:
                properties['upVoteCount']['readOnly'] = True

        if self.object_type in ['victims']:
            # ownerName is readOnly, but readOnly is not defined in response from OPTIONS endpoint
            properties['ownerName']['readOnly'] = True

    def _write_comparison_data(self, properties_comparison: list):
        # write input/output data for troubleshooting
        output_file = self.properties_data_directory / f'{self.object_type}.json'
        with output_file.open(mode='w') as fh:
            json.dump(properties_comparison, fh, indent=2)
