"""TcEx Generate Configurations CLI Command"""
# standard library
import os
import re
from typing import TYPE_CHECKING, List, Optional, Tuple

# first-party
import tcex.input.field_types as FieldTypes  # noqa: N812
from tcex.app_config.permutation import Permutation
from tcex.backports import cached_property
from tcex.bin.bin_abc import BinABC
from tcex.bin.spec_tool_app_input_static import SpecToolAppInputStatic
from tcex.pleb.none_model import NoneModel

if TYPE_CHECKING:
    # first-party
    from tcex.app_config.models.install_json_model import ParamsModel


class SpecToolAppInput(BinABC):
    """Generate App Config File"""

    def __init__(self):
        """Initialize class properties."""
        super().__init__()

        # properties
        self._app_inputs_data = None
        self.class_model_map = {}
        self.field_type_modules = set()
        self.filename = 'app_inputs.py'
        self.input_static = SpecToolAppInputStatic()
        self.typing_modules = set()
        self.pydantic_modules = {'BaseModel'}
        self.permutations = Permutation(self.log)
        self.report_mismatch = []

    def _add_action_classes(self):
        """Add actions to the App."""
        for action in self._tc_actions:
            class_name = self._gen_tc_action_class_name(action)
            self.class_model_map[action] = class_name
            self._app_inputs_data[class_name] = {}

    def _add_input_to_action_class(
        self, applies_to_all: bool, param_data: 'ParamsModel', tc_action: Optional[str] = None
    ):
        """Add input data to Action class."""
        tc_action_class = 'AppBaseModel'
        if applies_to_all is False:
            tc_action_class = self._gen_tc_action_class_name(tc_action)
        self.app_inputs_data[tc_action_class][param_data.name] = param_data

    def _add_typing_import_module(self, type_: str):
        """Add the appropriate import module for typing."""
        if 'List[' in type_:
            self.typing_modules.add('List')

        if 'Optional[' in type_:
            self.typing_modules.add('Optional')

        if 'Union[' in type_:
            self.typing_modules.add('Union')

    def class_comment(self, model_class: str) -> str:
        """Return the appropriate comment for the provided class."""
        _class_comment = f'{self.i1}"""Action Model"""'
        _comment_map = {
            'AppBaseModel': self.input_static.app_base_model_class_comment,
            'ServiceConfigModel': self.input_static.service_config_model_class_comment,
            'TriggerConfigModel': self.input_static.trigger_config_model_class_comment,
        }
        return _comment_map.get(model_class, _class_comment)

    @property
    def _code_app_inputs_data(self):
        """Return app_inputs.py input data."""
        _code = []
        # sorting of the inputs can only be done at this point
        for class_name, class_inputs in self.app_inputs_data.items():
            # determine the base class for the current action class
            base_class = 'AppBaseModel'
            class_comment = self.class_comment(class_name)
            if class_name in ['AppBaseModel', 'ServiceConfigModel']:
                base_class = 'BaseModel'
            elif class_name == 'TriggerConfigModel':
                base_class = 'CreateConfigModel'

            _code.extend(
                [
                    f'class {class_name}({base_class}):',
                    f'{class_comment}',
                    '',
                ]
            )
            _always_array = []
            _entity_input = []
            for input_name, input_data in sorted(class_inputs.items()):
                # skip special inputs
                if input_name in ['tc_log_level']:
                    continue

                # add comment
                _comment = self._code_app_inputs_data_comments(input_data)
                if _comment is not None:
                    _code.append(_comment)

                # add finalized input code line
                _type_data = f'{self.i1}{input_name}: {self._gen_type(class_name, input_data)}'
                _code.append(_type_data)

                # check if validator are applicable to this input
                if self._validator_always_array_check(input_data) is True:
                    _always_array.append(f'\'{input_name}\'')

                if self._validator_entity_input_check(input_data) is True:
                    _entity_input.append(f'\'{input_name}\'')

            # validator - always_array
            if _always_array:
                self.field_type_modules.add('always_array')
                self.pydantic_modules.add('validator')
                _code.extend(self._validator_always_array(_always_array))

            # validator - entity_input
            if _entity_input:
                self.field_type_modules.add('entity_input')
                self.pydantic_modules.add('validator')
                _code.extend(self._validator_entity_input(_entity_input))

        # append 2 blank lines between classes
        _code.append('')
        _code.append('')
        return _code

    def _code_app_inputs_data_comments(self, input_data: 'ParamsModel') -> str:
        """Return comments for a single input."""
        # append comment for playbookDataTypes
        comments = []
        if input_data.playbook_data_type:
            playbook_data_type_str = '|'.join(input_data.playbook_data_type)
            comments.append(f'pbd: {playbook_data_type_str}')
        # append comment for validValues
        if input_data.valid_values:
            valid_values_str = '|'.join(input_data.valid_values)
            comments.append(f'vv: {valid_values_str}')

        if comments:
            comment = ', '.join(comments)
            comment_wrapped = self.utils.wrap_string(comment, [' ', '|'], 80).split('\n')
            return '\n'.join([f'{self.i1}# {c}' for c in comment_wrapped])
        return None

    def _extract_type_from_definition(self, input_name: str, type_definition: str) -> str:
        """Extract the type from the type definition.

        string_allow_multiple: Union[String, List[String]] -> Union[String, List[String]]
        string_intel_type: Optional[String] -> Optional[str]
        """
        input_extract_pattern = (
            # match beginning white space on line
            r'(?:^\s+)?'
            # match input name
            rf'(?:{input_name}:\s)'
            # Capture Group: greedy capture until the end of the line
            r'(.*)$'
        )
        current_type = re.search(input_extract_pattern, type_definition)
        if current_type is not None:
            self.log.debug(
                f'action=extract-type-from-definition, current-type={current_type.group(1)}'
            )
            return current_type.group(1).strip()
        return None

    def _extract_type_from_list(self, type_data: str) -> str:
        """Extract type data from Union[]."""
        # extract the type from List
        list_extract_pattern = r'^List\[(.*)\]'
        extract_from_list = re.search(list_extract_pattern, type_data)
        if extract_from_list is not None:
            self.log.debug(f'action=extract-type-from-list, type-data={type_data}')
            return extract_from_list.group(1)
        return type_data

    def _extract_type_from_method(self, type_data: str) -> str:
        """Extract type data from method (e.g. binary(min_length=2) -> binary)."""
        remove_args_pattern = r'\([^\)]*\)'
        type_data = re.sub(remove_args_pattern, '', type_data)
        self.log.debug(f'action=remove-args-pattern, types-data={type_data}')
        return type_data

    def _extract_type_from_optional(self, type_data: str) -> str:
        """Extract type data from Union[]."""
        optional_extract_pattern = r'Optional\[?(.*)\]'
        extracted_data = re.search(optional_extract_pattern, type_data)
        if extracted_data is not None:
            type_data = extracted_data.group(1)
            self.log.debug(f'action=extract-type-from-optional, type-data={type_data}')
            return extracted_data.group(1)
        return type_data

    def _extract_type_from_union(self, type_data: str) -> str:
        """Extract type data from Union[]."""
        union_extract_pattern = r'Union\[(\((.+)\)|.+)\]'
        extracted_data = re.search(union_extract_pattern, type_data)
        if extracted_data is not None:
            # return the last matched group that is not None
            type_data = [g for g in extracted_data.groups() if g is not None][-1]
            self.log.debug(f'action=extract-type-from-union, type-data={type_data}')
            return type_data
        return type_data

    def _generate_app_inputs_to_action(self):
        """Generate App Input dict from install.json and layout.json."""
        if self.ij.model.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            for ij_data in self.ij.model.params_dict.values():
                class_name = 'Trigger Config'
                if ij_data.service_config is True:
                    class_name = 'Service Config'
                self._add_input_to_action_class(False, ij_data, class_name)
        elif not self.lj.has_layout:
            # process Apps WITHOUT a layout.json file
            for ij_data in self.ij.model.params_dict.values():
                self._add_input_to_action_class(True, ij_data)
        else:
            # process Apps WITH a layout.json file
            for tc_action in self._tc_actions:
                if tc_action == 'Advanced Request':
                    # AdvancedRequestModel is included in tcex
                    continue

                # for applies_to_all, ij_data in self.permutations.inputs_by_action(tc_action):
                for input_data in self.permutations.inputs_by_action(tc_action):
                    applies_to_all = input_data.get('applies_to_all')
                    ij_data = input_data.get('input')
                    self._add_input_to_action_class(applies_to_all, ij_data, tc_action)

                    self.log.debug(
                        f'''action=inputs-to-action, input-name={ij_data.name}, '''
                        f'''applies-to-all={applies_to_all}'''
                    )

    @staticmethod
    def _gen_tc_action_class_name(tc_action: str) -> str:
        """Format the action to a proper class name."""
        if tc_action is not None:
            # split to make pascal case
            _parts = [p.title() for p in tc_action.replace('_', ' ').split(' ')]

            # title case each word
            tc_action = ''.join([f'{p.title()}' for p in _parts]) + 'Model'

            # remove all non-alphanumeric characters and underscores
            tc_action = re.sub(r'[^a-zA-Z0-9]', '', tc_action)
        return tc_action

    def _gen_type(self, class_name: str, input_data: 'ParamsModel') -> str:
        """Determine the type value for the current input."""
        field_types = []

        # get map lookup key
        lookup_key = input_data.type
        required_key = 'optional' if input_data.required is False else 'required'
        if input_data.encrypt is True:
            lookup_key = 'Encrypt'

        # lookup input name in standards map to get pre-defined type.
        standard_name_type = self._standard_field_to_type_map(input_data.name)

        # get the type value and field type
        if standard_name_type is not None:
            type_ = standard_name_type.get('type')
            field_types.append(standard_name_type.get('field_type'))
        elif input_data.type == 'Boolean':
            type_ = 'bool'
        elif (
            input_data.encrypt is False
            and input_data.type == 'String'
            and input_data.playbook_data_type not in [[], None]
        ):
            type_, field_types = self._gen_type_from_playbook_data_type(
                required_key, input_data.playbook_data_type
            )
        else:
            try:
                type_ = self.input_static.type_map[lookup_key][required_key]['type']
                field_types = [self.input_static.type_map[lookup_key][required_key]['field_type']]
            except (AttributeError, KeyError) as ex:
                self.print_failure(f'Failed looking up type data for {input_data.type} ({ex}).')

        # wrap type data in Optional for non-required inputs
        if input_data.required is False and input_data.type not in ('Boolean'):
            type_ = f'Optional[{type_}]'

        # append default if one exists
        # if input_data.default is not None and input_data.type in ('Choice', 'String'):
        #     type_ += f' = \'{input_data.default}\''
        if input_data.type == 'Boolean':
            type_ += f' = {input_data.default or False}'

        # get the current value from the app_inputs.py file
        current_type = self._get_current_type(class_name, input_data.name)
        if current_type is not None and current_type != type_:
            self.report_mismatch.append(
                f'{input_data.name} -> calculated-type="{type_}" does '
                f'not match current-type="{current_type}"'
            )
            self.log.warning(
                f'input={input_data.name}, current-type={current_type}, '
                f'calculated-type={type_}, using=current-type'
            )
            field_types = self._get_current_field_types(current_type)
            type_ = current_type

        # add field types for import
        for field_type in field_types:
            if field_type is not None:
                # only add the field type if it is a defined field type
                if hasattr(FieldTypes, field_type):
                    self.field_type_modules.add(field_type)

        # add import data
        self._add_typing_import_module(type_)

        return type_

    def _gen_type_from_playbook_data_type(
        self, required_key: str, playbook_data_types: List[str]
    ) -> Tuple[str, List[str]]:
        """Return type based on playbook data type."""
        # TODO: what to do with Any Playbook Data Type?
        if 'Any' in playbook_data_types:
            self.typing_modules.add('Any')

        if len(playbook_data_types) == 1:
            _field_types = [
                self.input_static.type_map[playbook_data_types[0]][required_key]['field_type']
            ]
            _types = self.input_static.type_map[playbook_data_types[0]][required_key]['type']
        else:
            _types = []
            _field_types = []
            for lookup_key in playbook_data_types:
                _field_types.append(
                    self.input_static.type_map[lookup_key][required_key]['field_type']
                )
                _types.append(self.input_static.type_map[lookup_key][required_key]['type'])
            _types = f'''Union[{', '.join(_types)}]'''

        return _types, _field_types

    def _get_current_type(self, class_name: str, input_name: str) -> str:
        """Return the type from the current app_input.py file if found."""
        # Try to capture the value from the specific class first. If not
        # found, search the entire app_inputs.py file.
        type_defintion = self.utils.find_line_in_code(
            needle=rf'\s+{input_name}: ',
            code=self.app_inputs_contents,
            trigger_start=rf'^class {class_name}',
            trigger_stop=r'^class ',
        ) or self.utils.find_line_in_code(needle=f'{input_name}: ', code=self.app_inputs_contents)
        # type_definition -> "string_encrypt: Optional[Sensitive]"
        self.log.debug(
            f'action=find-definition, input-name={input_name}, type-definition={type_defintion}'
        )

        # parse out the actual type
        if type_defintion is not None:
            current_type = self._extract_type_from_definition(input_name, type_defintion)
            if current_type is not None:
                if 'Union' in current_type:
                    # the find method will return Union[(String, Optional[String])] that has
                    # the types as a tuple. this may be valid, but to keep the type
                    # consistent this bit of code will remove the extra ()/tuple. this
                    # needs to cover all cases, even the more complicated ones
                    # (e.g., "Optional[Union[(String, List[String])]]")
                    _types_data = self._extract_type_from_union(current_type)
                    union_original = f'Union[({_types_data})]'
                    union_replace = f'Union[{_types_data}]'
                    current_type = current_type.replace(union_original, union_replace)

                self.log.debug(
                    f'action=get-type, input-name={input_name}, current-type={current_type}'
                )
                return current_type

            self.log.warning(
                f'input found, but not matched: input={input_name}, type_defintion={type_defintion}'
            )

        return None

    def _get_current_field_types(self, current_type_data: str) -> str:
        """Return the current type from the type data (e.g., integer(gt=2) -> integer)."""
        types_data = current_type_data

        # extract the type from Union (e.g. Union[binary(), List[binary()]])
        types_data = self._extract_type_from_union(types_data)

        # extract type from method (e.g. binary(min_length=2) -> binary)
        types_data = self._extract_type_from_method(types_data)

        types = []
        for type_ in types_data.split(', '):
            # extract the type from List[]
            type_ = self._extract_type_from_list(type_)

            # extract the type from Optional[]
            type_ = self._extract_type_from_optional(type_)

            # append types
            types.append(type_)

        self.log.debug(f'current-field-types={types}, current-type-data={current_type_data}')
        return types

    @staticmethod
    def _standard_field_to_type_map(input_name: str) -> str:
        """Return the type for "standard" input fields."""
        _field_name_to_type_map = {
            'confidence_rating': {
                'type': 'integer(ge=0, le=100)',
                'field_type': 'integer',
            },
            'last_run': {
                'type': 'DateTime',
                'field_type': 'DateTime',
            },
            'max_historical_poll_start': {
                'type': 'DateTime',
                'field_type': 'DateTime',
            },
            'poll_interval': {
                'type': 'integer(gt=0)',
                'field_type': 'integer',
            },
            'threat_rating': {
                'type': 'integer(ge=0, le=5)',
                'field_type': 'integer',
            },
        }
        return _field_name_to_type_map.get(input_name)

    @property
    def _tc_actions(self):
        """Return tc_action input valid values."""
        _tc_action = self.ij.model.get_param('tc_action')
        if not isinstance(_tc_action, NoneModel):
            return _tc_action.valid_values
        return []

    def _validator_always_array(self, always_array: List[str]) -> str:
        """Return code for always_array_validator."""
        _always_array = ', '.join(always_array)
        return [
            '',
            f'{self.i1}# ensure inputs that take single and array types always return an array',
            (
                f'{self.i1}_always_array = validator({_always_array}, '
                'allow_reuse=True)(always_array())'
            ),
        ]

    def _validator_always_array_check(self, input_data: 'ParamsModel') -> bool:
        """Return True if Single and Multiple types used."""
        array_type = False
        single_type = False
        for _type in input_data.playbook_data_type:
            if _type in self.utils.variable_playbook_array_types:
                array_type = True
            elif _type in self.utils.variable_playbook_single_types:
                single_type = True

        return all([array_type, single_type])

    def _validator_entity_input(self, entity_input: List[str]) -> str:
        """Return code for always_array_validator."""
        _entity_input = ', '.join(entity_input)
        return [
            '',
            f'{self.i1}# add entity_input validator for supported types',
            (
                f'''{self.i1}_entity_input = validator({_entity_input}, '''
                '''allow_reuse=True)(entity_input(only_field='value'))'''
            ),
        ]

    @staticmethod
    def _validator_entity_input_check(input_data: 'ParamsModel') -> bool:
        """Return True if Single and Multiple types used."""
        for _type in input_data.playbook_data_type:
            if _type in ['TCEntity', 'TCEntityArray']:
                return True
        return False

    @cached_property
    def app_inputs_contents(self):  # pylint: disable=no-self-use
        """Return app_inputs.py contents."""
        if os.path.isfile('app_inputs.py'):
            with open('app_inputs.py') as f:
                return f.read()
        return ''

    @property
    def app_inputs_data(self) -> dict:
        """Return base App inputs data."""
        if self._app_inputs_data is None:
            if self.ij.model.runtime_level.lower() in [
                'triggerservice',
                'webhooktriggerservice',
            ]:
                self._app_inputs_data = {'ServiceConfigModel': {}, 'TriggerConfigModel': {}}
            else:
                self._app_inputs_data = {'AppBaseModel': {}}

            # add a model for each action (for layout based Apps)
            self._add_action_classes()
        return self._app_inputs_data

    def generate(self):
        """Generate App Config File"""
        self.log.debug('--- generate: AppConfig ---')

        # generate the App Inputs
        self._generate_app_inputs_to_action()

        # generate input code first so that imports can be added
        _code_inputs = self._code_app_inputs_data

        # create the app_inputs.py code
        code = self.input_static.template_app_inputs_prefix(
            self.field_type_modules, self.pydantic_modules, self.typing_modules
        )
        code.extend(_code_inputs)
        if not isinstance(self.ij.model.get_param('tc_action'), NoneModel):
            # the App support tc_action and should use the tc_action input class
            self.typing_modules.add('Optional')
            code.extend(self.input_static.template_app_inputs_class_tc_action(self.class_model_map))
        else:
            code.extend(self.input_static.template_app_inputs_class)
        return code
