"""Generate Docs for ThreatConnect API"""
# standard library
from abc import ABC
import sys

# third-party
from requests import Session


class GenerateDocABC(ABC):
    """Generate docstring for Model."""

    def __init__(self, type_: str) -> None:
        """Initialize class properties."""
        self.type_ = type_.value

        # properties
        self.indent = '    '

    def _arg_type_map(self, arg_type: str) -> str:
        """Return hint type."""
        arg_types = {
            'boolean': 'bool',
            'integer': 'int',
            'string': 'str',
        }
        return arg_types.get(arg_type, arg_type)

    def _format_description(self, description: str, length: int, other_used_space: int) -> str:
        """Format description for field."""
        # fix descriptions coming from core API endpoint
        if not description.endswith('.'):
            description += '.'

        # fix core descriptions that are not capitalized.
        description_words = description.split(' ')
        description = f'{description_words[0].title()} ' + ' '.join(description_words[1:])

        # return description if under length
        if len(description) < length - other_used_space:
            return f'{description}'

        # _description = [f'{self.indent * 2}Args:']
        _description = []
        indent = 3
        updated_description = ''
        for w in description.split(' '):
            if len(updated_description) + len(w) + other_used_space >= length:
                _description.append(f'{updated_description}')
                indent = 4
                other_used_space = 16
                updated_description = ''
            updated_description += f'{w} '
        _description.append(f'{self.indent * indent}{updated_description.strip()}')

        return '\n'.join(_description)

    def gen_docs(self):
        """Model Map"""
        model = self._import_model()
        _doc_string = [f'{self.indent * 2}Args:']

        # get properties from schema
        schema = model().schema(by_alias=False)
        if '$ref' in schema:
            model_name = schema.get('$ref').split('/')[-1]
            properties = schema.get('definitions').get(model_name).get('properties')
        elif 'properties' in schema:
            properties = schema.get('properties')
        else:
            print('WTH???')
            print(model().schema_json(by_alias=False))
            sys.exit()

        # iterate over properties to build docstring
        for arg, arg_data in properties.items():
            # arg
            indention = f'{self.indent * 3}'
            _arg_doc = f'{indention}{arg} '

            # type
            if 'type' in arg_data:
                arg_type = self._arg_type_map(arg_data.get('type'))
            elif 'allOf' in arg_data and arg_data.get('allOf'):
                ref = arg_data.get('allOf')[0].get('$ref')
                arg_type = ref.split('/')[-1].replace('Model', '')
            elif 'items' in arg_data and arg_data.get('items'):
                ref = arg_data.get('items').get('$ref')
                arg_type = ref.split('/')[-1].replace('Model', '')
            _arg_doc += f'({arg_type}, kwargs): '

            # read only
            read_only = arg_data.get('read_only')
            if read_only is True:
                continue
                # _arg_doc += '[read-only] '

            # description
            description = arg_data.get('description')

            # description = self._update_description(description, len(_arg_doc))
            description = self._format_description(description, 100, len(_arg_doc))
            _arg_doc += f'{description}'
            _doc_string.append(_arg_doc)

        print('\n'.join(_doc_string))
