"""TcEx Framework Module"""

# standard library
import os
from abc import ABC
from textwrap import TextWrapper

# first-party
from tcex.util import Util
from tcex.util.string_operation import SnakeString


class GenerateABC(ABC):  # noqa: B024
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
                comment = '  # CIRCULAR-IMPORT'
                _libs.append(f'{indent}# first-party')
            else:
                _libs.append(f'{indent}# {from_}')

            # manage imports as string and dicts
            _imports = []  # temp store for imports so they can be sorted
            for lib in libs:
                if isinstance(lib, dict):
                    imports = ', '.join(sorted(lib.get('imports')))  # type: ignore
                    _imports.append(f'{indent}from {lib.get("module")} import {imports}{comment}')
                elif isinstance(lib, str):
                    _imports.append(f'{indent}{lib}{comment}')
            _libs.extend(sorted(_imports))  # add imports sorted

            _libs.append('')  # add newline
        _libs.append('')  # add newline

        # This is the last part of the requirements generated.
        return '\n'.join(_libs)  # type: ignore

    def tap(self, type_: str):
        """Return the TcEx Api Path."""
        type_ = self.util.snake_string(type_)
        if type_.plural().lower() in [
            'owners',
            'owner_roles',
            'system_roles',
            'users',
            'user_groups',
            'exclusion_lists',
        ]:
            return 'tcex.api.tc.v3.security'

        if type_.plural().lower() in ['categories', 'results', 'subtypes', 'keyword_sections']:
            return 'tcex.api.tc.v3.intel_requirements'

        return 'tcex.api.tc.v3'
