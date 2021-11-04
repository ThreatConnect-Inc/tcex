"""Generate Filters for ThreatConnect API"""
# standard library
from abc import ABC

# third-party
import typer
from requests.exceptions import ProxyError

# first-party
from tcex.api.tc.v3._gen._gen_abc import GenerateABC
from tcex.backports import cached_property


class GenerateFilterABC(GenerateABC, ABC):
    """Generate Models for Case Management Types"""

    def __init__(self, type_: str) -> None:
        """Initialize class properties."""
        super().__init__(type_)

        # properties
        self.api_url = None
        self.requirements = {
            'standard library': [
                'from enum import Enum',
            ],
            'third-party': [],
            'first-party': [
                'from tcex.api.tc.v3.api_endpoints import ApiEndpoints',
                'from tcex.api.tc.v3.filter_abc import FilterABC',
                'from tcex.api.tc.v3.tql.tql_type import TqlType',
            ],
            'first-party-forward-reference': [],
        }

    def _add_tql_imports(self):
        """Add TQL imports when required."""
        if 'from tcex.api.tc.v3.tql.tql import Tql' not in self.requirements['first-party']:
            self.requirements['first-party'].extend(
                [
                    'from tcex.api.tc.v3.tql.tql import Tql',
                    'from tcex.api.tc.v3.tql.tql_operator import TqlOperator',
                ]
            )

    @cached_property
    def _filter_properties(self) -> dict:
        """Return defined API properties for the current object.

        Response:
        {
            "keyword": "analyticsScore",
            "name": "Analytics Score",
            "type": "Integer",
            "description": "The intel score of the artifact",
            "groupable": false,
            "targetable": true
        }
        """
        _properties = []
        try:
            r = self.session.options(f'{self.api_url}/tql', params={})
            if r.ok:
                _properties = r.json()
        except (ConnectionError, ProxyError) as ex:
            typer.secho(f'Failed getting types properties ({ex}).', fg=typer.colors.RED)
            typer.Exit(1)
        return _properties

    @staticmethod
    def _filter_type(filter_type: str):
        """Return the Python type based on the filter type."""
        # get the arg type
        filter_type_map = {
            'Boolean': 'bool',
            'Integer': 'int',
            'Long': 'int',
        }
        return filter_type_map.get(filter_type, 'str')

    def _gen_code_generic_method(self, filter_data: dict) -> str:
        """Return code for generic TQL filter methods.

        filter_data:
        {
            "keyword": "analyticsScore",
            "name": "Analytics Score",
            "type": "Integer",
            "description": "The intel score of the artifact",
            "groupable": false,
            "targetable": true
        }
        """
        keyword = self.utils.camel_string(filter_data.get('keyword'))
        description = filter_data.get('description')
        name = filter_data.get('name')
        type_ = filter_data.get('type')

        comment = ''
        if keyword in ['id', 'type']:
            comment = '  # pylint: disable=redefined-builtin'

        return [
            (
                f'{self.i1}def {keyword.snake_case()}'
                f'(self, operator: Enum, {keyword.snake_case()}: '
                f'{self._filter_type(type_)}) -> None:{comment}'
            ),
            f'{self.i2}"""Filter {name} based on **{keyword}** keyword.',
            '',
            f'{self.i2}Args:',
            f'{self.i3}operator: The operator enum for the filter.',
            f'{self.i3}{keyword.snake_case()}: {description}.',
            f'{self.i2}"""',
            (
                f'''{self.i2}self._tql.add_filter('{keyword}', '''
                f'''operator, {keyword.snake_case()}, {self._tql_type(type_)})'''
            ),
            '',
        ]

    def _gen_code_has_artifact_method(self) -> str:
        """Return code for has_artifact TQL filter methods."""
        self._add_tql_imports()
        return [
            f'{self.i1}@property',
            f'{self.i1}def has_artifact(self):',
            f'{self.i2}"""Return **ArtifactFilter** for further filtering."""',
            f'{self.i2}# first-party',
            f'{self.i2}from tcex.api.tc.v3.artifacts.artifact_filter import ArtifactFilter',
            '',
            f'{self.i2}artifacts = ArtifactFilter(Tql())',
            (
                f'''{self.i2}self._tql.add_filter('hasArtifact', '''
                '''TqlOperator.EQ, artifacts, TqlType.SUB_QUERY)'''
            ),
            f'{self.i2}return artifacts',
            '',
        ]

    def _gen_code_has_case_method(self) -> str:
        """Return code for has_case TQL filter methods."""
        self._add_tql_imports()
        return [
            f'{self.i1}@property',
            f'{self.i1}def has_case(self):',
            f'{self.i2}"""Return **CaseFilter** for further filtering."""',
            f'{self.i2}# first-party',
            f'{self.i2}from tcex.api.tc.v3.cases.case_filter import CaseFilter',
            '',
            f'{self.i2}cases = CaseFilter(Tql())',
            (
                f'''{self.i2}self._tql.add_filter('hasCase', '''
                '''TqlOperator.EQ, cases, TqlType.SUB_QUERY)'''
            ),
            f'{self.i2}return cases',
            '',
        ]

    def _gen_code_has_group_method(self) -> str:
        """Return code for has_group TQL filter methods."""
        self._add_tql_imports()
        _code = [
            f'{self.i1}@property',
            f'{self.i1}def has_group(self):',
            f'{self.i2}"""Return **GroupFilter** for further filtering."""',
        ]
        if self.type_ != 'groups':
            _code.extend(
                [
                    f'{self.i2}# first-party',
                    f'{self.i2}from tcex.api.tc.v3.groups.group_filter import GroupFilter',
                    '',
                ]
            )
        _code.extend(
            [
                f'{self.i2}groups = GroupFilter(Tql())',
                (
                    f'''{self.i2}self._tql.add_filter('hasGroup', '''
                    '''TqlOperator.EQ, groups, TqlType.SUB_QUERY)'''
                ),
                f'{self.i2}return groups',
                '',
            ]
        )
        return _code

    def _gen_code_has_indicator_method(self) -> str:
        """Return code for has_indicator TQL filter methods."""
        self._add_tql_imports()
        _code = [
            f'{self.i1}@property',
            f'{self.i1}def has_indicator(self):',
            f'{self.i2}"""Return **IndicatorFilter** for further filtering."""',
        ]
        if self.type_ != 'indicators':
            _code.extend(
                [
                    f'{self.i2}# first-party',
                    (
                        f'{self.i2}from tcex.api.tc.v3.indicators.indicator_filter '
                        'import IndicatorFilter'
                    ),
                    '',
                ]
            )
        _code.extend(
            [
                f'{self.i2}indicators = IndicatorFilter(Tql())',
                (
                    f'''{self.i2}self._tql.add_filter('hasIndicator', '''
                    '''TqlOperator.EQ, indicators, TqlType.SUB_QUERY)'''
                ),
                f'{self.i2}return indicators',
                '',
            ]
        )
        return _code

    def _gen_code_has_note_method(self) -> str:
        """Return code for has_note TQL filter methods."""
        self._add_tql_imports()
        return [
            f'{self.i1}@property',
            f'{self.i1}def has_note(self):',
            f'{self.i2}"""Return **NoteFilter** for further filtering."""',
            f'{self.i2}# first-party',
            f'{self.i2}from tcex.api.tc.v3.notes.note_filter import NoteFilter',
            '',
            f'{self.i2}notes = NoteFilter(Tql())',
            (
                f'''{self.i2}self._tql.add_filter('hasNote', '''
                f'''TqlOperator.EQ, notes, TqlType.SUB_QUERY)'''
            ),
            f'{self.i2}return notes',
            '',
        ]

    def _gen_code_has_tag_method(self) -> str:
        """Return code for has_tag TQL filter methods."""
        self._add_tql_imports()
        return [
            f'{self.i1}@property',
            f'{self.i1}def has_tag(self):',
            f'{self.i2}"""Return **TagFilter** for further filtering."""',
            f'{self.i2}# first-party',
            f'{self.i2}from tcex.api.tc.v3.tags.tag_filter import TagFilter',
            '',
            f'{self.i2}tags = TagFilter(Tql())',
            (
                f'''{self.i2}self._tql.add_filter('hasTag', '''
                '''TqlOperator.EQ, tags, TqlType.SUB_QUERY)'''
            ),
            f'{self.i2}return tags',
            '',
        ]

    def _gen_code_has_task_method(self) -> str:
        """Return code for has_task TQL filter methods."""
        self._add_tql_imports()
        return [
            f'{self.i1}@property',
            f'{self.i1}def has_task(self):',
            f'{self.i2}"""Return **TaskFilter** for further filtering."""',
            f'{self.i2}# first-party',
            f'{self.i2}from tcex.api.tc.v3.tasks.task_filter import TaskFilter',
            '',
            f'{self.i2}tasks = TaskFilter(Tql())',
            (
                f'''{self.i2}self._tql.add_filter('hasTask', '''
                '''TqlOperator.EQ, tasks, TqlType.SUB_QUERY)'''
            ),
            f'{self.i2}return tasks',
            '',
        ]

    @staticmethod
    def _tql_type(tql_type: str):
        """Return the Python type based on the filter type."""
        # get the arg type
        tql_type_map = {
            'Boolean': 'TqlType.BOOLEAN',
            'Integer': 'TqlType.INTEGER',
            'Long': 'TqlType.INTEGER',
        }
        return tql_type_map.get(tql_type, 'TqlType.STRING')

    def gen_api_endpoint_method(self) -> str:
        """Generate private class method/property.

        @property
        def _api_endpoint(self) -> str:
            \"\"\"Return the API endpoint.\"\"\"
            return ApiEndpoints.ARTIFACTS.value
        """
        _method = [
            f'{self.i1}@property',
            f'{self.i1}def _api_endpoint(self) -> str:',
            f'{self.i2}"""Return the API endpoint."""',
            f'{self.i2}return ApiEndpoints.{self.type_.upper()}.value',
        ]
        _method.append('')
        return '\n'.join(_method)

    def gen_class(self) -> str:
        """Generate doc string."""
        return '\n'.join(
            [
                f'\nclass {self.type_.singular().pascal_case()}Filter(FilterABC):',
                f'{self.i1}"""Filter Object for {self.type_.plural().pascal_case()}"""',
                '',
                '',
            ]
        )

    def gen_class_methods(self):
        """Return a Filter Class current object."""
        _filter_class = []

        # added _api_endpoint method
        _filter_class.append(self.gen_api_endpoint_method())

        for t in sorted(self._filter_properties.get('data', []), key=lambda i: i['keyword']):
            keyword = self.utils.camel_string(t.get('keyword'))

            if keyword.snake_case() == 'has_artifact':
                _filter_class.extend(self._gen_code_has_artifact_method())
            elif keyword.snake_case() == 'has_case':
                _filter_class.extend(self._gen_code_has_case_method())
            elif keyword.snake_case() == 'has_group':
                _filter_class.extend(self._gen_code_has_group_method())
            elif keyword.snake_case() == 'has_indicator':
                _filter_class.extend(self._gen_code_has_indicator_method())
            elif keyword.snake_case() == 'has_note':
                _filter_class.extend(self._gen_code_has_note_method())
            elif keyword.snake_case() == 'has_tag':
                _filter_class.extend(self._gen_code_has_tag_method())
            elif keyword.snake_case() == 'has_task':
                _filter_class.extend(self._gen_code_has_task_method())
            else:
                _filter_class.extend(self._gen_code_generic_method(t))

        return '\n'.join(_filter_class)

    def gen_doc_string(self) -> str:
        """Generate doc string."""
        return f'"""{self.type_.singular().title()} TQL Filter"""\n'
