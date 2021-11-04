"""Generate Object for ThreatConnect API"""
# standard library
from abc import ABC
from typing import Dict, List, Optional

# first-party
from tcex.api.tc.v3._gen._gen_abc import GenerateABC
from tcex.api.tc.v3._gen._gen_args_abc import GenerateArgsABC


class GenerateArgs(GenerateArgsABC):
    """Generate Models for TC API Types"""


class GenerateObjectABC(GenerateABC, ABC):
    """Generate Models for Case Management Types"""

    def __init__(self, type_: str) -> None:
        """Initialize class properties."""
        super().__init__(type_)

        # properties
        self.requirements = {
            'standard library': [],
            'third-party': [],
            'first-party': [
                'from tcex.api.tc.v3.api_endpoints import ApiEndpoints',
                'from tcex.api.tc.v3.object_abc import ObjectABC',
                'from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC',
                'from tcex.api.tc.v3.tql.tql_operator import TqlOperator',
            ],
            'first-party-forward-reference': [],
            'type-checking': [],
        }

    def _gen_code_api_endpoint_property(self) -> str:
        """Return the method code.

        @property
        def _api_endpoint(self) -> str:
            '''Return the type specific API endpoint.'''
            return ApiEndpoints.ARTIFACTS.value
        """
        return '\n'.join(
            [
                f'''{self.i1}@property''',
                f'''{self.i1}def _api_endpoint(self) -> str:''',
                f'''{self.i2}"""Return the type specific API endpoint."""''',
                f'''{self.i2}return ApiEndpoints.{self.type_.upper()}.value''',
                '',
                '',
            ]
        )

    def _gen_code_container_init_method(self) -> str:
        """Return the method code.

        def __init__(self, **kwargs) -> None:
            '''Initialize Class properties.'''
            super().__init__(
                kwargs.pop('session', None),
                kwargs.pop('tql_filter', None),
                kwargs.pop('params', None)
            )
            self._model = ArtifactsModel(**kwargs)
        """
        # add method import requirement
        classes = [
            f'{self.type_.singular().pascal_case()}Model',
            f'{self.type_.plural().pascal_case()}Model',
        ]
        self.update_requirements(self.type_, f'{self.type_.singular()}_model', classes)

        return '\n'.join(
            [
                f'''{self.i1}def __init__(self, **kwargs) -> None:''',
                f'''{self.i2}"""Initialize class properties."""''',
                f'''{self.i2}super().__init__(''',
                (
                    f'''{self.i3}kwargs.pop('session', None), '''
                    f'''kwargs.pop('tql_filter', None), '''
                    f'''kwargs.pop('params', None)'''
                ),
                f'''{self.i2})''',
                f'''{self.i2}self._model = {self.type_.plural().pascal_case()}Model(**kwargs)''',
                f'''{self.i2}self._type = \'{self.type_.plural()}\'''',
                '',
                '',
            ]
        )

    def _gen_code_container_iter_method(self) -> str:
        """Return the method code.

        def __iter__(self) -> 'Artifact':
            '''Iterate over CM objects.'''
            return self.iterate(base_class=Artifact)
        """
        return '\n'.join(
            [
                f'''{self.i1}def __iter__(self) -> '{self.type_.singular().pascal_case()}':''',
                f'''{self.i2}"""Iterate over CM objects."""''',
                (
                    f'''{self.i2}return self.iterate(base_class='''
                    f'''{self.type_.singular().pascal_case()})'''
                ),
                '',
                '',
            ]
        )

    def _gen_code_container_filter_property(self) -> str:
        """Return the method code.

        @property
        def filter(self) -> 'ArtifactFilter':
            '''Return the type specific filter object.'''
            return ArtifactFilter(self._session, self.tql)
        """
        filter_class = f'{self.type_.singular().pascal_case()}Filter'
        self.update_requirements(self.type_, f'{self.type_.singular()}_filter', [filter_class])
        return '\n'.join(
            [
                f'''{self.i1}@property''',
                f'''{self.i1}def filter(self) -> '{filter_class}':''',
                f'''{self.i2}"""Return the type specific filter object."""''',
                f'''{self.i2}return {filter_class}(self.tql)''',
                '',
                '',
            ]
        )

    def _gen_code_object_init_method(self) -> str:
        """Return the method code.

        def __init__(self, **kwargs) -> None:
            '''Initialize Class properties'''
            super().__init__(kwargs.pop('session', None))
            self._model = ArtifactModel(**kwargs)
        """
        # add method import requirement
        # classes = [f'{self.type_.singular().pascal_case()}Model']
        # self.update_requirements(self.type_, 'model', classes)

        return '\n'.join(
            [
                f'''{self.i1}def __init__(self, **kwargs) -> None:''',
                f'''{self.i2}"""Initialize class properties."""''',
                f'''{self.i2}super().__init__(kwargs.pop('session', None))''',
                f'''{self.i2}self._model = {self.type_.singular().pascal_case()}Model(**kwargs)''',
                f'''{self.i2}self.type_ = \'{self.type_.singular().space_case()}\'''',
                '',
                '',
            ]
        )

    def _gen_code_object_base_filter_method(self) -> str:
        """Return the method code.

        @property
        def _base_filter(self) -> dict:
            '''Return the default filter.'''
            return {
                'keyword': 'artifactid',
                'operator': TqlOperator.EQ,
                'value': self.model.id,
                'type_': 'integer',
            }
        """
        return '\n'.join(
            [
                f'''{self.i1}@property''',
                f'''{self.i1}def _base_filter(self) -> dict:''',
                f'''{self.i2}"""Return the default filter."""''',
                f'''{self.i2}return {{''',
                f'''{self.i3}'keyword': '{self.type_.singular()}_id',''',
                f'''{self.i3}'operator': TqlOperator.EQ,''',
                f'''{self.i3}'value': self.model.id,''',
                f'''{self.i3}'type_': 'integer',''',
                f'''{self.i2}}}''',
                '',
                '',
            ]
        )

    def _gen_code_object_as_entity_property_method(self) -> str:
        """Return the method code.

        @property
        def as_entity(self) -> dict:
            '''Return the entity representation of the object.'''
            case - name
            notes - summary
            tag - name
            task - name
            workflow_event - summary
            workflow_template_model - name

            return {'type': 'Artifact', 'id': self.model.id, 'value': self.model.summary}
        """
        # TODO: Make the type value the indicator type -
        name_entities = ['case', 'tag', 'task', 'workflow template']
        value_type = 'summary'
        if self.type_.lower() in name_entities:
            value_type = 'name'

        return '\n'.join(
            [
                f'''{self.i1}@property''',
                f'''{self.i1}def as_entity(self) -> dict:''',
                f'''{self.i2}"""Return the entity representation of the object."""''',
                f'''{self.i2}type = self.type_''',
                f'''{self.i2}if hasattr(self.model, 'type'):''',
                f'''{self.i3}type = self.model.type''',
                '',
                (
                    f'''{self.i2}return {{'type': type, 'id': '''
                    f'''self.model.id, 'value': self.model.{value_type}}}'''
                ),
                '',
                '',
            ]
        )

    def _gen_code_object_add_type_method(self, type_) -> str:
        """Return the method code.

        def add_artifact(self, **kwargs) -> None:
            '''Add a Artifact to object.

            ...
            '''
            self.model.notes.data.append(NoteModel(**kwargs))
        """
        type_ = self.utils.camel_string(type_)
        model_name = f'{type_.singular().pascal_case()}Model'
        self.update_requirements(type_, f'{type_.singular()}_model', [model_name])

        # get args
        args = GenerateArgs(type_).gen_args(self.i2, self.i3, nested_objects=False, updatable=False)
        return '\n'.join(
            [
                f'''{self.i1}def add_{type_.singular()}(self, **kwargs) -> None:''',
                f'''{self.i2}"""Add {type_.singular()} to the object.''',
                '',
                f'''{args}''',
                f'''{self.i2}"""''',
                f'''{self.i2}self.model.{type_.plural()}.data.append({model_name}(**kwargs))''',
                '',
                '',
            ]
        )

    def _gen_code_object_type_property_method(self, type_: str) -> str:
        """Return the method code.

        @property
        def artifacts(self):
            '''Yield Artifact from Artifacts'''
            from tcex.api.tc.v3.artifacts.model import Artifact, Artifacts

            yield from self._iterate_over_sublist(Artifacts)
        """
        type_ = self.utils.camel_string(type_)
        self.requirements['type-checking'].append(
            f'from tcex.api.tc.v3.{type_.plural()}.{type_.singular()} import '
            f'{type_.singular().pascal_case()}'
        )
        # self.requirements['first-party'].append(
        #     (
        #         f'from tcex.api.tc.v3.{type_.plural()}.{type_.singular()} import '
        #         f'{type_.singular().pascal_case()}, {type_.plural().pascal_case()}'
        #     )
        # )
        return '\n'.join(
            [
                f'''{self.i1}@property''',
                f'''{self.i1}def {type_.plural()}(self) -> '{type_.singular().pascal_case()}':''',
                (
                    f'''{self.i2}"""Yield {type_.singular().pascal_case()} '''
                    f'''from {type_.plural().pascal_case()}."""'''
                ),
                (
                    f'''{self.i2}from tcex.api.tc.v3.{type_.plural()}.{type_.singular()} import '''
                    f'''{type_.plural().pascal_case()}'''
                ),
                '',
                (
                    f'''{self.i2}yield from self._iterate_over_sublist'''
                    f'''({type_.plural().pascal_case()})'''
                ),
                '',
                '',
            ]
        )

    def gen_container_class(self) -> str:
        """Generate the Container Model

        class Artifacts(ObjectCollectionABC):
            '''Artifacts Collection.

            # Example of params input
            {
                'result_limit': 100,  # Limit the retrieved results.
                'result_start': 10,  # Starting count used for pagination.
                'fields': ['caseId', 'summary']  # Select additional return fields.
            }

            Arg:
                session (Session): Session object configured with TC API Auth.
                tql_filters (list): List of TQL filters.
                params (dict): Additional query params (see example above).
            '''
        """
        return '\n'.join(
            [
                '',
                f'''class {self.type_.plural().pascal_case()}(ObjectCollectionABC):''',
                f'''{self.i1}"""{self.type_.plural().pascal_case()} Collection.''',
                '',
                f'''{self.i1}# Example of params input''',
                f'''{self.i1}{{''',
                f'''{self.i2}'result_limit': 100,  # Limit the retrieved results.''',
                f'''{self.i2}'result_start': 10,  # Starting count used for pagination.''',
                f'''{self.i2}'fields': ['caseId', 'summary']  # Select additional return fields.''',
                f'''{self.i1}}}''',
                '',
                f'''{self.i1}Args:''',
                f'''{self.i2}session (Session): Session object configured with TC API Auth.''',
                f'''{self.i2}tql_filters (list): List of TQL filters.''',
                f'''{self.i2}params (dict): Additional query params (see example above).''',
                f'{self.i1}"""',
                '',
                '',
            ]
        )

    def gen_container_methods(self) -> str:
        """Return the container methods.

        def __init__ ...

        def __iter__ ...

        def filter ...

        """
        _code = ''
        # generate __init__ method
        _code += self._gen_code_container_init_method()

        # generate __iter__ method
        _code += self._gen_code_container_iter_method()

        # generate api_endpoint property method
        _code += self._gen_code_api_endpoint_property()

        # generate filter property method
        _code += self._gen_code_container_filter_property()

        return _code

    def gen_doc_string(self) -> str:
        """Generate doc string."""
        return (
            f'"""{self.type_.singular().pascal_case()} '
            f'/ {self.type_.plural().pascal_case()} Object"""\n'
        )

    def gen_object_class(self) -> str:
        """Generate the Object Model

        class Artifact(ObjectABC):
            '''Case Management Artifact

            Arg:
                case_id (int, kwargs): The **case id** for the Artifact.
                case_xid (str, kwargs): The **case xid** for the Artifact.
                derived_link (bool, kwargs): Flag to specify if this artifact should be used for
                    potentially associated cases or not.
                ...
            '''
        """
        args = GenerateArgs(self.type_).gen_args()
        return '\n'.join(
            [
                '',
                f'''class {self.type_.singular().pascal_case()}(ObjectABC):''',
                f'''{self.i1}"""{self.type_.plural().pascal_case()} Object.''',
                '',
                f'{args}',
                f'{self.i1}"""',
                '',
                '',
            ]
        )

    def gen_object_methods(self) -> str:
        """Return the container methods.

        def __init__ ...

        def __iter__ ...

        def filter ...

        """
        _code = ''

        # generate __init__ method
        _code += self._gen_code_object_init_method()

        # generate api_endpoint property method
        _code += self._gen_code_api_endpoint_property()

        # generate base_filter property method
        _code += self._gen_code_object_base_filter_method()

        # generate as_entity property method
        _code += self._gen_code_object_as_entity_property_method()

        # get NON read-only properties of endpoint
        add_properties = []
        for field_name, field_data in self._type_properties.items():
            # TODO: [super-low] remove this when core updates format of attribute on v3 TI
            if isinstance(field_data.get('data'), dict):
                field_data['data'] = [field_data.get('data')]

            if field_data.get('data') is None:
                # normalize the data format
                field_data = {'data': [field_data]}

            if field_data.get('data')[0].get('read-only', False) is False:
                add_properties.append(field_name)

        # generate add_artifact method
        if 'artifacts' in add_properties:
            _code += self._gen_code_object_add_type_method('artifacts')

        # generate add_case method
        if 'cases' in add_properties:
            _code += self._gen_code_object_add_type_method('cases')

        # generate add_note method
        if 'notes' in add_properties:
            _code += self._gen_code_object_add_type_method('notes')

        # generate add_tag method
        if 'tags' in add_properties:
            _code += self._gen_code_object_add_type_method('tags')

        # generate add_task method
        if 'tasks' in add_properties:
            _code += self._gen_code_object_add_type_method('tasks')

        # properties of endpoint
        properties = list(self._type_properties.keys())

        # generate artifacts property method
        if 'artifacts' in properties:
            _code += self._gen_code_object_type_property_method('artifacts')

        # generate cases property method
        if 'cases' in properties:
            _code += self._gen_code_object_type_property_method('cases')

        # generate notes property method
        if 'notes' in properties:
            _code += self._gen_code_object_type_property_method('notes')

        # generate tags property method
        if 'tags' in properties:
            _code += self._gen_code_object_type_property_method('tags')

        # generate tasks property method
        if 'tasks' in properties:
            _code += self._gen_code_object_type_property_method('tasks')

        return _code

    def update_requirements(
        self, type_: str, filename: str, classes: List[str], from_: Optional[str] = 'first-party'
    ) -> Dict[str, str]:
        """Return the requirements code"""
        type_ = self.utils.camel_string(type_)
        classes = ', '.join(classes)
        self.requirements[from_].append(
            f'from {self.tap(type_)}.{type_.plural().snake_case()}.{filename} import {classes}'
        )
