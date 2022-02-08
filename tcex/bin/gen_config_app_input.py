"""TcEx Generate Configurations CLI Command"""
# standard library
import os
import re
from typing import List, Optional, Tuple

# first-party
import tcex.input.field_types as FieldTypes  # noqa: N812
from tcex.app_config.models.install_json_model import ParamsModel
from tcex.app_config.permutation import Permutation
from tcex.backports import cached_property
from tcex.bin.bin_abc import BinABC
from tcex.bin.gen_config_app_input_map import app_input_map


class GenConfigAppInput(BinABC):
    """Generate App Config File"""

    def __init__(self) -> None:
        """Initialize class properties."""
        super().__init__()

        # properties
        self._app_inputs_data = None
        self.class_model_map = {}
        self.field_type_modules = set()
        self.filename = 'app_inputs.py'
        self.typing_modules = {'Optional'}
        self.pydantic_modules = {'BaseModel'}
        self.permutations = Permutation()
        self.report_mismatch = []

    def _add_action_classes(self) -> None:
        """Add actions to the App."""
        for action in self._tc_actions:
            class_name = self._gen_tc_action_class_name(action)
            self.class_model_map[action] = class_name
            self._app_inputs_data[class_name] = {}

    def _add_input_to_action_class(
        self, param_data: 'ParamsModel', tc_action: Optional[str] = None
    ) -> None:
        """Add input data to Action class."""
        tc_action_class = self._gen_tc_action_class_name(tc_action) or 'AppBaseModel'
        self.app_inputs_data[tc_action_class][param_data.name] = param_data

    @property
    def _code_app_inputs_class(self) -> list:
        """Return app_inputs.py AppInput class."""
        class_model_map = ''
        for action, class_name in self.class_model_map.items():
            class_model_map += f'\'{action}\': {class_name},'
        class_model_map = f'{{{class_model_map}}}'
        return [
            '''class AppInputs:''',
            f'''{self.i1}"""App Inputs"""''',
            '',
            f'''{self.i1}def __init__(self, inputs: 'BaseModel') -> None:''',
            f'''{self.i2}"""Initialize class properties."""''',
            f'''{self.i2}self.inputs = inputs''',
            '',
            f'''{self.i1}def get_model(self, tc_action: Optional[str] = None) -> 'BaseModel':''',
            f'''{self.i2}"""Return the model based on the current action."""''',
            f'''{self.i2}tc_action = tc_action or self.inputs.model_unresolved.tc_action''',
            f'''{self.i2}action_model_map = {class_model_map}''',
            f'''{self.i2}return action_model_map.get(tc_action)''',
            '',
            f'''{self.i1}def update_inputs(self) -> None:''',
            f'''{self.i2}"""Add custom App models to inputs.''',
            '',
            f'''{self.i2}Input will be validate when the model is added an any exceptions will''',
            f'''{self.i2}cause the App to exit with a status code of 1.''',
            f'''{self.i2}"""''',
            f'''{self.i2}self.inputs.add_model(self.get_model())''',
            '',
            '',
        ]

    @property
    def _code_app_inputs_prefix(self) -> list:
        """Return app_inputs.py prefix data."""
        field_types_modules = ', '.join(sorted(list(self.field_type_modules)))
        pydantic_modules = ', '.join(sorted(list(self.pydantic_modules)))
        typing_modules = ', '.join(sorted(list(self.typing_modules)))
        return [
            '"""App Inputs"""',
            '# pylint: disable=no-self-argument, no-self-use',
            '# standard library',
            f'from typing import {typing_modules}',
            '',
            '# third-party',
            f'from pydantic import {pydantic_modules}',
            f'from tcex.input.field_types import {field_types_modules}',
            '',
            '',
        ]

    @property
    def _code_app_inputs_data(self) -> None:
        """Return app_inputs.py input data."""
        _code = []
        # sorting of the inputs can only be done at this point
        for class_name, class_inputs in self.app_inputs_data.items():
            # determine the base class for the current action class
            base_class = 'AppBaseModel'
            class_comment = f'{self.i1}"""Action Model"""'
            if class_name == 'AppBaseModel':
                base_class = 'BaseModel'
                class_comment = (
                    f'{self.i1}"""Base model for the App containing any common inputs."""'
                )

            _code.extend(
                [
                    f'class {class_name}({base_class}):',
                    f'{class_comment}' '',
                ]
            )
            _always_array = []
            _entity_input = []
            for input_name, input_data in sorted(class_inputs.items()):
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
            return f'{self.i1}# {comment}'
        return None

    def _extract_tc_action_clause(self, display_clause: Optional[str]) -> Optional[str]:
        """Extract the tc_action part of the display clause."""
        if display_clause is not None:
            # action_clause_extract_pattern = r'''tc_action\sin\s\('.*'\)'''
            action_clause_extract_pattern = r'(tc_action\sin\s\([^\)]*\))'
            _tc_action_clause = re.search(
                action_clause_extract_pattern, display_clause, re.IGNORECASE
            )
            if _tc_action_clause is not None:
                self.log.debug(f'action=extract-action-clause, display-clause={display_clause}')
                return _tc_action_clause.group(1)
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
        # type_pattern = r'(\w+)(?:.*)?'
        # extract_type = re.search(type_pattern, type_data)
        # if extract_type is not None:
        #     return extract_type.group(1)
        # return type_data
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
        union_extract_pattern = r'Union\[\(?(.*)\)\]'
        extracted_data = re.search(union_extract_pattern, type_data)
        if extracted_data is not None:
            type_data = extracted_data.group(1)
            self.log.debug(f'action=extract-type-from-union, type-data={type_data}')
            return extracted_data.group(1)
        return type_data

    def _generate_app_inputs_to_action(self) -> None:
        """Generate App Input dict from install.json and layout.json."""
        if not self.lj.has_layout:
            # process Apps WITHOUT a layout.json file
            for ij_data in self.ij.model.params_dict.values:
                self._add_input_to_action_class(ij_data)
        else:
            # TODO: handle Service Apps

            # process Apps WITH a layout.json file
            for tc_action in self._tc_actions:
                if tc_action == 'Advanced Request':
                    # AdvancedRequestModel is included in tcex
                    continue

                for ij_data in self._params_data:
                    display = self._extract_tc_action_clause(
                        self.lj.model.get_param(ij_data.name).display
                    )
                    self.log.debug(f'input-name={ij_data.name}, display={display}')

                    if display is None or ij_data.hidden is True:
                        # when there is no display clause or the input is hidden,
                        # then the input gets added to the AppBaseModel
                        self._add_input_to_action_class(ij_data)
                    elif ij_data.service_config:
                        # inputs that are serviceConfig are not applicable for profiles
                        continue
                    elif self.permutations.validate_input_variable(
                        ij_data.name, {'tc_action': tc_action}, display
                    ):
                        # each input will be checked for permutations
                        # if the App has layout and not hidden
                        self._add_input_to_action_class(ij_data, tc_action)

    @staticmethod
    def _gen_tc_action_class_name(tc_action: str) -> str:
        """Format the action to a proper class name."""
        if tc_action is not None:
            _parts = tc_action.replace('_', ' ').split(' ')
            return ''.join([f'{p.title()}' for p in _parts]) + 'Model'
        return tc_action

    def _gen_type(self, class_name: str, input_data: 'ParamsModel') -> str:
        """Determine the type value for the current input."""
        field_types = []

        # get map lookup key
        lookup_key = input_data.type
        required_key = 'optional' if input_data.required is False else 'required'
        if input_data.encrypt is True:
            lookup_key = 'Encrypt'

        # get the type value and field type
        if input_data.type == 'Boolean':
            type_ = 'bool'
        elif (
            input_data.encrypt is False
            and input_data.type == 'String'
            and input_data.playbook_data_type is not None
        ):
            type_, field_types = self._gen_type_from_playbook_data_type(
                required_key, input_data.playbook_data_type
            )
        else:
            try:
                type_ = app_input_map[lookup_key][required_key]['type']
                field_types = [app_input_map[lookup_key][required_key]['field_type']]
            except AttributeError as ex:
                self.print_failure(f'Failed looking up type data for {lookup_key} ({ex}).')

        # wrap type data in Optional for non-required inputs
        if input_data.required is False and input_data.type not in ('Boolean'):
            self.typing_modules.add('Optional')
            type_ = f'Optional[{type_}]'

        # append default if one exists
        if input_data.default is not None and input_data.type in ('Choice', 'String'):
            type_ += f' = \'{input_data.default}\''
        elif input_data.type == 'Boolean':
            type_ += ' = False'

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

        return type_

    def _gen_type_from_playbook_data_type(
        self, required_key: str, playbook_data_types: List[str]
    ) -> Tuple[str, List[str]]:
        """Return type based on playbook data type."""
        # TODO: what to do with Any Playbook Data Type?
        if 'Any' in playbook_data_types:
            self.typing_modules.add('Any')

        if len(playbook_data_types) == 1:
            _field_types = [app_input_map[playbook_data_types[0]][required_key]['field_type']]
            _types = app_input_map[playbook_data_types[0]][required_key]['type']
        else:
            # more than one type, so add Union
            self.typing_modules.add('Union')

            _types = []
            _field_types = []
            for lookup_key in playbook_data_types:
                _field_types.append(app_input_map[lookup_key][required_key]['field_type'])
                _types.append(app_input_map[lookup_key][required_key]['type'])
            _types = f'''Union[{', '.join(_types)}]'''

        return _types, _field_types

    def _get_current_type(self, class_name: str, input_name: str) -> str:
        """Return the type from the current app_input.py file if found."""
        # Testing
        #
        # instead of parsing the code it would interesting if the type was able to be
        # pulled from the Pydantic model. below is an example of how this may be possible.
        # however, it does not seem to be possible to get the original typing string.
        # if os.path.isfile('app_inputs.py'):
        #     import importlib.util

        #     spec = importlib.util.spec_from_file_location(
        #         'app_inputs', os.path.join('app_inputs.py')
        #     )
        #     foo = importlib.util.module_from_spec(spec)
        #     spec.loader.exec_module(foo)
        #     # print('dir', dir(foo.Action1Model.__fields__['string_required']))
        #     print('_type', foo.Action1Model.__fields__['string_required'].type_)
        #     print('_type_display', foo.Action1Model.__fields__['string_required']._type_display())

        # Try to capture the value from the specific class first. If not
        # found, search the entire app_inputs.py file.
        type_defintion = (
            self.utils.find_line_in_code(
                needle=rf'\s+{input_name}: ',
                code=self.app_inputs_contents,
                trigger_start=rf'^class {class_name}',
                trigger_stop=r'^class ',
            )
            or self.utils.find_line_in_code(needle=f'{input_name}: ', code=self.app_inputs_contents)
        )
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

    @property
    def _params_data(self) -> Tuple[str, 'ParamsModel']:
        """Return param data."""
        # using inputs from layout.json since they are required to be in order
        # (display field can only use inputs previously defined)
        for input_name in self.lj.model.params:
            # get data from install.json based on name
            ij_data = self.ij.model.get_param(input_name)
            yield ij_data

        # hidden fields will not be in layout.json so they need to be include manually
        for input_name, ij_data in self.ij.model.filter_params(hidden=True).items():
            yield ij_data

    @property
    def _tc_actions(self):
        """Return tc_action input valid values."""
        _tc_action = self.ij.model.get_param('tc_action')
        if isinstance(_tc_action, ParamsModel):
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
                self.typing_modules.add('List')
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
                f'{self.i1}_entity_input = validator({_entity_input}, '
                'allow_reuse=True)(entity_input(only_value=True))'
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
            self._app_inputs_data = {'AppBaseModel': {}}

            # add a model for each action (for layout based Apps)
            self._add_action_classes()
        return self._app_inputs_data

    def generate(self) -> None:
        """Generate App Config File"""
        self.log.debug('--- generate: AppConfig ---')

        # generate the App Inputs
        self._generate_app_inputs_to_action()

        # generate input code first so that imports can be added
        _code_inputs = self._code_app_inputs_data

        # create the app_inputs.py code
        code = self._code_app_inputs_prefix
        code.extend(_code_inputs)
        code.extend(self._code_app_inputs_class)
        return code
