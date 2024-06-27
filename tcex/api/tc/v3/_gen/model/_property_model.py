"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.pleb.cached_property import cached_property
from tcex.util import Util
from tcex.util.render.render import Render
from tcex.util.string_operation import CamelString


# pylint: disable=no-self-argument
class ExtraModel(
    BaseModel,
    extra=Extra.forbid,
    title='Extra Model',
    validate_assignment=True,
):
    """Model Definition"""

    alias: CamelString = Field(..., description='Field alias.')
    import_data: str | None = Field(None, description='The import data.')
    import_source: str | None = Field(
        None, description='The source of the import: standard library, first-party, etc.'
    )
    methods: list[str] = Field([], description='Field methods.')
    model: str | None = Field(None, description='The type model.')
    type: CamelString = Field(..., description='The type of the property.')
    typing_type: str = Field(..., description='The Python typing hint type.')

    @validator('alias', 'type', always=True, pre=True)
    def _camel_string(cls, v):
        """Convert to CamelString."""
        return CamelString(v)


# pylint: disable=no-self-argument
class PropertyModel(
    BaseModel,
    alias_generator=Util().snake_to_camel,
    arbitrary_types_allowed=True,
    extra=Extra.forbid,
    keep_untouched=(cached_property,),
    title='Property Model',
    validate_assignment=True,
):
    """Model Definition"""

    applies_to: list[str] | None = Field(None, description='Applies to property.')
    allowable_values: list[str] | None = Field(
        None, description='Allowable values for the property.'
    )
    conditional_read_only: list[str] | None = Field(
        None, description='Conditionally read-only property.'
    )
    conditional_required: list[str] | None = Field(
        None, description='Conditionally required property.'
    )
    default: str | None = Field(default=None, description='Default value of the property value.')
    description: str | None = Field(default=None, description='Description of the property.')
    max_size: int | None = Field(default=None, description='Maximum size of the property value.')
    max_length: int | None = Field(
        default=None, description='Maximum length of the property value.'
    )
    max_value: int | None = Field(default=None, description='Maximum value of the property value.')
    min_length: int | None = Field(
        default=None, description='Minimum length of the property value.'
    )
    min_value: int | None = Field(default=None, description='Minimum value of the property value.')
    name: CamelString = Field(default=None, description='Name of the property.')
    read_only: bool = Field(default=False, description='Read only property.')
    required: bool = Field(default=False, description='Required property.')
    required_alt_field: str | None = Field(None, description='Required alternative field property.')
    type: CamelString = Field(..., description='The defined property type.')
    updatable: bool = Field(default=True, description='Updatable property.')

    @validator('name', 'type', always=True, pre=True)
    def _came_string(cls, v):
        """Convert to CamelString."""
        if v is None:
            raise ValueError('The property must have a name.')
        return CamelString(v)

    @validator('description', always=True, pre=True)
    def _fix_first_letter_of_sentence(cls, v):
        """Convert to CamelString."""
        if v:
            # ensure the first letter of the sentence is capitalized
            v = v[0].capitalize() + v[1:]
        return v

    @cached_property
    def extra(self) -> ExtraModel:
        """Return the extra model."""
        extra_data = self.__extra_data()
        # print(self.name, self.type, extra_data)
        return ExtraModel(**extra_data)  # type: ignore

    def __extra_data(self) -> dict[str, str]:
        """Enrich the extra model."""
        # set default value for type
        extra = {
            'alias': self.name,
            # calculate the field methods
            'methods': self.__calculate_methods(),
            # set type to current type value, update later
            'type': self.type,
        }

        reserved_words = ['from']
        if self.name in reserved_words:
            extra['alias'] = f'{self.name}_'

        # process bool types
        self.__process_bool_types(self, extra)

        # process dict types
        self.__process_dict_types(self, extra)

        # process float types
        self.__process_float_types(self, extra)

        # process int types
        self.__process_int_types(self, extra)

        # process str types
        self.__process_str_types(self, extra)

        # process tc types
        self.__process_tc_types(self, extra)

        # process special types
        self.__process_special_types(self, extra)

        if extra.get('typing_type') is None:
            Render.panel.failure(
                f'New type found for object name="{self.name}"\n'
                f'Type: "{self.type}" should be added to PropertyModel '
                f'in one of the following methods:\n'
                f'_process_dict, _process_tc_type, _process_special_types\n'
                f'\nextra: {extra}'
            )

        return extra

    def __calculate_methods(self):
        """Calculate the field methods."""

        # special case until core updates OPTIONS output
        methods = []
        if self.name.snake_case() == 'deleted_reason':
            methods.append('DELETE')
        elif self.read_only is False:
            methods.append('POST')

            if self.updatable is not False:
                methods.append('PUT')
        return methods

    @classmethod
    def __process_bool_types(cls, pm: 'PropertyModel', extra: dict[str, str]):
        """Process standard type."""
        types = ['boolean']
        if pm.type.lower() in types:
            extra.update({'typing_type': 'bool'})

    @classmethod
    def __process_dict_types(cls, pm: 'PropertyModel', extra: dict[str, str]):
        """Process standard type."""
        types = [
            'AiInsights',
            'AttackSecurityCoverage',
            'AttributeSource',
            'DNSResolutions',
            'Enrichments',
            'GeoLocation',
            'InvestigationLinks',
            'IntelReqType',
            'IntelRequirement',
            'KeywordSection',
            'Links',
            'Map',
            'ValidationRule',
            'Strings',
            'WhoIs',
        ]
        if pm.type in types:
            extra.update({'typing_type': cls.__extra_format_type('dict')})

    @classmethod
    def __process_float_types(cls, pm: 'PropertyModel', extra: dict[str, str]):
        """Process standard type."""
        types = ['Double']
        if pm.type in types:
            extra.update({'typing_type': cls.__extra_format_type('float')})

    @classmethod
    def __process_int_types(cls, pm: 'PropertyModel', extra: dict[str, str]):
        """Process standard type."""
        types = [
            'bigdecimal',  # BigDecimal
            'integer',  # Integer
            'long',  # Long
            'short',  # Short
        ]
        if pm.type.lower() in types:
            extra.update({'typing_type': cls.__extra_format_type('int')})

    @classmethod
    def __process_special_types(cls, pm: 'PropertyModel', extra: dict[str, str]):
        """Process standard type."""
        bi = 'from tcex.api.tc.v3.'

        if pm.type == 'Assignee':
            bi += 'security.assignee_model'
            extra.update(
                {
                    'import_data': f'{bi} import AssigneeModel',
                    'import_source': 'first-party-forward-reference',
                    'model': f'{pm.type}Model',
                    'typing_type': cls.__extra_format_type_model(pm.type),
                }
            )
        elif pm.type == 'AttributeDatas':
            extra.update(
                {
                    'import_data': f'{bi}.attributes.attribute_model import AttributesModel',
                    'import_source': 'first-party-forward-reference',
                    'model': f'{pm.type}Model',
                    'typing_type': cls.__extra_format_type_model(pm.type),
                }
            )
        elif pm.type == 'CaseAttributes':
            bi += 'case_attributes.case_attribute_model'
            extra.update(
                {
                    'import_data': f'{bi} import CaseAttributesModel',
                    'import_source': 'first-party-forward-reference',
                    'model': f'{pm.type}Model',
                    'typing_type': cls.__extra_format_type_model(pm.type),
                }
            )
        elif pm.type == 'Date':
            extra.update(
                {
                    'import_data': 'from datetime import datetime',
                    'import_source': 'standard library',
                    'typing_type': cls.__extra_format_type('datetime'),
                }
            )
        elif pm.type == 'Group':
            bi += 'groups.group_model'
            extra.update(
                {
                    'import_data': f'{bi} import GroupModel',
                    'import_source': 'first-party-forward-reference',
                    'model': f'{pm.type}Model',
                    'typing_type': cls.__extra_format_type_model(pm.type),
                }
            )
        elif pm.type == 'GroupAttributes':
            bi += 'group_attributes.group_attribute_model'
            extra.update(
                {
                    'import_data': f'{bi} import GroupAttributesModel',
                    'import_source': 'first-party-forward-reference',
                    'model': f'{pm.type}Model',
                    'typing_type': cls.__extra_format_type_model(pm.type),
                }
            )
        elif pm.type == 'Indicator':
            bi += 'indicators.indicator_model'
            extra.update(
                {
                    'import_data': f'{bi} import IndicatorModel',
                    'import_source': 'first-party-forward-reference',
                    'model': f'{pm.type}Model',
                    'typing_type': cls.__extra_format_type_model(pm.type),
                }
            )
        elif pm.type == 'IntelReqType':
            bi += 'intel_requirements.intel_req_type_model'
            extra.update(
                {
                    'import_data': f'{bi} import IntelReqTypeModel',
                    'import_source': 'first-party-forward-reference',
                    'model': 'IntelReqTypeModel',
                    'typing_type': cls.__extra_format_type_model(pm.type),
                }
            )
        elif pm.type == 'IndicatorAttributes':
            bi += 'indicator_attributes.indicator_attribute_model'
            extra.update(
                {
                    'import_data': f'{bi} import IndicatorAttributesModel',
                    'import_source': 'first-party-forward-reference',
                    'model': f'{pm.type}Model',
                    'typing_type': cls.__extra_format_type_model(pm.type),
                }
            )
        elif pm.type == 'JsonNode':
            extra.update(
                {
                    'import_source': 'standard library',
                    'typing_type': '''dict | list[dict] | None''',
                }
            )
        elif pm.type == 'KeywordSection':
            bi += 'intel_requirements.keyword_sections.keyword_section_model'
            extra.update(
                {
                    'import_data': f'{bi} import KeywordSectionModel',
                    'import_source': 'first-party-forward-reference',
                    'model': 'KeywordSectionModel',
                    'typing_type': f'list[{cls.__extra_format_type_model(pm.type)}]',
                }
            )
        elif pm.name == 'customAssociationNames':
            extra.update(
                {
                    'typing_type': 'list[str]',
                }
            )
        elif pm.name == 'customAssociationNames':
            extra.update(
                {
                    'typing_type': 'list[str]',
                }
            )
        elif pm.type == 'TaskAssignees':
            extra.update(
                {
                    'import_data': (f'{bi}security.task_assignee_model import TaskAssigneesModel'),
                    'import_source': 'first-party-forward-reference',
                    'model': f'{pm.type}Model',
                    'typing_type': cls.__extra_format_type_model(pm.type),
                }
            )
        elif pm.type == 'VictimAttributes':
            bi += 'victim_attributes.victim_attribute_model'
            extra.update(
                {
                    'import_data': f'{bi} import VictimAttributesModel',
                    'import_source': 'first-party-forward-reference',
                    'model': f'{pm.type}Model',
                    'typing_type': cls.__extra_format_type_model(pm.type),
                }
            )

    @classmethod
    def __process_str_types(cls, pm: 'PropertyModel', extra: dict[str, str]):
        """Process standard type."""
        types = [
            'From',
            'Owner',
            'String',
        ]
        if pm.type in types:
            extra.update({'typing_type': cls.__extra_format_type('str')})

    @classmethod
    def __process_tc_types(cls, pm: 'PropertyModel', extra: dict[str, str]):
        """Process standard type."""
        types = [
            'AdversaryAssets',
            'Artifact',
            'Artifacts',
            'ArtifactType',
            'Case',
            'Cases',
            'FileActions',
            'FileOccurrences',
            'Groups',
            'Indicators',
            'Note',
            'Notes',
            'SecurityLabel',
            'SecurityLabels',
            'Tag',
            'Tags',
            'Task',
            'Tasks',
            'User',
            'Users',
            'Victims',
            'VictimAssets',
            'WorkflowEvent',
            'WorkflowEvents',
            'WorkflowTemplate',
        ]
        if pm.type in types:
            extra.update(cls.__extra_gen_req_code(pm.type))
            extra['model'] = f'{pm.type}Model'
            extra['typing_type'] = cls.__extra_format_type_model(pm.type)

    @classmethod
    def __extra_gen_req_code(cls, type_: CamelString) -> dict[str, str]:
        """Return the requirements code"""
        type_ = Util().camel_string(type_)
        return {
            'import_data': (
                f'from {cls.__extra_tap(type_)}.{type_.plural().snake_case()}.'
                f'{type_.singular().snake_case()}_model import {type_}Model'
            ),
            'import_source': 'first-party-forward-reference',
        }

    @classmethod
    def __extra_format_type(cls, type_: str, optional: bool = True) -> str:
        """Format type for use in code."""
        if optional:
            return f'{type_} | None'
        return type_

    @classmethod
    def __extra_format_type_non_native(cls, type_: str, optional: bool = False) -> str:
        """Format type for use in code."""
        if optional:
            return f'\'{type_} | None\''
        return f'\'{type_}\''

    @classmethod
    def __extra_format_type_model(cls, type_: str, optional: bool = False) -> str:
        """Format type for use in code."""
        return cls.__extra_format_type_non_native(f'{type_}Model', optional)

    @classmethod
    def __extra_tap(cls, type_: CamelString) -> str:
        """Return the TcEx Api Path."""
        if type_.snake_case().plural().lower() in [
            'owners',
            'owner_roles',
            'system_roles',
            'users',
            'user_groups',
        ]:
            return 'tcex.api.tc.v3.security'

        if type_.snake_case().plural().lower() in [
            'categories',
            'results',
            'subtypes',
        ]:
            return 'tcex.api.tc.v3.intel_requirements'

        return 'tcex.api.tc.v3'
