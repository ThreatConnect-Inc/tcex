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

    def __init__(self, type_: str):
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
                _properties = r.json().get('data', [])

                # Provided invalid type "BigInteger" on tql options call and correcting it to String
                if self.type_ == 'indicators':
                    for property_ in _properties:
                        if property_.get('keyword') == 'addressIpval':
                            property_['type'] = 'String'

        except (ConnectionError, ProxyError) as ex:
            typer.secho(f'Failed getting types properties ({ex}).', fg=typer.colors.RED)
            typer.Exit(1)
        return _properties

    @staticmethod
    def _filter_type(filter_type: str):
        """Return the Python type based on the filter type."""
        # hint types for the filter method
        filter_type_map = {
            'Assignee': 'str',
            'BigInteger': 'int',
            'Boolean': 'bool',
            'Date': 'str',
            'DateTime': 'str',
            'Enum': 'str',
            'EnumToInteger': 'str',
            'Integer': 'int',
            'Long': 'int',
            'String': 'str',
            'StringCIDR': 'str',
            'StringLower': 'str',
            'StringUpper': 'str',
            'Undefined': 'str',
            'User': 'str',
        }
        hint_type = filter_type_map.get(filter_type)

        # tql types for the add_filter method call
        tql_type_map = {
            'bool': 'TqlType.BOOLEAN',
            'int': 'TqlType.INTEGER',
            'str': 'TqlType.STRING',
        }
        tql_type = tql_type_map.get(hint_type)

        # fail on any unknown types (core added something new)
        if hint_type is None:
            raise RuntimeError(f'Invalid type of {filter_type} (Core team added something new?)')

        return {
            'hint_type': hint_type,
            'tql_type': tql_type,
        }

    def _gen_code_generic_method(self, filter_data: dict) -> list:
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
        description = filter_data.get('description', 'No description provided.')
        name = filter_data.get('name')
        type_ = filter_data.get('type')

        comment = ''
        if keyword in ['id', 'type']:
            comment = '  # pylint: disable=redefined-builtin'

        keyword_description = self._format_description(
            arg=keyword.snake_case(), description=description, length=100, indent=' ' * 12
        )
        _code = [
            (
                f'{self.i1}def {keyword.snake_case()}'
                f'(self, operator: Enum, {keyword.snake_case()}: '
                f'''{self._filter_type(type_).get('hint_type')}):{comment}'''
            ),
            f'{self.i2}"""Filter {name} based on **{keyword}** keyword.',
            '',
            f'{self.i2}Args:',
            f'{self.i3}operator: The operator enum for the filter.',
            # f'{self.i3}{keyword.snake_case()}: {description}.',
            f'{self.i3}{keyword_description}',
            f'{self.i2}"""',
        ]
        # if type_.lower() in ['date']:
        #     _code.extend(
        #         [
        #             f'''{self.i2}{keyword.snake_case()} = self.utils.any_to_datetime'''
        #             f'''({keyword.snake_case()}).strftime('%Y-%m-%d')'''
        #         ]
        #     )
        if type_.lower() in ['date', 'datetime']:
            _code.extend(
                [
                    f'''{self.i2}{keyword.snake_case()} = self.utils.any_to_datetime'''
                    f'''({keyword.snake_case()}).strftime('%Y-%m-%dT%H:%M:%S')'''
                ]
            )
        _code.extend(
            [
                (
                    f'''{self.i2}self._tql.add_filter('{keyword}', operator, '''
                    f'''{keyword.snake_case()}, {self._filter_type(type_).get('tql_type')})'''
                ),
                '',
            ]
        )
        return _code

    def _gen_code_has_artifact_method(self) -> list:
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

    def _gen_code_has_case_method(self) -> list:
        """Return code for has_case TQL filter methods."""
        self._add_tql_imports()
        _code = [
            f'{self.i1}@property',
            f'{self.i1}def has_case(self):',
            f'{self.i2}"""Return **CaseFilter** for further filtering."""',
        ]
        if self.type_ != 'cases':
            _code.extend(
                [
                    f'{self.i2}# first-party',
                    f'{self.i2}from tcex.api.tc.v3.cases.case_filter import CaseFilter',
                    '',
                ]
            )
        _code.extend(
            [
                f'{self.i2}cases = CaseFilter(Tql())',
                (
                    f'''{self.i2}self._tql.add_filter('hasCase', '''
                    '''TqlOperator.EQ, cases, TqlType.SUB_QUERY)'''
                ),
                f'{self.i2}return cases',
                '',
            ]
        )
        return _code

    def _gen_code_has_group_method(self) -> list:
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

    def _gen_code_has_indicator_method(self) -> list:
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

    def _gen_code_has_note_method(self) -> list:
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

    def _gen_code_has_tag_method(self) -> list:
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

    def _gen_code_has_task_method(self) -> list:
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

    def _gen_code_has_security_label_method(self) -> list:
        """Return code for has_security_label TQL filter methods."""
        self._add_tql_imports()
        return [
            f'{self.i1}@property',
            f'{self.i1}def has_security_label(self):',
            f'{self.i2}"""Return **SecurityLabel** for further filtering."""',
            f'{self.i2}# first-party',
            (
                f'{self.i2}from tcex.api.tc.v3.security_labels.security_label_filter import '
                f'SecurityLabelFilter'
            ),
            '',
            f'{self.i2}security_labels = SecurityLabelFilter(Tql())',
            (
                f'''{self.i2}self._tql.add_filter('hasSecurityLabel', '''
                '''TqlOperator.EQ, security_labels, TqlType.SUB_QUERY)'''
            ),
            f'{self.i2}return security_labels',
            '',
        ]

    def _gen_code_has_victim_asset_method(self) -> list:
        """Return code for has_victim_asset TQL filter methods."""
        self._add_tql_imports()
        _code = [
            f'{self.i1}@property',
            f'{self.i1}def has_victim_asset(self):',
            f'{self.i2}"""Return **VictimAssetFilter** for further filtering."""',
        ]
        if self.type_ != 'victim_assets':
            _code.extend(
                [
                    f'{self.i2}# first-party',
                    (
                        f'{self.i2}from tcex.api.tc.v3.victim_assets.victim_asset_filter import '
                        f'VictimAssetFilter'
                    ),
                    '',
                ]
            )
        _code.extend(
            [
                f'{self.i2}victim_assets = VictimAssetFilter(Tql())',
                (
                    f'''{self.i2}self._tql.add_filter('hasVictimAsset', '''
                    '''TqlOperator.EQ, victim_assets, TqlType.SUB_QUERY)'''
                ),
                f'{self.i2}return victim_assets',
                '',
            ]
        )
        return _code

    def _gen_code_has_victim_method(self) -> list:
        """Return code for has_victim TQL filter methods."""
        self._add_tql_imports()
        _code = [
            f'{self.i1}@property',
            f'{self.i1}def has_victim(self):',
            f'{self.i2}"""Return **VictimFilter** for further filtering."""',
        ]
        if self.type_ != 'victims':
            _code.extend(
                [
                    f'{self.i2}# first-party',
                    f'{self.i2}from tcex.api.tc.v3.victims.victim_filter import VictimFilter',
                    '',
                ]
            )
        _code.extend(
            [
                f'{self.i2}victims = VictimFilter(Tql())',
                (
                    f'''{self.i2}self._tql.add_filter('hasVictim', '''
                    '''TqlOperator.EQ, victims, TqlType.SUB_QUERY)'''
                ),
                f'{self.i2}return victims',
                '',
            ]
        )
        return _code

    def _gen_code_has_attribute_method(self) -> list:
        """Return code for has_attribute TQL filter methods."""
        self._add_tql_imports()

        # hasAttribute filter is present on groups/indicators/ and victims.
        filter_type = 'GroupAttributeFilter'
        import_path = 'group_attributes.group_attribute_filter'
        if self.type_.lower() == 'indicators':
            filter_type = 'IndicatorAttributeFilter'
            import_path = 'indicator_attributes.indicator_attribute_filter'
        elif self.type_.lower() == 'victims':
            filter_type = 'VictimAttributeFilter'
            import_path = 'victim_attributes.victim_attribute_filter'

        return [
            f'{self.i1}@property',
            f'{self.i1}def has_attribute(self):',
            f'{self.i2}"""Return **{filter_type}** for further filtering."""',
            f'{self.i2}# first-party',
            f'{self.i2}from tcex.api.tc.v3.{import_path} import {filter_type}',
            '',
            f'{self.i2}attributes = {filter_type}(Tql())',
            (
                f'''{self.i2}self._tql.add_filter('hasAttribute', '''
                '''TqlOperator.EQ, attributes, TqlType.SUB_QUERY)'''
            ),
            f'{self.i2}return attributes',
            '',
        ]

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

        for t in sorted(self._filter_properties, key=lambda i: i['keyword']):
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
            elif keyword.snake_case() == 'has_attribute':
                _filter_class.extend(self._gen_code_has_attribute_method())
            elif keyword.snake_case() == 'has_security_label':
                _filter_class.extend(self._gen_code_has_security_label_method())
            elif keyword.snake_case() == 'has_victim':
                _filter_class.extend(self._gen_code_has_victim_method())
            elif keyword.snake_case() == 'has_victim_asset':
                _filter_class.extend(self._gen_code_has_victim_asset_method())
            else:
                _filter_class.extend(self._gen_code_generic_method(t))

        return '\n'.join(_filter_class)

    def gen_doc_string(self) -> str:
        """Generate doc string."""
        return f'"""{self.type_.singular().title()} TQL Filter"""\n'
