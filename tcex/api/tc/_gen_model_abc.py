"""Generate Models for ThreatConnect API"""
# standard library
from abc import ABC
import os
import sys

# third-party
import inflect
import typer
from requests import Session
from requests.exceptions import ProxyError

# first-party
from tcex.backports import cached_property
from tcex.sessions.tc_session import HmacAuth
from tcex.utils import Utils


class GenerateModelABC(ABC):
    """Generate Models for Case Management Types"""

    def __init__(self, type_: str) -> None:
        """Initialize class properties."""
        self.type_ = type_

        # properties
        self._api_server = os.getenv('TC_API_PATH')
        self.class_name = ''.join(w.title() for w in self.type_.split('_'))
        self.config_title = self.type_.replace('_', ' ').title()
        self.indent = '    '
        self.inflect = inflect.engine()
        self.requirements = {
            'standard library': [
                'from typing import Optional, List',
            ],
            'third-party': ['from pydantic import BaseModel, Extra, Field, validator'],
            'first-party': ['from tcex.utils import Utils'],
            'first-party-forward-reference': [],
        }
        self.utils = Utils()
        self.validators = {}

    def _prop_type_common(self) -> dict:
        """Return common types."""
        return {
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
            'Integer': {
                'type': 'Optional[int]',
            },
            'JsonNode': {
                'type': 'Optional[dict]',
            },
            'Links': {
                'type': 'Optional[dict]',
            },
            'Long': {
                'type': 'Optional[int]',
            },
            'String': {
                'type': 'Optional[str]',
            },
        }

    def _prop_type_case_management(self, type_: str, field: str) -> dict:
        """Return cm types."""
        return {
            'Artifact': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.case_management.models.artifact_model import ArtifactModel'
                    ),
                },
                'type': '\'Optional[ArtifactModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'Artifacts': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.case_management.models.artifact_model import ArtifactsModel'
                    ),
                },
                'type': '\'Optional[ArtifactsModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'ArtifactType': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.case_management.models.artifact_type_model '
                        'import ArtifactTypeModel'
                    ),
                },
                'type': '\'Optional[ArtifactTypeModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            # 'Attributes': {
            'CaseAttributeDatas': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.case_management.models.attribute_model import AttributesModel'
                    ),
                },
                'type': '\'Optional[AttributesModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'Case': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.case_management.models.case_model import CaseModel',
                },
                'type': '\'Optional[CaseModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'Cases': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.case_management.models.case_model import CasesModel',
                },
                'type': '\'Optional[CasesModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'Note': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.case_management.models.note_model import NoteModel',
                },
                'type': '\'Optional[NoteModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'Notes': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.case_management.models.note_model import NotesModel',
                },
                'type': '\'Optional[NotesModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'Tag': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.case_management.models.tag_model import TagModel',
                },
                'type': '\'Optional[TagModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'Tags': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.case_management.models.tag_model import TagsModel',
                },
                'type': '\'Optional[TagsModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'Task': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.case_management.models.task_model import TaskModel',
                },
                'type': '\'Optional[TaskModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'Tasks': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.case_management.models.task_model import TasksModel',
                },
                'type': '\'Optional[TasksModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'WorkflowEvent': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.case_management.models.workflow_event_model '
                        'import WorkflowEventModel'
                    ),
                },
                'type': '\'Optional[WorkflowEventModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'WorkflowEvents': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.case_management.models.workflow_event_model '
                        'import WorkflowEventsModel'
                    ),
                },
                'type': '\'Optional[WorkflowEventsModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'WorkflowTemplate': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': (
                        'from tcex.api.tc.v3.case_management.models.workflow_template_model '
                        'import WorkflowTemplateModel'
                    ),
                },
                'type': '\'Optional[WorkflowTemplateModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
        }

    def _prop_type_user(self, type_: str, field: str) -> dict:
        """Return user types."""
        return {
            'Assignee': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': ('from tcex.api.tc.v3.case_management.assignee import Assignee'),
                },
                'type': '\'Optional[Assignee]\'',
            },
            'User': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.security.models.user_model import UserModel',
                },
                'type': '\'Optional[UserModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
            'Users': {
                'requirement': {
                    'from': 'first-party-forward-reference',
                    'import': 'from tcex.api.tc.v3.security.models.user_model import UsersModel',
                },
                'type': '\'Optional[UsersModel]\'',
                'validator': [
                    f'''    @validator('{field}', always=True)''',
                    f'''    def _validate_{field}(cls, v):''',
                    '''        if not v:''',
                    f'''            return {type_}Model()''',
                    '''        return v''',
                    '',
                ],
            },
        }

    def _format_description(self, description: str, length: int) -> str:
        """Format description for field."""
        # fix descriptions coming from core API endpoint
        if not description.endswith('.'):
            description += '.'

        # fix core descriptions that are not capitalized.
        description_words = description.split(' ')
        description = f'{description_words[0].title()} ' + ' '.join(description_words[1:])

        # there are 23 characters used on the line (indent -> key -> quote -> comma)
        other_used_space = 22  # space used by indent -> single quote -> key -> comma
        if len(description) < length - other_used_space:
            return f'\'{description}\''

        _description = ['(']
        updated_description = ''
        other_used_space = 15  # space used by indent -> single quote -> comma
        for w in description.split(' '):
            if len(updated_description) + len(w) + other_used_space >= length:
                _description.append(f'{self.indent * 3}\'{updated_description}\'')
                updated_description = ''
            updated_description += f'{w} '
        _description.append(f'{self.indent * 3}\'{updated_description.strip()}\'')
        _description.append(f'{self.indent * 2})')

        return '\n'.join(_description)

    @cached_property
    def _type_properties(self) -> dict:
        """Return defined API properties for the current object."""
        _properties = []
        try:
            r = self.session.options(self.api_url, params={'show': 'readOnly'})
            # print(r.request.method, r.request.url, r.text)
            if r.ok:
                _properties = r.json()
                if 'id' not in _properties:
                    _properties['id'] = {
                        'required': False,
                        'type': 'Integer',
                        'description': 'The id of the **Object**',
                        'read-only': True,
                    }
        except (ConnectionError, ProxyError) as ex:
            typer.secho(f'Failed getting types properties ({ex}).', fg=typer.colors.RED)
            typer.Exit(1)
        return _properties

    def gen_doc_string_code(self) -> str:
        """Generate doc string."""
        return f'"""{self.config_title} Model"""\n'

    def gen_requirements_code(self):
        """Generate imports string."""
        _libs = []
        for from_, libs in self.requirements.items():
            if from_ in ['first-party-forward-reference']:
                continue

            _libs.append(f'# {from_}')
            for lib in sorted(libs):
                _libs.append(lib)
            _libs.append('')  # add newline
        _libs.append('')  # add newline
        _libs.append('')  # add newline
        return '\n'.join(_libs)

    def gen_requirements_forward_reference_code(self):
        """Generate imports string."""
        # add imports
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

        # add forward references
        _libs.append('')
        _libs.append('')
        _libs.append('# add forward references')
        _libs.append(f'{self.class_name}Data.update_forward_refs()')
        _libs.append(f'{self.class_name}Model.update_forward_refs()')
        _libs.append(f'{self.class_name}sModel.update_forward_refs()')
        _libs.append('')  # add newline
        return '\n'.join(_libs)

    def gen_model_container_code(self) -> str:
        """Generate the Model

        class ArtifactsModel(
            BaseModel,
            title='Artifacts Model',
            alias_generator=Utils().snake_to_camel,
            validate_assignment=True
        ):
            data: 'Optional[List[ArtifactModel]]' = Field(
                [],
                description='The data of the Cases.',
                methods=['POST', 'PUT'],
                title='data',
            )
        """
        _model = [
            f'''class {self.class_name}sModel(''',
            '''    BaseModel,''',
            f'''    title='{self.class_name}s Model',''',
            '''    alias_generator=Utils().snake_to_camel,''',
            '''    validate_assignment=True,''',
            '''):''',
            f'''    """{self.config_title}s Model"""''',
            '',
            f'''    data: 'Optional[List[{self.class_name}Model]]' = Field(''',
            '''        [],''',
            f'''        description='The data for the {self.class_name}.',''',
            '''        methods=['POST', 'PUT'],''',
            '''        title='data',''',
            '''    )''',
        ]
        _model.append('')
        _model.append('')
        _model.append('')
        return '\n'.join(_model)

    def gen_model_data_code(self) -> str:
        """Generate the Model

        class ArtifactData(
            BaseModel,
            title='Artifact Data',
            alias_generator=Utils().snake_to_camel,
            validate_assignment=True
        ):
            data: 'Optional[ArtifactModel]' = Field(
                None,
                description='The data of the Artifact.',
                title='data',
            )
        """
        _model = [
            f'''class {self.class_name}Data(''',
            '''    BaseModel,''',
            f'''    title='{self.class_name} Data',''',
            '''    alias_generator=Utils().snake_to_camel,''',
            '''    validate_assignment=True''',
            '''):''',
            f'''    """{self.config_title} Data"""''',
            '',
            f'''    data: 'Optional[{self.class_name}Model]' = Field(''',
            '''        None,''',
            f'''        description='The data for the {self.class_name}.',''',
            '''        methods=['POST', 'PUT'],''',
            '''        title='data',''',
            '''    )''',
        ]
        _model.append('')
        _model.append('')
        _model.append('')
        return '\n'.join(_model)

    def gen_model_code(self) -> str:
        """Generate the Model"""
        _model = [
            f'''class {self.class_name}Model(''',
            '''    BaseModel,''',
            f'''    title='{self.class_name} Model',''',
            '''    alias_generator=Utils().snake_to_camel,''',
            '''    extra=Extra.allow,''',
            '''    validate_assignment=True''',
            '''):''',
            f'    """{self.config_title} Model"""',
            '',
        ]
        for prop, prop_data in sorted(self._type_properties.items()):
            prop_snake_case = self.utils.camel_to_snake(prop)
            prop_space_case = self.utils.camel_to_space(prop)
            prop_type = prop_data.get('type')

            if prop_data.get('data') is not None:
                try:
                    prop_data = prop_data.get('data', [])[0]
                except IndexError:
                    print(prop, prop_data)
                    sys.exit(1)

                try:
                    prop_type = self.inflect.plural(
                        prop_data.get('type')
                    )  # change prop type to plural
                except TypeError:
                    print(prop, prop_type, prop_data)
                    sys.exit(1)

            # get the hint type and set requirements
            prop_hint_type = self._configure_type(prop_type, prop_snake_case)

            # property to model fields
            prop_description = self._format_description(
                prop_data.get(
                    'description', f'The **{prop_space_case}** for the {self.class_name}.'
                ),
                100,
            )

            prop_max_length = prop_data.get('max_length')
            prop_min_length = prop_data.get('min_length')
            prop_max_size = prop_data.get('max_size')
            prop_methods = []
            prop_read_only = prop_data.get('read-only', False)
            prop_required_alt_field = prop_data.get('required-alt-field')
            prop_updatable = prop_data.get('updatable')

            # method rules
            if prop_read_only is False:
                prop_methods.append('POST')
                if prop_updatable not in [False]:
                    prop_methods.append('PUT')

            # update model
            _model.append(f'''{self.indent}{prop_snake_case}: {prop_hint_type} = Field(''')
            _model.append(f'''{self.indent * 2}None,''')  # the default value
            if prop_read_only is True and prop != 'id':
                _model.append(
                    f'''{self.indent * 2}allow_mutation=False,'''  # read-only/mutation setting
                )
            if prop_description is not None:
                _model.append(f'''{self.indent * 2}description={prop_description},''')
            if prop_methods:
                _model.append(f'''{self.indent * 2}methods={prop_methods},''')
            if prop_max_length is not None:
                _model.append(f'''{self.indent * 2}max_length={prop_max_length},''')
            if prop_max_size is not None:
                _model.append(f'''{self.indent * 2}max_size={prop_max_size},''')
            if prop_min_length is not None:
                _model.append(f'''{self.indent * 2}min_length={prop_min_length},''')
            # read-only/mutation setting
            _model.append(f'''{self.indent * 2}read_only={prop_read_only},''')
            if prop_required_alt_field is not None:
                _model.append(
                    f'''{self.indent * 2}required_alt_field='{prop_required_alt_field}','''
                )
            _model.append(f'''{self.indent * 2}title='{prop}',''')
            if prop_updatable is not None:
                _model.append(f'''{self.indent * 2}updatable={prop_updatable},''')
            _model.append(f'''{self.indent})''')
        _model.append('')

        return '\n'.join(_model)

    # def gen_model_config_code(self) -> str:
    #     """Generate model config."""
    #     _model_config = [
    #         f'{self.indent}class Config:',
    #         f'{self.indent * 2}"""DataModel Config"""',
    #         '',
    #         f'{self.indent * 2}alias_generator = Utils().snake_to_camel',
    #         f'{self.indent * 2}arbitrary_types_allowed = True',
    #         f'{self.indent * 2}extra = Extra.allow',
    #         f'{self.indent * 2}title = \'{self.config_title} Model\'',
    #         f'{self.indent * 2}underscore_attrs_are_private = True',
    #         f'{self.indent * 2}validate_assignment = True',
    #         '',
    #     ]
    #     return '\n'.join(_model_config)

    def gen_model_validators(self) -> str:
        """Generate model validator."""
        _validators = ''
        if self.validators:
            _validators = '\n'.join(v for k, v in dict(sorted(self.validators.items())).items())
            _validators = f'\n{_validators}'
        return _validators

    @property
    def session(self) -> Session:
        """Return Session configured for TC API."""
        _session = Session()
        _session.auth = HmacAuth(os.getenv('TC_API_ACCESS_ID'), os.getenv('TC_API_SECRET_KEY'))
        return _session
