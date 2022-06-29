"""Generate Models for ThreatConnect API"""
# standard library
import sys
from abc import ABC
from textwrap import TextWrapper
from typing import Dict, List

# first-party
from tcex.api.tc.v3._gen._gen_abc import GenerateABC


class GenerateModelABC(GenerateABC, ABC):
    """Generate Models for Case Management Types"""

    def __init__(self, type_: str):
        """Initialize class properties."""
        super().__init__(type_)

        # properties
        self.requirements = {
            'standard library': [{'module': 'typing', 'imports': ['List', 'Optional']}],
            'third-party': [
                {'module': 'pydantic', 'imports': ['BaseModel', 'Extra', 'Field']},
            ],
            'first-party': [
                {'module': 'tcex.utils', 'imports': ['Utils']},
                {'module': 'tcex.api.tc.v3.v3_model_abc', 'imports': ['V3ModelABC']},
            ],
            'first-party-forward-reference': [],
        }
        self.validators = {}

    def _add_module_class(self, from_: str, module: str, class_: str):
        """Add pydantic validator only when required."""
        for lib in self.requirements[from_]:
            if isinstance(lib, dict):
                if lib.get('module') == module:
                    lib['imports'].append(class_)

    def _add_pydantic_validator(self):
        """Add pydantic validator only when required."""
        self._add_module_class('third-party', 'pydantic', 'validator')

    def _add_pydantic_private_attr(self):
        """Add pydantic validator only when required."""
        self._add_module_class('third-party', 'pydantic', 'PrivateAttr')

    def _configure_type(self, type_: str, field: str) -> str:
        """Return hint type."""
        _types = self._prop_type_common()
        _types.update(self._prop_type_custom(type_))

        # Ensure dict is lowercase.
        _types = {k.lower(): v for k, v in _types.items()}

        # handle types
        type_ = self._fix_type(type_)  # swap Attribute for specific type (e.g., CaseAttribute)
        type_data = _types.get(type_.lower(), {})
        requirement_data = type_data.get('requirement')

        # add additional requirements, if not current model type
        if requirement_data is not None and not type_ == self.type_.plural().pascal_case():
            from_ = requirement_data.get('from')
            import_ = requirement_data.get('import')
            if import_ not in self.requirements.get(from_):
                self.requirements[from_].append(import_)

        # add validator
        for custom_type in self._prop_type_custom(type_):
            if custom_type.lower() == type_.lower():
                self.validators.setdefault(type_, []).append(field)

        return type_data.get('type', type_)

    def _fix_type(self, type_: str) -> str:
        """Fix type for when API returns a "bad" type."""
        if self.type_ == 'cases' and type_ == 'Attributes':
            return 'CaseAttributes'
        if self.type_ == 'groups' and type_ == 'Attributes':
            return 'GroupAttributes'
        if self.type_ == 'indicators' and type_ == 'Attributes':
            return 'IndicatorAttributes'
        if type_ == 'AttributeDatas':
            return 'Attributes'
        return type_

    def _gen_req_code(self, type_: str) -> Dict[str, str]:
        """Return the requirements code"""
        type_ = self.utils.camel_string(type_)
        return {
            'from': 'first-party-forward-reference',
            'import': (
                f'from {self.tap(type_)}.{type_.plural().snake_case()}.'
                f'{type_.singular().snake_case()}_model import {type_}Model'
            ),
        }

    def _gen_code_validator_method(self, type_: str, fields: List[str]) -> str:
        """Return the validator code

        @validator('artifact_type', always=True)
        def _validate_artifact_type(cls, v):
            if not v:
                return ArtifactTypeModel()
            return v
        """
        type_ = self.utils.camel_string(type_)

        fields = ', '.join(f'\'{field}\'' for field in fields)
        return '\n'.join(
            [
                f'''{self.i1}@validator({fields}, always=True)''',
                f'''{self.i1}def _validate_{type_.snake_case()}(cls, v):''',
                f'''{self.i2}if not v:''',
                f'''{self.i3}return {type_}Model()''',
                f'''{self.i2}return v''',
                '',
            ]
        )

    @staticmethod
    def _prop_type_common() -> dict:
        """Return common types."""
        return {
            'boolean': {
                'type': 'bool',
            },
            'BigDecimal': {
                'type': 'Optional[int]',
            },
            'Boolean': {
                'type': 'bool',
            },
            'Date': {
                'requirement': {
                    'from': 'standard library',
                    'import': 'from datetime import datetime',
                },
                'type': 'Optional[datetime]',
            },
            'Double': {
                'type': 'Optional[float]',
            },
            'Integer': {
                'type': 'Optional[int]',
            },
            'JsonNode': {
                'requirement': {'from': 'standard library', 'import': 'from typing import Union'},
                'type': 'Union[Optional[dict], Optional[List[dict]]]',
            },
            'Links': {
                'type': 'Optional[dict]',
            },
            'Long': {
                'type': 'Optional[int]',
            },
            'Short': {
                'type': 'Optional[int]',
            },
            'String': {
                'type': 'Optional[str]',
            },
        }

    def _prop_type_custom(self, type_: str) -> dict:
        """Return cm types."""
        type_ = self._fix_type(self.utils.snake_string(type_))
        return {
            'AdversaryAssets': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'Artifact': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'Artifacts': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'ArtifactType': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'Assignee': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.security.assignee_model import AssigneeModel',
                },
                'type': 'Optional[\'AssigneeModel\']',
            },
            'Attributes': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.attributes.attribute_model import AttributesModel'
                    ),
                },
                'type': f'Optional[\'{type_}Model\']',
            },
            'Case': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'CaseAttributes': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.case_attributes.case_attribute_model '
                        'import CaseAttributesModel'
                    ),
                },
                'type': f'Optional[\'{type_}Model\']',
            },
            'Cases': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'FileAction': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.indicators.file_action_model import FileActionModel'
                    ),
                },
                'type': f'Optional[\'{type_}Model\']',
            },
            'FileOccurrences': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.indicators.file_occurrences_model '
                        'import FileOccurrencesModel'
                    ),
                },
                'type': f'Optional[\'{type_}Model\']',
            },
            'GroupAttributes': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.group_attributes.group_attribute_model '
                        'import GroupAttributesModel'
                    ),
                },
                'type': f'Optional[\'{type_}Model\']',
            },
            'Groups': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'IndicatorAttributes': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.indicator_attributes.indicator_attribute_model '
                        'import IndicatorAttributesModel'
                    ),
                },
                'type': f'Optional[\'{type_}Model\']',
            },
            'Indicators': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'Note': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'Notes': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'SecurityLabels': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'Tag': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'Tags': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'Task': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'TaskAssignees': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.security.task_assignee_model '
                        'import TaskAssigneesModel'
                    ),
                },
                'type': 'Optional[\'TaskAssigneesModel\']',
            },
            'Tasks': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'User': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'Users': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'Victims': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'VictimAssets': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'VictimAttributes': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.victim_attributes.victim_attribute_model '
                        'import VictimAttributesModel'
                    ),
                },
                'type': f'Optional[\'{type_}Model\']',
            },
            'WorkflowEvent': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'WorkflowEvents': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
            'WorkflowTemplate': {
                'requirement': self._gen_req_code(type_),
                'type': f'Optional[\'{type_}Model\']',
            },
        }

    # TODO: [low] bsummers - research combining this method with parent method
    # pylint: disable=arguments-differ
    def _format_description(self, description: str, length: int) -> str:
        """Format description for field."""
        # fix descriptions coming from core API endpoint
        if description[-1] not in ('.', '?', '!'):
            description += '.'

        # fix core descriptions that are not capitalized.
        description_words = description.split(' ')
        description = f'{description_words[0].title()} ' + ' '.join(description_words[1:])

        # there are 23 characters used on the line (indent -> key -> quote -> comma)
        other_used_space = 22  # space used by indent -> single quote -> key -> comma
        if len(description) < length - other_used_space:
            return f'\'{description}\''

        _description = ['(']
        _description.extend(
            [
                f'{line}\''
                for line in TextWrapper(
                    break_long_words=False,
                    drop_whitespace=False,
                    expand_tabs=True,
                    initial_indent=' ' * 12 + '\'',
                    subsequent_indent=' ' * 12 + '\'',
                    tabsize=15,
                    width=length - 1,
                ).wrap(description)
            ]
        )
        _description.append(f'{self.i2})')
        return '\n'.join(_description)

    def gen_doc_string(self) -> str:
        """Generate doc string."""
        return (
            f'"""{self.type_.singular().title()} / {self.type_.plural().title()} Model"""\n'
            '# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position\n'
        )

    def gen_container_class(self) -> str:
        """Generate the Container Model

        class ArtifactsModel(
            BaseModel,
            title='Artifacts Model',
            alias_generator=Utils().snake_to_camel,
            validate_assignment=True,
        ):
        """
        return '\n'.join(
            [
                '',
                f'''class {self.type_.plural().pascal_case()}Model(''',
                f'''{self.i1}BaseModel,''',
                f'''{self.i1}title='{self.type_.plural().pascal_case()} Model',''',
                f'''{self.i1}alias_generator=Utils().snake_to_camel,''',
                f'''{self.i1}validate_assignment=True,''',
                '''):''',
                f'''{self.i1}"""{self.type_.plural().title()} Model"""''',
                '',
                '',
            ]
        )

    def gen_container_fields(self) -> str:
        """Generate the Container Model fields

        data: Optional[List['ArtifactModel']] = Field(
            [],
            description='The data of the Cases.',
            methods=['POST', 'PUT'],
            title='data',
        )
        """
        return '\n'.join(
            [
                (
                    f'''{self.i1}data: '''
                    f'''Optional[List['{self.type_.singular().pascal_case()}Model']] '''
                    '''= Field('''
                ),
                f'''{self.i2}[],''',
                (
                    f'''{self.i2}description='The data for the '''
                    f'''{self.type_.plural().pascal_case()}.','''
                ),
                f'''{self.i2}methods=['POST', 'PUT'],''',
                f'''{self.i2}title='data',''',
                f'''{self.i1})''',
                f'''{self.i1}mode: str = Field(''',
                f'''{self.i2}'append',''',
                (
                    f'''{self.i2}description='The PUT mode for nested '''
                    '''objects (append, delete, replace). Default: append','''
                ),
                f'''{self.i2}methods=['POST', 'PUT'],''',
                f'''{self.i2}title='append',''',
                f'''{self.i1})''',
                '',
                '',
            ]
        )

    def gen_container_private_attrs(self) -> str:
        """Generate doc string."""
        self._add_pydantic_private_attr()
        if self.type_.lower() in [
            'case_attributes',
            'group_attributes',
            'groups',
            'indicator_attributes',
            'indicators',
            'security_labels',
            'cases',
            'artifacts',
            'tags',
            # 'task_assignments',
        ]:
            return '\n'.join(
                [
                    f'{self.i1}_mode_support = PrivateAttr(True)',
                    '',
                    '',
                ]
            )
        return '\n'.join(
            [
                f'{self.i1}_mode_support = PrivateAttr(False)',
                '',
                '',
            ]
        )

    def gen_data_class(self) -> str:
        """Generate the Data Class

        class ArtifactDataModel(
            BaseModel,
            title='Artifact Data',
            alias_generator=Utils().snake_to_camel,
            validate_assignment=True,
        ):
        """
        return '\n'.join(
            [
                '',
                f'''class {self.type_.singular().pascal_case()}DataModel(''',
                f'''{self.i1}BaseModel,''',
                f'''{self.i1}title='{self.type_.singular().pascal_case()} Data Model',''',
                f'''{self.i1}alias_generator=Utils().snake_to_camel,''',
                f'''{self.i1}validate_assignment=True,''',
                '''):''',
                f'''{self.i1}"""{self.type_.plural().title()} Data Model"""''',
                '',
                '',
            ]
        )

    def gen_data_fields(self) -> str:
        """Generate the Data Model fields

        data: 'Optional[ArtifactModel]' = Field(
            None,
            description='The data of the Artifact.',
            title='data',
        )
        """
        return '\n'.join(
            [
                (
                    f'''{self.i1}data: '''
                    f'''Optional[List['{self.type_.singular().pascal_case()}Model']] '''
                    '''= Field('''
                ),
                f'''{self.i2}[],''',
                (
                    f'''{self.i2}description='The data for the '''
                    f'''{self.type_.plural().pascal_case()}.','''
                ),
                f'''{self.i2}methods=['POST', 'PUT'],''',
                f'''{self.i2}title='data',''',
                f'''{self.i1})''',
                '',
                '',
            ]
        )

    def gen_model_class(self) -> str:
        """Generate the model class

        class ArtifactModel(
            BaseModel,
            title='Artifact Model',
            alias_generator=Utils().snake_to_camel,
            validate_assignment=True,
        ):
        """
        return '\n'.join(
            [
                '',
                f'''class {self.type_.singular().pascal_case()}Model(''',
                f'''{self.i1}V3ModelABC,''',
                f'''{self.i1}alias_generator=Utils().snake_to_camel,''',
                f'''{self.i1}extra=Extra.allow,''',
                f'''{self.i1}title='{self.type_.singular().pascal_case()} Model',''',
                f'''{self.i1}validate_assignment=True,''',
                '''):''',
                f'''{self.i1}"""{self.type_.singular().title()} Model"""''',
                '',
                '',
            ]
        )

    def gen_model_fields(self) -> str:
        """Generate the Model

        Example field_data:
        "analyticsPriority": {
            "readOnly": true,
            "type": "String"
        }

        Example Field:
        analytics_priority: Optional[str] = Field(
            None,
            allow_mutation=False,
            description='The **analytics priority** for the Artifact.',
            read_only=True,
            title='analyticsPriority',
        )
        """
        _model = []
        for field_name, field_data in sorted(self._type_properties.items()):
            field_name = self.utils.camel_string(field_name)
            field_title = field_name  # only required when field matches a python reserved word
            field_alias = None  # only required when field matches a python reserved word
            field_type = field_data.get('type')  # the defined field type

            # fix python reserved words
            if field_name in ['from']:
                field_alias = 'from'
                field_name = self.utils.camel_string(f'{field_name}_')

            if field_data.get('data') is not None:
                try:
                    if isinstance(field_data.get('data'), list):
                        field_data = field_data.get('data', [])[0]
                    elif isinstance(field_data.get('data'), dict):
                        # for attributes on groups, this should go away after update to
                        # new attribute format in the future
                        field_data = field_data.get('data')
                except IndexError:
                    print(field_name, field_data)
                    sys.exit(1)

                try:
                    field_type = self.utils.inflect.plural(field_data.get('type'))
                    # field_type = self._fix_type(
                    #     self.utils.inflect.plural(field_data.get('type'))
                    # )  # change field type to plural
                except TypeError:
                    print(field_name, field_type, field_data)
                    sys.exit(1)

            # get the hint type and set requirements
            field_hint_type = self._configure_type(field_type, field_name.snake_case())

            # property to model fields
            field_description = self._format_description(
                field_data.get(
                    'description',
                    (
                        f'The **{field_name.space_case().lower()}** '
                        f'for the {self.type_.singular().title()}.'
                    ),
                ).replace('\'', '\\\''),
                100,
            )

            field_applies_to = field_data.get('appliesTo')
            field_conditional_required = field_data.get('conditionalRequired')
            field_max_length = field_data.get('maxLength')
            field_min_length = field_data.get('minLength')
            # field_max_size = field_data.get('maxSize')
            field_max_value = field_data.get('maxValue')
            field_min_value = field_data.get('minValue')
            field_methods = []
            field_read_only = field_data.get('readOnly', False)
            field_required_alt_field = field_data.get('requiredAltField')
            field_updatable = field_data.get('updatable', True)

            # Bandage to fix core issue. Core should be sending us back `updatable false` on these
            # fields.
            if field_name in ['owner', 'ownerId'] and self.type_.lower() in [
                'cases',
                'tasks',
                'workflow_templates',
            ]:
                field_updatable = False
                field_read_only = True

            # method rules
            if field_read_only is False:
                field_methods.append('POST')
                if field_updatable not in [False]:
                    field_methods.append('PUT')

            # special case until core updates OPTIONS output
            if (
                self.type_.lower() == 'workflow_events'
                and field_name.snake_case() == 'deleted_reason'
            ):
                field_methods = ['DELETE']

            # update model
            _model.append(f'''{self.i1}{field_name.snake_case()}: {field_hint_type} = Field(''')
            _model.append(f'''{self.i2}None,''')  # the default value

            # allow_mutation / readOnly
            if field_read_only is True and field_name != 'id':
                _model.append(f'''{self.i2}allow_mutation=False,''')  # readOnly/mutation setting

            # alias
            if field_alias is not None:
                _model.append(f'''{self.i2}alias='{field_alias}',''')

            # applies_to
            if field_applies_to is not None:
                _model.append(f'''{self.i2}applies_to={field_applies_to},''')

            # applies_to
            if field_conditional_required is not None:
                _model.append(f'''{self.i2}conditional_required={field_conditional_required},''')

            # description
            if field_description is not None:
                _model.append(f'''{self.i2}description={field_description},''')

            # methods (HTTP)
            if field_methods:
                _model.append(f'''{self.i2}methods={field_methods},''')

            # max_length
            if field_max_length is not None:
                _model.append(f'''{self.i2}max_length={field_max_length},''')

            # max_size
            # if field_max_size is not None:
            #     _model.append(f'''{self.i2}max_items={field_max_size},''')

            # max_value
            if field_max_value is not None:
                _model.append(f'''{self.i2}maximum={field_max_value},''')

            # min_length
            if field_min_length is not None:
                _model.append(f'''{self.i2}min_length={field_min_length},''')

            # min_value
            if field_min_value is not None:
                _model.append(f'''{self.i2}minimum={field_min_value},''')

            # readOnly/allow_mutation setting
            _model.append(f'''{self.i2}read_only={field_read_only},''')

            # required-alt-field
            if field_required_alt_field is not None:
                _model.append(f'''{self.i2}required_alt_field='{field_required_alt_field}',''')

            # title
            _model.append(f'''{self.i2}title='{field_title}',''')

            _model.append(f'''{self.i1})''')
        _model.append('')

        return '\n'.join(_model)

    def gen_model_private_attrs(self) -> str:
        """Generate doc string."""
        associated_type = False
        cm_type = False
        shared_type = False

        self._add_pydantic_private_attr()
        if self.type_.lower() in [
            'artifacts',
            'artifact_types',
            'cases',
            'notes',
            'tasks',
            'workflow_events',
            'workflow_templates',
        ]:
            cm_type = True
        elif self.type_.lower() in [
            'security_labels',
            'tags',
        ]:
            shared_type = True
        elif self.type_.lower() in [
            'groups',
            'indicators',
            'victim_assets',
        ]:
            associated_type = True

        return '\n'.join(
            [
                f'{self.i1}_associated_type = PrivateAttr({associated_type})',
                f'{self.i1}_cm_type = PrivateAttr({cm_type})',
                f'{self.i1}_shared_type = PrivateAttr({shared_type})',
                f'{self.i1}_staged = PrivateAttr(False)',
                '',
                '',
            ]
        )

    def gen_requirements_first_party_forward_reference(self):
        """Generate first-party forward reference, imported at the bottom of the file."""
        _libs = []
        for from_, libs in self.requirements.items():
            if from_ not in ['first-party-forward-reference']:
                continue

            if libs:
                _libs.append('')  # add newline
                _libs.append('')  # add newline
                _libs.append('# first-party')
                for lib in sorted(libs):
                    _libs.append(lib)
        return '\n'.join(_libs)

    def gen_forward_reference(self):
        """Generate first-party forward reference, imported at the bottom of the file."""
        return '\n'.join(
            [
                '',
                '',
                '# add forward references',
                f'{self.type_.singular().pascal_case()}DataModel.update_forward_refs()',
                f'{self.type_.singular().pascal_case()}Model.update_forward_refs()',
                f'{self.type_.plural().pascal_case()}Model.update_forward_refs()',
                '',
            ]
        )

    def gen_validator_methods(self) -> str:
        """Generate model validator."""
        _v = []

        validators = dict(
            sorted({k: v for k, v in self.validators.items() if v is not None}.items())
        )
        for key, fields in validators.items():
            if not fields:
                continue
            _v.append(self._gen_code_validator_method(key, fields))

        # add blank line above validators only if validators exists
        if _v:
            _v.insert(0, '')
            self._add_pydantic_validator()

        return '\n'.join(_v)
