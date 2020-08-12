# -*- coding: utf-8 -*-
"""TcEx testing profile Class."""
# standard library
import json
import math

# import os
import re
import sys
from base64 import b64encode

# third-party
import colorama as c

# autoreset colorama
c.init(autoreset=True, strip=False)


class Interactive:
    """Testing Profile Interactive Class.

    Args:
        profile (Profile): The profile object to build interactive inputs.
    """

    def __init__(self, profile):
        """Initialize Class properties."""
        self.profile = profile

        # properties
        self._inputs = {
            'optional': {},
            'required': {},
        }
        self._no_selection_text = 'No Selection'
        self._staging_data = {'kvstore': {}}
        # self._user_defaults = None
        self.collect_type_map = {
            'Any': self.collect_string,
            'Binary': self.collect_binary,
            'BinaryArray': self.collect_binary_array,
            'KeyValue': self.collect_key_value,
            'KeyValueArray': self.collect_key_value_array,
            'String': self.collect_string,
            'StringArray': self.collect_string_array,
            'TCEntity': self.collect_tcentity,
            'TCEntityArray': self.collect_tcentity_array,
        }
        self.exit_codes = []
        self.input_type_map = {
            'boolean': self.present_boolean,
            'choice': self.present_choice,
            'keyvaluelist': self.present_key_value_list,
            'multichoice': self.present_multichoice,
            'string': self.present_string,
        }
        # self.user_defaults_filename = os.path.join('tests', '.user_defaults')

    def _default(self, data, data_type=None):  # pylint: disable=unused-argument
        """Return the best option for default."""
        if data.get('type').lower() == 'boolean':
            default = str(data.get('default', 'false')).lower()
        elif data.get('type').lower() == 'choice':
            default = 0
            valid_values = self._expand_valid_values(data.get('validValues', []))
            if data.get('name') == 'tc_action':
                for vv in valid_values:
                    if self.profile.feature.lower() == vv.replace(' ', '_').lower():
                        default = vv
                        break
            else:
                default = data.get('default')
        elif data.get('type').lower() == 'multichoice':
            default = data.get('default')
            if default is not None and isinstance(default, str):
                default = default.split('|')
        else:
            default = data.get('default')
            # if default is None:
            #     # set default from user default file
            #     default = self.user_defaults.get(data.get('name'))
        return default

    def _expand_valid_values(self, valid_values):
        """Expand supported playbook variables to their full list.

        Args:
            valid_values (list): The list of valid values for Choice or MultiChoice inputs.

        Returns:
            list: An expanded list of valid values for Choice or MultiChoice inputs.
        """
        valid_values = list(valid_values)
        if '${ARTIFACT_TYPES}' in valid_values:
            valid_values.remove('${ARTIFACT_TYPES}')
            valid_values.extend(
                [
                    'ASN',
                    'Asset Group ID',
                    'Certificate File',
                    'CIDR',
                    'Credential ID',
                    'Document Metadata',
                    'Email Address',
                    'Email Attachment File',
                    'Email Attachment File Name',
                    'Email Body',
                    'Email Message File',
                    'Email Subject',
                    'Event File',
                    'Exploit ID',
                    'File Hash',
                    'Filter ID',
                    'Hashtag',
                    'Host',
                    'Image File',
                    'IP Address',
                    'Log File',
                    'MutEx',
                    'PCAP File',
                    'Policy ID',
                    'Registry Key',
                    'Results ID',
                    'Screenshot File',
                    'Tactic ID',
                    'Technique ID',
                    'Ticket ID',
                    'Timestamp',
                    'URL',
                    'User Agent',
                    'Vulnerability Detection ID',
                    'Vulnerability ID',
                ]
            )
        elif '${GROUP_TYPES}' in valid_values:
            valid_values.remove('${GROUP_TYPES}')
            valid_values.extend(
                [
                    'Adversary',
                    'Campaign',
                    'Document',
                    'Email',
                    'Event',
                    'Incident',
                    'Intrusion Set',
                    'Signature',
                    'Task',
                    'Threat',
                ]
            )
        elif '${INDICATOR_TYPES}' in valid_values:
            valid_values.remove('${INDICATOR_TYPES}')
            r = self.profile.session.get('/v2/types/indicatorTypes')
            if r.ok:
                valid_values.extend(
                    [t.get('name') for t in r.json().get('data', {}).get('indicatorType', {})]
                )
        elif '${OWNERS}' in valid_values:
            valid_values.remove('${OWNERS}')
            r = self.profile.session.get('/v2/owners')
            if r.ok:
                valid_values.extend(
                    [o.get('name') for o in r.json().get('data', {}).get('owner', {})]
                )
        elif '${USERS}' in valid_values:
            valid_values.remove('${USERS}')
            r = self.profile.session.get('/v2/owners/mine/members')
            if r.ok:
                valid_values.extend(
                    [o.get('userName') for o in r.json().get('data', {}).get('user', {})]
                )
        elif '${USER_GROUPS}' in valid_values:
            valid_values.remove('${USER_GROUPS}')
            valid_values.extend(['User Group 1', 'User Group 1'])

        return valid_values

    def _input_value(self, label, option_text=None):
        """Return user input."""
        # update option text to include help message
        option_text = option_text or ''
        if option_text:
            # add space for cleaness in user display
            option_text = f' {option_text}'

        print(f'{c.Fore.WHITE}[? for help]')
        prompt = f'{c.Fore.MAGENTA}{label}{c.Fore.RESET}{c.Style.BRIGHT}{option_text}: '
        input_value = input(prompt).strip()  # nosec

        # handle special user inputs
        if input_value == '?':
            self.present_help()
            return self._input_value(label, option_text)

        return input_value

    @staticmethod
    def _split_list(data):
        """Split a list in two "equal" parts."""
        half = math.ceil(len(data) / 2)
        return data[:half], data[half:]

    def add_input(self, name, data, value):
        """Add an input to inputs."""
        if data.get('required', False):
            self._inputs['required'].setdefault(name, value)
        else:
            self._inputs['optional'].setdefault(name, value)

    # def add_user_default(self, key, value, data_type=None):
    #     """Add data to user default."""
    #     self.user_defaults.setdefault(self.profile.feature, {})
    #     if data_type is None:
    #         self.user_defaults[self.profile.feature][key] = value
    #     else:
    #         # store the value under the appropriate data type
    #         self.user_defaults[self.profile.feature].setdefault(key, {})
    #         self.user_defaults[self.profile.feature][key].setdefault(data_type, value)

    #     if self.user_defaults.get('base') is None:
    #         self.user_defaults['base'] = self.user_defaults[self.profile.feature]

    def add_staging_data(self, name, type_, value):
        """Create staging data and return variable value.

        Args:
            name (str): The name of the input.
            type_ (str): The type of input (Binary, StringArray, etc.)
            value (str): The value to write in the staging data.

        Returns:
            [type]: [description]
        """
        arg_value = value
        if (
            self.profile.ij.runtime_level.lower() not in ['triggerservice', 'webhooktriggerservice']
            and value is not None
        ):
            arg_value = self.profile.ij.create_variable(name, type_)
            self._staging_data['kvstore'].setdefault(arg_value, value)

        return arg_value

    def collect_binary(self, **kwargs):
        """Collect binary data

        Args:
            default (str, kwargs): The default value if no value provided by user.
            feedback (book, kwargs): If True user feedback will be printed.
            option_text (str, kwargs): The text shown to the user.
            required (str, kwargs): If True the user cannot continue until they provide a value.
        """
        input_value = self._input_value('Input', kwargs.get('option_text'))
        if not input_value:
            # if no default value and required force user to input again
            if kwargs.get('default') is None and kwargs.get('required') is True:
                self.print_required()
                return self.collect_binary(**kwargs)

        if input_value not in [None, '']:
            input_data = b64encode(input_value.encode()).decode()
            feedback = f'{input_value} -> ({input_data})'
        else:
            input_data = kwargs.get('default')
            feedback = input_data

        # print user feedback
        if kwargs.get('feedback', True):
            self.print_feedback(feedback)

        return input_data

    def collect_binary_array(self, **kwargs):
        """Collect binary array data

        Args:
            required (str, kwargs): If True the user cannot continue until they provide a value.
        """
        input_values = []
        required = kwargs.get('required', False)
        while True:
            input_value = self.collect_binary(feedback=False, required=required)
            if not input_value:
                break
            input_values.append(input_value)
            required = False  # only the first input is required

        if not input_values:
            # return None to ensure data doesn't get added to inputs
            input_values = None

        # print user feedback
        self.print_feedback(input_values)

        return input_values

    def collect_boolean(self, **kwargs):
        """Collect binary data

        Args:
            default (str, kwargs): The default value if no value provided by user.
            option_text (str, kwargs): The text shown to the user.
        """
        input_value = self._input_value('Input', kwargs.get('option_text'))
        if input_value == '':
            input_value = kwargs.get('default')

        if str(input_value).lower() not in ['0', 'f', 'false', '1', 't', 'true']:
            self.print_invalid_bool()
            return self.collect_boolean(**kwargs)

        # covert input value to a proper boolean
        input_value = self.profile.utils.to_bool(input_value)

        # print user feedback
        self.print_feedback(input_value)

        return input_value

    def collect_choice(self, **kwargs):
        """Collect choice data

        Args:
            default (str, kwargs): The default value if no value provided by user.
            option_text (str, kwargs): The text shown to the user.
            required (str, kwargs): If True the user cannot continue until they provide a value.
            valid_values (str, kwargs): A list of valid values
        """
        # collect input value from user and set default if required
        input_value = self._input_value('Choice', kwargs.get('option_text')) or kwargs.get(
            'default'
        )

        # ensure input value is provided when input is required
        if input_value is None and kwargs.get('required') is True:
            self.print_required()
            return self.collect_choice(**kwargs)

        # if input value is None then there is not need to continue
        if input_value is None:
            return input_value

        # set valid values
        valid_values = kwargs.get('valid_values', [])

        # convert to int or recollect input
        try:
            input_value = int(input_value)
        except ValueError:
            self.print_invalid_index(f'0-{len(valid_values)}')
            return self.collect_choice(**kwargs)

        # ensure input value is valid
        valid_index_values = [i for i, _ in enumerate(valid_values)]
        # valid_index_values = list(range(0, len(valid_values) - 1))
        if input_value not in valid_index_values:
            self.print_invalid_index(f'0-{len(valid_values)}')
            return self.collect_choice(**kwargs)

        # using index value provided by user, set value to valid value
        input_value = valid_values[input_value]
        if input_value == self._no_selection_text:
            # special case for when user select no selection
            input_value = None

        # print user feedback
        if kwargs.get('feedback', True):
            self.print_feedback(input_value)

        return input_value

    def collect_exit_code(self, **kwargs):
        """Collect exit codes."""
        input_value = self._input_value('Code', kwargs.get('option_text'))

        if input_value != '':
            try:
                input_value = int(input_value)
            except ValueError:
                self.print_invalid_exit_code()
                return self.collect_exit_code(**kwargs)

            if input_value not in [0, 1, 3]:
                self.print_invalid_exit_code()
                return self.collect_exit_code(**kwargs)

        return input_value

    def collect_exit_codes(self, **kwargs):
        """Collect exit codes."""
        input_values = []
        while True:
            input_value = self.collect_exit_code(**kwargs)
            if input_value == '':
                break
            input_values.append(input_value)

        if not input_values:
            # return None to ensure data doesn't get added to inputs
            input_values = [0]

        # print user feedback
        self.print_feedback(input_values)

        return input_values

    def collect_key_value(self, **kwargs):
        """Collect key value data"""
        input_value = None
        key = self._input_value('Key', option_text=kwargs.get('option_text'))

        # ensure input value is provided when input is required
        if key == '' and kwargs.get('required') is True:
            self.print_required()
            return self.collect_key_value(**kwargs)

        if key != '':
            value = self._input_value('Value')
            input_value = {'key': key, 'value': value}
        else:
            input_value = kwargs.get('default')

        # print user feedback
        if kwargs.get('feedback', True):
            self.print_feedback(input_value)

        return input_value

    def collect_key_value_array(self, **kwargs):
        """Collect key value array data"""
        input_values = []
        required = kwargs.get('required')
        while True:
            input_value = self.collect_key_value(
                default=kwargs.get('default'),
                feedback=False,
                option_test=kwargs.get('option_text'),
                required=required,
            )
            if not input_value:
                break
            input_values.append(input_value)
            required = False

        if not input_values:
            # return None to ensure data doesn't get added to inputs
            input_values = None

        # print user feedback
        self.print_feedback(input_values)

        return input_values

    def collect_multichoice(self, **kwargs):
        """Collect multichoice data"""
        input_values = []
        required = kwargs.get('required', False)
        while True:
            input_value = self.collect_choice(
                feedback=False,
                # option_text=kwargs.get('option_text'),
                required=required,
                valid_values=kwargs.get('valid_values'),
            )
            if not input_value:
                break
            input_values.append(input_value)
            required = False

        input_values = list(set(input_values))
        if input_values:
            # format multichoice value as pipe delimited string
            input_values = '|'.join(input_values)
        else:
            # return None to ensure data doesn't get added to inputs
            input_values = None

        # print user feedback
        self.print_feedback(input_values)

        return input_values

    def collect_string(self, **kwargs):
        """Collect string data

        Args:
            option_text (str, kwargs): The text shown to the user.
            default (str, kwargs): The default value if no value provided by user.
        """
        input_value = self._input_value('Input', kwargs.get('option_text', ''))
        if not input_value:
            input_value = kwargs.get('default')

        if input_value is None and kwargs.get('required', False) is True:
            self.print_required()
            return self.collect_string(**kwargs)

        # print user feedback
        if kwargs.get('feedback', True):
            self.print_feedback(input_value)

        # APP-622 - handle null/None values
        if input_value == 'null':
            input_value = None
        elif input_value in ['"null"', "'null'"]:
            input_value = 'null'

        return input_value

    def collect_string_array(self, **kwargs):
        """Collect string array data"""
        input_values = []
        required = kwargs.get('required', False)
        while True:
            input_value = self.collect_string(feedback=False, required=required)
            if not input_value:
                break
            input_values.append(input_value)
            required = False

        if not input_values:
            # return None to ensure data doesn't get added to inputs
            input_values = None

        # print user feedback
        self.print_feedback(input_values)

        return input_values

    def collect_tcentity(self, **kwargs):
        """Collect tcentity data"""
        input_value = None
        id_ = self._input_value('ID')
        if id_:
            value = self._input_value('Value')
            type_ = self._input_value('Type')
            input_value = {'id': id_, 'value': value, 'type': type_}

        if input_value is None and kwargs.get('required', False) is True:
            self.print_required()
            return self.collect_tcentity(**kwargs)

        # print user feedback
        if kwargs.get('feedback', True):
            self.print_feedback(input_value)

        return input_value

    def collect_tcentity_array(self, **kwargs):
        """Collect tcentity array data"""
        input_values = []
        required = kwargs.get('required', False)
        while True:
            input_value = self.collect_tcentity(feedback=False, required=required)
            if not input_value:
                break
            input_values.append(input_value)
            required = False

        if not input_values:
            # return None to ensure data doesn't get added to inputs
            input_values = None

        # print user feedback
        self.print_feedback(input_values)

        return input_values

    @property
    def inputs(self):
        """Return inputs dict."""
        return self._inputs

    def present(self):
        """Present interactive menu to build profile."""

        def params_data():
            # handle non-layout and layout based App appropriately
            if self.profile.lj.has_layout:
                # using inputs from layout.json since they are required to be in order
                # (display field can only use inputs previously defined)
                for name in self.profile.lj.params_dict:
                    # get data from install.json based on name
                    data = self.profile.ij.params_dict.get(name)
                    yield name, data

                # hidden fields will not be in layout.json so they need to be include manually
                for name, data in self.profile.ij.filter_params_dict(hidden=True).items():
                    yield name, data
            else:
                for name, data in self.profile.ij.params_dict.items():
                    yield name, data

        inputs = {}
        for name, data in params_data():
            if data.get('serviceConfig'):
                # inputs that are serviceConfig are not applicable for profiles
                continue

            if not data.get('hidden'):
                # each input will be checked for permutations if the App has layout and not hidden
                if not self.profile.permutations.validate_input_variable(name, inputs):
                    continue

            # present the input
            value = self.input_type_map.get(data.get('type').lower())(name, data)

            # update inputs
            inputs[name] = value

        self.present_exit_code()

    def present_boolean(self, name, data):
        """Build a question for boolean input."""
        # print header information
        self.print_header(data)

        default = self._default(data)
        valid_values = ['true', 'false']

        option_default = 'false'
        option_text = ''
        options = []
        for v in valid_values:
            if v.lower() == default.lower():
                option_default = v
                v = f'[{v}]'
            options.append(v)
        option_text = f'''({'/'.join(options)})'''

        value = self.collect_boolean(default=option_default, option_text=option_text)

        # add input
        self.add_input(name, data, value)

        return value

    def present_choice(self, name, data):
        """Build a question for choice input."""
        # print header information
        self.print_header(data)

        default = self._default(data)
        option_index = 0
        valid_values = self._expand_valid_values(data.get('validValues', []))
        if data.get('required', False) is False:
            # add option to invalidate defaults
            valid_values.insert(0, self._no_selection_text)

        # default value needs to be converted to index
        if default:
            try:
                option_index = valid_values.index(default)
            except ValueError:
                # if "magic" variable (e.g., ${GROUP_TYPES}) was not expanded then use index 0.
                # there is no way to tell if the default value is be part of the expansion.
                if any([re.match(r'^\${.*}$', v) for v in valid_values]):
                    option_index = 0
                else:
                    print(
                        f'''{c.Fore.RED}Invalid value of ({default}) for {data.get('name')}, '''
                        'check that default value and validValues match in install.json.'
                    )
                    sys.exit()
        option_text = f'[{option_index}]'

        # build options list to display to the user in two columns
        options = []
        for i, v in enumerate(valid_values):
            options.append(f'{i}. {v}')

        # display options list into two columns
        left, right = self._split_list(options)
        for i, _ in enumerate(left):
            ld = left[i]
            try:
                rd = right[i]
            except IndexError:
                rd = ''
            print(f'{ld:40} {rd:40}')

        # collect user input
        value = self.collect_choice(
            default=option_index, option_text=option_text, valid_values=valid_values
        )

        # add input
        self.add_input(name, data, value)

        return value

    def present_data_types(self, data_types, required=False):
        """Present data types options.

        Args:
            data_types (list): A list of optional data types.
            required (bool): If False the no selection option will be added.
        """
        if 'Any' in data_types:
            data_types = [
                'Binary',
                'BinaryArray',
                'KeyValue',
                'KeyValueArray',
                'String',
                'StringArray',
                'TCEntity',
                'TCEntityArray',
            ]

        # add option to not select an index value if input is not required
        if required is False:
            data_types.insert(0, self._no_selection_text)

        # build options list to display to the user in two columns
        options = []
        for i, v in enumerate(data_types):
            options.append(f'{i}. {v}')

        left, right = self._split_list(options)
        for i, _ in enumerate(left):
            ld = left[i]
            try:
                rd = right[i]
            except IndexError:
                rd = ''
            print(f'{ld:40} {rd:40}')

        index = self._input_value('Type', '[0]') or 0

        try:
            data_type = data_types[int(index)]
        except (IndexError, TypeError, ValueError):
            print(
                f'{c.Fore.RED}Invalid index of {index} provided. '
                f'Please provide a integer between 0-{len(data_types) - 1}'
            )
            sys.exit(1)

        return data_type

    def present_exit_code(self):
        """Provide user input for exit code."""
        self.print_header({'label': 'Exit Codes'})
        self.exit_codes = list(set(self.collect_exit_codes(default=[0], option_text='[0]')))

    @staticmethod
    def present_help():
        """Provide user help information."""
        print(
            f'{c.Fore.CYAN}For String type inputs: \n'
            ' * A value of null will be treated as an actual null value.\n'
            ' * Using "null" or \'null\' to insert a string of null.\n'
        )
        print(f'{c.Fore.CYAN}When done entering array data press enter to continue.')

    def present_key_value_list(self, name, data):
        """Build a question for key value list input."""
        # print header information
        self.print_header(data)

        # the default value from install.json or user_data
        default = self._default(data)  # array of default values

        # collect input
        input_data = self.collect_key_value_array(default=default, required=data.get('required'))

        # create variable
        variable = self.add_staging_data(name, 'KeyValueArray', input_data)

        # add input to args
        self.add_input(name, data, variable)

        # user feedback
        feedback_data = input_data
        if input_data is not None:
            feedback_data = json.dumps(feedback_data)

        # # update default
        # if default is None:
        #     self.add_user_default(name, input_data)

        return variable

    def present_multichoice(self, name, data):
        """Build a question for choice input."""
        # print header information
        self.print_header(data)

        default = self._default(data)  # array of default values
        option_indexes = [0]
        valid_values = self._expand_valid_values(data.get('validValues', []))
        if data.get('required', False) is False:
            # add option to invalidate defaults
            valid_values.insert(0, self._no_selection_text)

        # default values will be return as an array (e.g., one|two -> ['one'. 'two']).
        # using the valid values array we can look up these values to show as default in input.
        if default:
            option_indexes = []
            for d in default:
                try:
                    option_indexes.append(valid_values.index(d))
                except ValueError:
                    # if "magic" variable (e.g., ${GROUP_TYPES}) was not expanded then skip value.
                    # there is no way to tell if the default value is be part of the expansion.
                    if any([re.match(r'^\${.*}$', v) for v in valid_values]):
                        continue

                    print(
                        f'''{c.Fore.RED}Invalid value of ({d}) for {data.get('name')}, check '''
                        'that default value(s) and validValues match in install.json.'
                    )
                    sys.exit()
        option_text = f''' [{','.join([str(v) for v in option_indexes])}]'''

        # build options list to display to the user in two columns
        options = []
        for i, v in enumerate(valid_values):
            options.append(f'{i}. {v}')

        # display options list into two columns
        left, right = self._split_list(options)
        for i, _ in enumerate(left):
            ld = left[i]
            try:
                rd = right[i]
            except IndexError:
                rd = ''
            print(f'{ld:40} {rd:40}')

        # collect user input
        values = self.collect_multichoice(
            default=option_indexes,
            option_text=option_text,
            required=data.get('required'),
            valid_values=valid_values,
        )

        # add input
        self.add_input(name, data, values)

        return values

    def present_string(self, name, data):
        """Build a question for boolean input."""
        # display header information
        self.print_header(data)

        # use playbook data types to determine what input to provide (default to String)
        data_type = data.get('playbookDataType', ['String'])[0]
        if len(data.get('playbookDataType', [])) > 1 or data_type.lower() == 'any':
            data_type = self.present_data_types(
                data.get('playbookDataType'), required=data.get('required', False)
            )

        # no need to proceed if there is not valid data type selected.
        if data_type == self._no_selection_text:
            self.add_input(name, data, None)
            self.print_feedback('null')
            return None

        # the default value from install.json or user_data
        default = self._default(data, data_type)

        option_text = ''
        if default is not None:
            option_text = f'[{default}]'

        # use data_type to properly format collection input
        input_value = self.collect_type_map[data_type](
            default=default, option_text=option_text, required=data.get('required', False)
        )

        # add staging data and get variable name
        variable = self.add_staging_data(name, data_type, input_value)

        # add input
        self.add_input(name, data, variable)

        # # update default
        # if default is None:
        #     if len(data.get('playbookDataType', [])) > 1 or data_type.lower() == 'any':
        #         # for inputs that take multiple types we need to store user default with the type
        #         self.add_user_default(name, input_value, data_type)
        #     else:
        #         self.add_user_default(name, input_value)

        return variable

    @staticmethod
    def print_feedback(feedback_value):
        """Print the value used."""
        print(f'Using value: {c.Fore.GREEN}{feedback_value}\n')

    @staticmethod
    def print_header(data):
        """Enrich the header with metadata."""

        def _print_metadata(title, value):
            """Print the title and value"""
            print(f'{c.Fore.CYAN}{title!s:<22}: {c.Fore.RESET}{c.Style.BRIGHT}{value}')

        label = data.get('label', 'NO LABEL')
        print(f'\n{c.Fore.GREEN}{label}')

        # type
        _print_metadata('Type', data.get('type'))

        # default
        default = data.get('default')
        if default:
            _print_metadata('Default', default)

        # note
        note = data.get('note', '')[:200]
        if note:
            _print_metadata('Note', note)

        # required
        _print_metadata('Required', str(data.get('required', False)).lower())

        # hidden
        if data.get('hidden'):
            _print_metadata('Hidden', 'true')

        # Input Types
        pbt = ','.join(data.get('playbookDataType', []))
        if pbt:
            _print_metadata('Playbook Data Types', pbt)

        vv = ','.join(data.get('validValues', []))
        if vv:
            _print_metadata('Valid Values', vv)

        print('-' * 50)

    @staticmethod
    def print_invalid_bool():
        """Print a invalid bool error."""
        print(f'{c.Fore.RED}The provided value is not a boolean value (true/false).\n')

    @staticmethod
    def print_invalid_exit_code():
        """Print a invalid exit code error."""
        print(f'{c.Fore.RED}The provided value is not a valid exit code (0, 1).\n')

    @staticmethod
    def print_invalid_index(range_):
        """Print a invalid index error."""
        print(
            f'{c.Fore.RED}The provided index value is not '
            f'valid, please select a valid value between {range_}.\n'
        )

    @staticmethod
    def print_required():
        """Print a required error."""
        print(f'{c.Fore.RED}This input is required, please enter an appropriate value.\n')

    @property
    def staging_data(self):
        """Return staging data dict."""
        return self._staging_data

    # @property
    # def user_defaults(self):
    #     """Return user defaults"""
    #     if self._user_defaults is None:
    #         user_defaults = {}
    #         if os.path.isfile(self.user_defaults_filename):
    #             with open(self.user_defaults_filename, 'r') as fh:
    #                 user_defaults = json.load(fh)

    #         # use feature defaults
    #         self._user_defaults = user_defaults.get(self.profile.feature)
    #         if self._user_defaults is None:
    #             # use base defaults if not feature defaults found
    #             self._user_defaults = user_defaults.get('base', {})

    #     return self._user_defaults
