"""TcEx Framework Module"""

# standard library
from abc import ABC
from textwrap import TextWrapper

# first-party
from tcex.api.tc.v3._gen._gen_abc import GenerateABC
from tcex.util.string_operation import SnakeString


class GenerateModelABC(GenerateABC, ABC):
    """Generate Models for Case Management Types"""

    def __init__(self, type_: SnakeString):
        """Initialize instance properties."""
        super().__init__(type_)

        # properties
        self.requirements = {
            'standard library': [],
            'third-party': [
                {'module': 'pydantic', 'imports': ['BaseModel', 'Extra', 'Field']},
            ],
            'first-party': [
                {'module': 'tcex.util', 'imports': ['Util']},
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

    def _gen_code_validator_method(self, type_: str, data: dict) -> str:
        """Return the validator code

        @validator('artifact_type', always=True, pre=True)
        def _validate_artifact_type(cls, v):
            if not v:
                return ArtifactTypeModel()
            return v
        """
        type_ = self.util.camel_string(type_)
        fields = data['fields']
        typing_type = data['typing_type'].strip('\'')

        fields_string = ', '.join(f'\'{field}\'' for field in fields)
        return '\n'.join(
            [
                f'''{self.i1}@validator({fields_string}, always=True, pre=True)''',
                f'''{self.i1}def _validate_{type_.snake_case()}(cls, v):''',
                f'''{self.i2}if not v:''',
                f'''{self.i3}return {typing_type}()  # type: ignore''',
                f'''{self.i2}return v''',
                '',
            ]
        )

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
        # return (
        #     f'"""{self.type_.singular().title()} / {self.type_.plural().title()} Model"""\n'
        #     '# pylint: disable=no-member,no-self-argument,wrong-import-position\n'
        # )
        return (
            '"""TcEx Framework Module"""\n'
            '# pylint: disable=no-member,no-self-argument,wrong-import-position\n'
        )

    def gen_container_class(self) -> str:
        """Generate the Container Model

        class ArtifactsModel(
            BaseModel,
            title='Artifacts Model',
            alias_generator=Util().snake_to_camel,
            validate_assignment=True,
        ):
        """
        return '\n'.join(
            [
                '',
                f'''class {self.type_.plural().pascal_case()}Model(''',
                f'''{self.i1}BaseModel,''',
                f'''{self.i1}title='{self.type_.plural().pascal_case()} Model',''',
                f'''{self.i1}alias_generator=Util().snake_to_camel,''',
                f'''{self.i1}validate_assignment=True,''',
                '''):''',
                f'''{self.i1}"""{self.type_.plural().title()} Model"""''',
                '',
                '',
            ]
        )

    def gen_container_fields(self) -> str:
        """Generate the Container Model fields

        data: list[ArtifactModel] | None = Field(
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
                    f'''list[{self.type_.singular().pascal_case()}Model] | None '''
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
            alias_generator=Util().snake_to_camel,
            validate_assignment=True,
        ):
        """
        return '\n'.join(
            [
                '',
                f'''class {self.type_.singular().pascal_case()}DataModel(''',
                f'''{self.i1}BaseModel,''',
                f'''{self.i1}title='{self.type_.singular().pascal_case()} Data Model',''',
                f'''{self.i1}alias_generator=Util().snake_to_camel,''',
                f'''{self.i1}validate_assignment=True,''',
                '''):''',
                f'''{self.i1}"""{self.type_.plural().title()} Data Model"""''',
                '',
                '',
            ]
        )

    def gen_data_fields(self) -> str:
        """Generate the Data Model fields

        data: 'ArtifactModel | None' = Field(
            None,
            description='The data of the Artifact.',
            title='data',
        )
        """
        return '\n'.join(
            [
                (
                    f'''{self.i1}data: '''
                    f'''list[{self.type_.singular().pascal_case()}Model] | None '''
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
            alias_generator=Util().snake_to_camel,
            validate_assignment=True,
        ):
        """
        return '\n'.join(
            [
                '',
                f'''class {self.type_.singular().pascal_case()}Model(''',
                f'''{self.i1}V3ModelABC,''',
                f'''{self.i1}alias_generator=Util().snake_to_camel,''',
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
        analytics_priority: str | None = Field(
            None,
            allow_mutation=False,
            description='The **analytics priority** for the Artifact.',
            read_only=True,
            title='analyticsPriority',
        )
        """
        _model = []
        for prop in self._prop_models:
            # only add requirements for non-current model type
            if prop.extra.type != self.type_.plural().pascal_case():
                if prop.extra.import_data and prop.extra.import_source:
                    self.requirements[prop.extra.import_source].append(prop.extra.import_data)

            # add validator
            if prop.extra.model is not None:
                self.validators.setdefault(prop.type, {})
                self.validators[prop.type].setdefault('fields', [])
                self.validators[prop.type]['fields'].append(prop.name.snake_case())
                self.validators[prop.type]['typing_type'] = prop.extra.typing_type

            # update model
            comment = ''
            if prop.extra.alias.snake_case() in ['id']:
                comment = '  # type: ignore'
            _model.append(
                f'''{self.i1}{prop.extra.alias.snake_case()}: '''
                f'''{prop.extra.typing_type} = Field({comment}'''
            )
            _model.append(f'''{self.i2}None,''')  # the default value

            # allow_mutation / readOnly
            if prop.read_only is True and prop.name != 'id':
                _model.append(f'''{self.i2}allow_mutation=False,''')  # readOnly/mutation setting

            # alias
            if prop.extra.alias is not None and prop.name != prop.extra.alias:
                _model.append(f'''{self.i2}alias='{prop.name}',''')

            # applies_to
            if prop.applies_to is not None:
                _model.append(f'''{self.i2}applies_to={prop.applies_to},''')

            # conditional_required
            if prop.conditional_required is not None:
                _model.append(f'''{self.i2}conditional_required={prop.conditional_required},''')

            # description - Use the TC provided description
            # if available, otherwise use a default format.
            field_description = self._format_description(
                (
                    prop.description
                    or (
                        f'The **{prop.name.space_case().lower()}** '
                        f'for the {self.type_.singular().title()}.'
                    )
                ).replace('\'', '\\\''),
                100,
            )
            if field_description is not None:
                _model.append(f'''{self.i2}description={field_description},''')

            # methods (HTTP)
            if prop.extra.methods:
                _model.append(f'''{self.i2}methods={prop.extra.methods},''')

            # max_length
            # if prop.max_length is not None:
            #     _model.append(f'''{self.i2}max_length={prop.max_length},''')

            # max_size
            # if field_max_size is not None:
            #     _model.append(f'''{self.i2}max_items={field_max_size},''')

            # max_value
            # if prop.max_value is not None:
            #     _model.append(f'''{self.i2}maximum={prop.max_value},''')

            # min_length
            # if prop.min_length is not None:
            #     _model.append(f'''{self.i2}min_length={prop.min_length},''')

            # min_value
            # if prop.min_value is not None:
            #     _model.append(f'''{self.i2}minimum={prop.min_value},''')

            # readOnly/allow_mutation setting
            _model.append(f'''{self.i2}read_only={prop.read_only},''')

            # required-alt-field
            if prop.required_alt_field is not None:
                _model.append(f'''{self.i2}required_alt_field='{prop.required_alt_field}',''')

            # title
            _model.append(f'''{self.i2}title='{prop.name}',''')

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

        validators = dict(sorted({k: v for k, v in self.validators.items() if v['fields']}.items()))
        for key, data in validators.items():
            if not data['fields']:
                continue
            _v.append(self._gen_code_validator_method(key, data))

        # add blank line above validators only if validators exists
        if _v:
            _v.insert(0, '')
            self._add_pydantic_validator()

        return '\n'.join(_v)
