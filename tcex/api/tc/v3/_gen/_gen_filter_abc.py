"""TcEx Framework Module"""

# standard library
from abc import ABC
from collections.abc import Generator
from typing import Any

# third-party
from pydantic import ValidationError
from requests.exceptions import ProxyError

# first-party
from tcex.api.tc.v3._gen._gen_abc import GenerateABC
from tcex.api.tc.v3._gen.model import FilterModel
from tcex.pleb.cached_property import cached_property
from tcex.util.render.render import Render
from tcex.util.string_operation import SnakeString


class GenerateFilterABC(GenerateABC, ABC):
    """Generate Models for Case Management Types"""

    def __init__(self, type_: SnakeString):
        """Initialize instance properties."""
        super().__init__(type_)

        # properties
        self.api_url = ''
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
    def _filter_contents(self) -> list[dict[str, Any]]:
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
            # print(r.request.method, r.request.url, r.text)
            if r.ok:
                _properties = r.json().get('data', [])
        except (ConnectionError, ProxyError) as ex:
            Render.panel.failure(f'Failed getting types properties ({ex}).')

        return _properties

    @property
    def _filter_contents_updated(self) -> list[dict[str, Any]]:
        """Update the properties contents, fixing issues in core data."""
        filters = self._filter_contents

        # Provided invalid type "BigInteger" on tql options call and correcting it to String
        for filter_ in filters:
            if self.type_ == 'indicators':
                title = 'Indicator Keyword Type'
                if filter_['keyword'] == 'addressIpval' and filter_['type'] != 'String':
                    self.messages.append(f'- [{self.type_}] - ({title}) - fix required.')
                    filter_['type'] = 'String'
                else:
                    self.messages.append(f'- [{self.type_}] - ({title}) - fix NOT required.')

            if self.type_ == 'cases' and 'description' in filter_:
                # fix misspelling in core data
                miss_map = {
                    'occured': 'occurred',
                    'Threatassess': 'ThreatAssess',
                }
                for c, w in miss_map.items():
                    if c in filter_['description']:
                        filter_['description'] = filter_['description'].replace(c, w)
        return sorted(filters, key=lambda i: i['keyword'])

    @cached_property
    def _filter_models(self) -> Generator[FilterModel, None, None]:
        for field_data in self._filter_contents_updated:
            try:
                yield FilterModel(**field_data)
            except ValidationError as ex:
                Render.panel.failure(f'Failed generating property model: data={field_data} ({ex}).')

    def _gen_code_generic_method(self, filter_data: FilterModel) -> list:
        """Return code for generic TQL filter methods."""
        keyword_description = self._format_description(
            arg=filter_data.keyword.snake_case(),
            description=filter_data.description,
            length=100,
            indent=' ' * 12,
        )
        _code = [
            (
                f'{self.i1}def {filter_data.keyword.snake_case()}'
                f'(self, operator: Enum, {filter_data.keyword.snake_case()}: '
                f'''{filter_data.extra.typing_type}):{filter_data.extra.comment}'''
            ),
            f'{self.i2}"""Filter {filter_data.name} based on **{filter_data.keyword}** keyword.',
            '',
            f'{self.i2}Args:',
            f'{self.i3}operator: The operator enum for the filter.',
            f'{self.i3}{keyword_description}',
            f'{self.i2}"""',
        ]
        if filter_data.type.lower() in ['date', 'datetime']:
            self.requirements['first-party'].extend(
                [
                    'from arrow import Arrow',
                    'from datetime import datetime',
                ]
            )
            _code.extend(
                [
                    f'''{self.i2}{filter_data.keyword.snake_case()} = self.util.any_to_datetime'''
                    f'''({filter_data.keyword.snake_case()}).strftime('%Y-%m-%d %H:%M:%S')'''
                ]
            )

        if 'list' in filter_data.extra.typing_type:
            _code.extend(
                [
                    (
                        f'''{self.i2}if isinstance({filter_data.keyword.snake_case()}, list) '''
                        '''and operator not in self.list_types:'''
                    ),
                    f'''{self.i3}raise RuntimeError('''
                    f'''{self.i5}'Operator must be CONTAINS, NOT_CONTAINS, IN\''''
                    f'''{self.i5}'or NOT_IN when filtering on a list of values.\''''
                    f'''{self.i4})''',
                    '',
                ]
            )
        _code.extend(
            [
                (
                    f'''{self.i2}self._tql.add_filter('{filter_data.keyword}', operator, '''
                    f'''{filter_data.keyword.snake_case()}, '''
                    f'''{filter_data.extra.tql_type})'''
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

    def _gen_code_has_all_tags_method(self) -> list:
        """Return code for has_tag TQL filter methods."""
        self._add_tql_imports()
        return [
            f'{self.i1}@property',
            f'{self.i1}def has_all_tags(self):',
            f'{self.i2}"""Return **TagFilter** for further filtering."""',
            f'{self.i2}# first-party',
            f'{self.i2}from tcex.api.tc.v3.tags.tag_filter import TagFilter',
            '',
            f'{self.i2}tags = TagFilter(Tql())',
            (
                f'''{self.i2}self._tql.add_filter('hasAllTags', '''
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

    def _gen_code_has_intel_requirement_method(self) -> list:
        self._add_tql_imports()
        _code = [
            f'{self.i1}@property',
            f'{self.i1}def has_intel_requirement(self):',
            f'{self.i2}"""Return **IntelRequirementFilter** for further filtering."""',
        ]
        if self.type_ != 'intel_requirements':
            _code.extend(
                [
                    f'{self.i2}# first-party',
                    (
                        f'{self.i2}from tcex.api.tc.v3.intel_requirements.intel_requirement_filter '
                        'import IntelRequirementFilter'
                    ),
                    '',
                ]
            )
        _code.extend(
            [
                f'{self.i2}intel_requirements = IntelRequirementFilter(Tql())',
                (
                    f'''{self.i2}self._tql.add_filter('hasIntelRequirement', '''
                    '''TqlOperator.EQ, intel_requirements, TqlType.SUB_QUERY)'''
                ),
                f'{self.i2}return intel_requirements',
                '',
            ]
        )
        return _code

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
        r"""Generate private class method/property.

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

        for f in self._filter_models:
            if f.keyword.snake_case() == 'has_artifact':
                _filter_class.extend(self._gen_code_has_artifact_method())
            elif f.keyword.snake_case() == 'has_case':
                _filter_class.extend(self._gen_code_has_case_method())
            elif f.keyword.snake_case() == 'has_group':
                _filter_class.extend(self._gen_code_has_group_method())
            elif f.keyword.snake_case() == 'has_indicator':
                _filter_class.extend(self._gen_code_has_indicator_method())
            elif f.keyword.snake_case() == 'has_note':
                _filter_class.extend(self._gen_code_has_note_method())
            elif f.keyword.snake_case() == 'has_tag':
                _filter_class.extend(self._gen_code_has_tag_method())
            elif f.keyword.snake_case() == 'has_all_tags':
                _filter_class.extend(self._gen_code_has_all_tags_method())
            elif f.keyword.snake_case() == 'has_task':
                _filter_class.extend(self._gen_code_has_task_method())
            elif f.keyword.snake_case() == 'has_attribute':
                _filter_class.extend(self._gen_code_has_attribute_method())
            elif f.keyword.snake_case() == 'has_security_label':
                _filter_class.extend(self._gen_code_has_security_label_method())
            elif f.keyword.snake_case() == 'has_victim':
                _filter_class.extend(self._gen_code_has_victim_method())
            elif f.keyword.snake_case() == 'has_victim_asset':
                _filter_class.extend(self._gen_code_has_victim_asset_method())
            elif f.keyword.snake_case() == 'has_intel_requirement':
                _filter_class.extend(self._gen_code_has_intel_requirement_method())
            else:
                _filter_class.extend(self._gen_code_generic_method(f))

        return '\n'.join(_filter_class)

    def gen_doc_string(self) -> str:
        """Generate doc string."""
        # return f'"""{self.type_.singular().title()} TQL Filter"""\n'
        return '"""TcEx Framework Module"""\n'
