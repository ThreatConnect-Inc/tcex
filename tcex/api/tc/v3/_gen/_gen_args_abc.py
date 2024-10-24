"""TcEx Framework Module"""

# standard library
import importlib
from abc import ABC
from typing import Any

# first-party
from tcex.api.tc.v3._gen._gen_abc import GenerateABC
from tcex.util.render.render import Render


class GenerateArgsABC(GenerateABC, ABC):
    """Generate docstring for Model."""

    def __init__(self, type_: Any):
        """Initialize instance properties."""
        super().__init__(type_)

    @staticmethod
    def _import_model(module: Any, class_name: str) -> Any:
        """Import the appropriate model."""
        return getattr(importlib.import_module(module), class_name)

    def _prop_type(self, prop_data: dict[str, dict | str | None]) -> str | None:
        """Return the appropriate arg type."""
        prop_type = None
        if 'type' in prop_data and prop_data.get('type') is not None:
            prop_type = self._prop_type_map(prop_data.get('type'))  # type: ignore
        elif 'allOf' in prop_data and prop_data.get('allOf'):
            ref: str = prop_data.get('allOf')[0].get('$ref')  # type: ignore
            prop_type = ref.split('/')[-1].replace('Model', '')
        elif 'items' in prop_data and prop_data.get('items'):
            ref: str = prop_data.get('items', {}).get('$ref')  # type: ignore
            prop_type = ref.split('/')[-1].replace('Model', '')
        return prop_type

    @staticmethod
    def _prop_type_map(prop_type: str) -> str:
        """Return hint type."""
        _prop_types = {
            'boolean': 'bool',
            'integer': 'int',
            'string': 'str',
        }
        return _prop_types.get(prop_type, prop_type)

    def gen_args(
        self,
        i1: str | None = None,
        i2: str | None = None,
        updatable: bool = True,
    ) -> str:
        """Model Map"""
        i1 = i1 or self.i1
        i2 = i2 or self.i2

        module_import_data = self._module_import_data(self.type_)
        model = self._import_model(
            module_import_data['model_module'], module_import_data['model_class']
        )
        _doc_string = [f'{i1}Args:']

        # get properties from schema
        schema = model.schema(by_alias=False)
        properties = {}
        if '$ref' in schema:
            model_name = schema.get('$ref').split('/')[-1]
            properties = schema.get('definitions').get(model_name).get('properties')
        elif 'properties' in schema:
            properties = schema.get('properties')
        else:
            Render.panel.failure(model.schema_json(by_alias=False))

        # iterate over properties to build docstring
        for arg, prop_data in properties.items():
            # for all doc string read-only args should not be included.
            if prop_data.get('read_only', False) is True:
                continue

            # for add_xxx method doc string non-updatable args should not be included.
            if updatable is False and prop_data.get('updatable', True) is False:
                continue

            # get arg type
            prop_type = self._prop_type(prop_data)

            # arg
            _arg_doc = f'{arg} ({prop_type}, kwargs)'

            # description
            description = prop_data.get('description')
            _arg_doc = self._format_description(
                arg=_arg_doc,
                description=description,
                length=100,
                indent=' ' * len(i2),
            )

            # add arg to doc string
            _doc_string.append(f'{i2}{_arg_doc}')

        if len(_doc_string) > 1:
            return '\n'.join(_doc_string)
        return ''
