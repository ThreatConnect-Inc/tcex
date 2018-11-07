# -*- coding: utf-8 -*-
""" TcEx Framework Playbook module """
# from builtins import int, str
import base64
import json
import re


class TcExPlaybook(object):
    """Playbook methods for accessing key value store."""

    def __init__(self, tcex):
        """Initialize the Class properties.

        Args:
            tcex (object): Instance of TcEx.
        """
        self.tcex = tcex
        self._db = None
        self._out_variables = None
        self._out_variables_type = None

        # match full variable
        self._variable_match = re.compile(r'^{}$'.format(self._variable_pattern))
        # capture variable parts (exactly a variable)
        self._variable_parse = re.compile(self._variable_pattern)
        # match embedded variables without quotes (#App:7979:variable_name!StringArray)
        self._vars_keyvalue_embedded = re.compile(
            r'(?:\"\:\s?)[^\"]?{}'.format(self._variable_pattern))

    def _parse_out_variable(self):
        """Internal method to parse the tc_playbook_out_variable arg.

        **Example Variable Format**::

            #App:1234:status!String,#App:1234:status_code!String
        """
        self._out_variables = {}
        self._out_variables_type = {}
        if self.tcex.default_args.tc_playbook_out_variables is not None:
            variables = self.tcex.default_args.tc_playbook_out_variables.strip()
            for o in variables.split(','):
                # parse the variable to get individual parts
                parsed_key = self.parse_variable(o)
                variable_name = parsed_key['name']
                variable_type = parsed_key['type']
                # store the variables in dict by name (e.g. "status_code")
                self._out_variables[variable_name] = {
                    'variable': o
                }
                # store the variables in dict by name-type (e.g. "status_code-String")
                vt_key = '{}-{}'.format(variable_name, variable_type)
                self._out_variables_type[vt_key] = {
                    'variable': o
                }

    @property
    def _variable_pattern(self):
        """Regex pattern to match and parse a playbook variable."""
        variable_pattern = r'#([A-Za-z]+)'  # match literal (#App) at beginning of String
        variable_pattern += r':([\d]+)'  # app id (:7979)
        variable_pattern += r':([A-Za-z0-9_\.\-\[\]]+)'  # variable name (:variable_name)
        variable_pattern += r'!(StringArray|BinaryArray|KeyValueArray'  # variable type (array)
        variable_pattern += r'|TCEntityArray|TCEnhancedEntityArray'  # variable type (array)
        variable_pattern += r'|String|Binary|KeyValue|TCEntity|TCEnhancedEntity'  # variable type
        variable_pattern += r'|(?:(?!String)(?!Binary)(?!KeyValue)'  # non matching for custom
        variable_pattern += r'(?!TCEntity)(?!TCEnhancedEntity)'  # non matching for custom
        variable_pattern += r'[A-Za-z0-9_-]+))'  # variable type (custom)
        return variable_pattern

    def aot_blpop(self):
        """Subscribe to AOT action channel."""
        if self.tcex.default_args.tc_playbook_db_type == 'Redis':
            try:
                self.tcex.log.info('Blocking for AOT message.')
                msg_data = self.db.blpop(
                    self.tcex.default_args.tc_action_channel,
                    timeout=self.tcex.default_args.tc_terminate_seconds)

                if msg_data is None:
                    self.tcex.exit(0, 'AOT subscription timeout reached.')

                msg_data = json.loads(msg_data[1])
                msg_type = msg_data.get('type', 'terminate')
                if msg_type == 'execute':
                    return msg_data.get('params', {})
                elif msg_type == 'terminate':
                    self.tcex.exit(0, 'Received AOT terminate message.')
                else:
                    self.tcex.log.warn('Unsupported AOT message type: ({}).'.format(
                        msg_type))
                    return self.aot_blpop()
            except Exception as e:
                self.tcex.exit(1, 'Exception during AOT subscription ({}).'.format(e))

    def aot_rpush(self, exit_code):
        """Subscribe to AOT action channel."""
        if self.tcex.default_args.tc_playbook_db_type == 'Redis':
            try:
                self.db.rpush(self.tcex.default_args.tc_exit_channel, exit_code)
            except Exception as e:
                self.tcex.exit(1, 'Exception during AOT exit push ({}).'.format(e))

    def check_output_variable(self, variable):
        """Check to see if output variable was requested by downstream app.

        Using the auto generated dictionary of output variables check to see if provided
        variable was requested by downstream app.

        Args:
            variable (string): The variable name, not the full variable.

        Returns:
            (boolean): Boolean value indicator whether a match was found.
        """
        match = False
        if variable in self.out_variables:
            match = True
        return match

    def create(self, key, value):
        """Create method of CRUD operation for working with KeyValue DB.

        This method will automatically determine the variable type and
        call the appropriate method to write the data.  If a non standard
        type is provided the data will be written as RAW data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result string of DB write.
        """
        data = None
        if key is not None:
            key = key.strip()
            self.tcex.log.debug(u'create variable {}'.format(key))
            # bcs - only for debugging or binary might cause issues
            # self.tcex.log.debug(u'variable value: {}'.format(value))
            parsed_key = self.parse_variable(key.strip())
            variable_type = parsed_key['type']
            if variable_type in self.read_data_types:
                data = self.create_data_types[variable_type](key, value)
            else:
                data = self.create_raw(key, value)
        return data

    @property
    def create_data_types(self):
        """Map of standard playbook variable types to create method."""
        return {
            'Binary': self.create_binary,
            'BinaryArray': self.create_binary_array,
            'KeyValue': self.create_key_value,
            'KeyValueArray': self.create_key_value_array,
            'String': self.create_string,
            'StringArray': self.create_string_array,
            'TCEntity': self.create_tc_entity,
            'TCEntityArray': self.create_tc_entity_array
        }

    def create_output(self, key, value, variable_type=None):
        """Wrapper for Create method of CRUD operation for working with KeyValue DB.

        This method will automatically check to see if provided variable was requested by
        a downstream app and if so create the data in the KeyValue DB.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.
            variable_type (string): The variable type being written.

        Returns:
            (string): Result string of DB write.
        """
        results = None
        if key is not None:
            key = key.strip()
            key_type = '{}-{}'.format(key, variable_type)
            if self.out_variables_type.get(key_type) is not None:
                # variable key-type has been requested
                v = self.out_variables_type.get(key_type)
                self.tcex.log.info(
                    u'Variable {} was requested by downstream app.'.format(v.get('variable')))
                if value is not None:
                    results = self.create(v.get('variable'), value)
                else:
                    self.tcex.log.info(
                        u'Variable {} has a none value and will not be written.'.format(key))
            elif self.out_variables.get(key) is not None and variable_type is None:
                # variable key has been requested
                v = self.out_variables.get(key)
                self.tcex.log.info(
                    u'Variable {} was requested by downstream app.'.format(v.get('variable')))
                if value is not None:
                    results = self.create(v.get('variable'), value)
                else:
                    self.tcex.log.info(
                        u'Variable {} has a none value and will not be written.'.format(
                            v.get('variable')))
            else:
                var_value = key
                if variable_type is not None:
                    var_value = key_type
                self.tcex.log.info(
                    u'Variable {} was NOT requested by downstream app.'.format(var_value))
        return results

    @property
    def db(self):
        """Return the correct KV store for this execution."""
        if self._db is None:
            if self.tcex.default_args.tc_playbook_db_type == 'Redis':
                from .tcex_redis import TcExRedis
                self._db = TcExRedis(
                    self.tcex.default_args.tc_playbook_db_path,
                    self.tcex.default_args.tc_playbook_db_port,
                    self.tcex.default_args.tc_playbook_db_context
                )
            elif self.tcex.default_args.tc_playbook_db_type == 'TCKeyValueAPI':
                from .tcex_key_value import TcExKeyValue
                self._db = TcExKeyValue(self.tcex)
            else:
                err = u'Invalid DB Type: ({})'.format(self.tcex.default_args.tc_playbook_db_type)
                raise RuntimeError(err)
        return self._db

    def delete(self, key):
        """Delete method of CRUD operation for all data types.

        Args:
            key (string): The variable to write to the DB.

        Returns:
            (string): Result of DB write.
        """
        data = None
        if key is not None:
            data = self.db.delete(key.strip())
        else:
            self.tcex.log.warning(u'The key field was None.')
        return data

    def exit(self, code=None, msg=None):
        """Playbook wrapper on TcEx exit method

        Playbooks do not support partial failures so we change the exit method from 3 to 1 and call
        it a partial success instead.

        Args:
            code (Optional [integer]): The exit code value for the app.
        """
        if code is None:
            code = self.tcex.exit_code
            if code == 3:
                self.tcex.log.info(u'Changing exit code from 3 to 0.')
                code = 0  # playbooks doesn't support partial failure
        elif code not in [0, 1]:
            code = 1
        self.tcex.exit(code, msg)

    @property
    def out_variables(self):
        """Return output variables stored as name dict."""
        if self._out_variables is None:
            # parse out variable
            self._parse_out_variable()
        return self._out_variables

    @property
    def out_variables_type(self):
        """Return output variables stored as name-type dict."""
        if self._out_variables_type is None:
            # parse out variable
            self._parse_out_variable()
        return self._out_variables_type

    def parse_variable(self, variable):
        """Method to parse an input or output variable.

        **Example Variable**::

        #App:1234:output!String

        Args:
            variable (string): The variable name to parse.

        Returns:
            (dictionary): Result of parsed string.
        """
        data = None
        if variable is not None:
            variable = variable.strip()
            if re.match(self._variable_match, variable):
                var = re.search(self._variable_parse, variable)
                data = {
                    'root': var.group(0),
                    'job_id': var.group(2),
                    'name': var.group(3),
                    'type': var.group(4)
                }
        return data

    def read(self, key, array=False, embedded=True):
        """Read method of CRUD operation for working with KeyValue DB.

        This method will automatically check to see if a single variable is passed
        or if "mixed" data is passed and return the results from the DB. It will also
        automatically determine the variable type to read.

        Args:
            key (string): The variable to read from the DB.
            array (boolean): Convert string/dict to Array/List before returning.
            embedded (boolean): Resolve embedded variables.

        Returns:
            (any): Results retrieved from DB
        """
        self.tcex.log.debug(u'read variable {}'.format(key))
        data = None
        if key is not None:
            key = key.strip()
            key_type = self.variable_type(key)
            if re.match(self._variable_match, key):
                if key_type in self.read_data_types:
                    # handle types with embedded variable
                    if key_type in ['Binary', 'BinaryArray']:
                        data = self.read_data_types[key_type](key)
                    else:
                        data = self.read_data_types[key_type](key, embedded)
                else:
                    data = self.read_raw(key)
            elif embedded:
                # check for any embedded variables
                data = self.read_embedded(key, key_type)

        # return data as a list
        if array and not isinstance(data, list):
            if data is not None:
                data = [data]
            else:
                data = []

        # self.tcex.log.debug(u'read data {}'.format(self.tcex.s(data)))
        return data

    def read_array(self, key, embedded=True):
        """Alias for read method that will read any type (e.g., String, KeyValue) and always
           return array.

        Args:
            key (string): The variable to read from the DB.
            embedded (boolean): Resolve embedded variables.

        Returns:
            (any): Results retrieved from DB
        """
        return self.read(key, True, embedded)

    @property
    def read_data_types(self):
        """Map of standard playbook variable types to read method."""
        return {
            'Binary': self.read_binary,
            'BinaryArray': self.read_binary_array,
            'KeyValue': self.read_key_value,
            'KeyValueArray': self.read_key_value_array,
            'String': self.read_string,
            'StringArray': self.read_string_array,
            'TCEntity': self.read_tc_entity,
            'TCEntityArray': self.read_tc_entity_array
        }

    def read_embedded(self, data, parent_var_type):
        """Read method for "mixed" variable type.

        .. Note:: The ``read()`` method will automatically determine if the input is a variable or
                  needs to be searched for embedded variables. There usually is no reason to call
                  this method directly.

        This method will automatically covert variables embedded in a string with data retrieved
        from DB. If there are no keys/variables the raw string will be returned.

        Examples::

            DB Values
            #App:7979:variable_name!String:
                "embedded \\"variable\\""
            #App:7979:two!String:
                "two"
            #App:7979:variable_name!StringArray:
                ["one", "two", "three"]

            Examples 1:
                Input:  "This input has a embedded #App:7979:variable_name!String"

            Examples 2:
                Input: ["one", #App:7979:two!String, "three"]

            Examples 3:
                Input: [{
                    "key": "embedded string",
                    "value": "This input has a embedded #App:7979:variable_name!String"
                }, {
                    "key": "string array",
                    "value": #App:7979:variable_name!StringArray
                }, {
                    "key": "string",
                    "value": #App:7979:variable_name!String
                }]

        Args:
            data (string): The data to parsed and updated from the DB.
            parent_var_type (string): The parent type of the embedded variable.

        Returns:
            (string): Results retrieved from DB
        """
        if data is not None:
            # self.tcex.log.debug(u'data {}'.format(data))
            try:
                data = u'{}'.format(data.strip())
            except UnicodeEncodeError:
                data = data.strip()

            # get all matching variables
            variables = []
            for v in re.finditer(self._variable_parse, data):
                variables.append(v.group(0))

            for var in set(variables):  # recursion over set to handle duplicates
                self.tcex.log.debug(u'var {}'.format(var))
                # get the embedded variable type.
                key_type = self.variable_type(var)
                # self.tcex.log.debug(u'key_type {}'.format(key_type))

                # val - read raw value from DB leaving escaped characters intact
                val = self.read_raw(var)
                # val - read recursive embedded
                val = self.read_embedded(val, key_type)
                # val - remove double quotes added by JSON encoding from embedded String
                if val and val.startswith('"') and val.endswith('"'):
                    # per slack conversation with danny on 3/22/17 all string data should already
                    # have quotes since they are JSON values
                    val = val[1:-1]  # ensure only first and last quote are removed
                # self.tcex.log.debug(u'var {}: val: {}'.format(var, val))

                if val is None:
                    # replace variable reference with nothing
                    val = ''
                # elif parent_var_type in ['String']:
                #     # a parent type of String should have escaped characters removed
                #     # convert "embedded \\\\\\"variable\\\\" TO "embedded \\"variable"
                #     val = codecs.getdecoder('unicode_escape')(val)[0]
                #     # self.tcex.log.debug(u'val (codec.getdecoder): {}'.format(val))
                elif parent_var_type in ['StringArray']:
                    if key_type in ['String']:
                        # handle case where String may or may not be wrapped in double quotes.
                        data = data.replace(', {}'.format(var), ', "{}"'.format(var))
                    elif key_type in ['StringArray']:
                        # handle case where StringArray may or may not be wrapped in double quotes.
                        data = data.replace('"{}"'.format(var), var)
                        if val.startswith('[') and val.endswith(']'):
                            # remove [] from embedded StringArray
                            val = val[1:-1]  # ensure only first and last bracket are removed
                elif parent_var_type in ['KeyValue', 'KeyValueArray']:
                    if key_type in ['StringArray']:
                        if not var.startswith('"') and not var.endswith('"'):
                            # add quotes to var so they will be removed in replace()
                            var = '"{}"'.format(var)

                data = data.replace(var, val)
        return data

    def variable_type(self, variable):
        """Get the Type from the variable string or default to String type.

        The default type is "String" for those cases when the input variable is
        contains not "DB variable" and is just a String.

        **Example Variable**::

            #App:1234:output!StringArray returns **StringArray**

        **Example String**::

            "My Data" returns **String**

        Args:
            variable (string): The variable to be parsed

        Returns:
            (string): The variable type.
        """
        var_type = 'String'
        if variable is not None:
            variable = variable.strip()
            # self.tcex.log.info(u'Variable {}'.format(variable))
            if re.match(self._variable_match, variable):
                var_type = re.search(self._variable_parse, variable).group(4)
        return var_type

    def wrap_embedded_keyvalue(self, data):
        """Wrap keyvalue embedded variable in double quotes.

        Args:
            data (string): The data with embedded variables.

        Returns:
            (string): Results retrieved from DB
        """
        if data is not None:
            try:
                data = u'{}'.format(data)
                # variables = re.findall(self._vars_keyvalue_embedded, u'{}'.format(data))
            except UnicodeEncodeError:
                # variables = re.findall(self._vars_keyvalue_embedded, data)
                pass

            variables = []
            for v in re.finditer(self._vars_keyvalue_embedded, data):
                variables.append(v.group(0))

            for var in set(variables):  # recursion over set to handle duplicates
                # pull (#App:1441:embedded_string!String) from (": #App:1441:embedded_string!String)
                variable_string = re.search(self._variable_parse, var).group(0)
                # reformat to replace the correct instance only, handling the case where a variable
                # is embedded multiple times in the same key value array.
                data = data.replace(var, '": "{}"'.format(variable_string))
        return data

    #
    # db methods
    #

    def hgetall(self):
        """Return all values for a context."""
        return self.db.hgetall

    def create_binary(self, key, value):
        """Create method of CRUD operation for binary data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write.
        """
        data = None
        if key is not None and value is not None:
            try:
                # py2
                # convert to bytes as required for b64encode
                # decode bytes for json serialization as required for json dumps
                data = self.db.create(
                    key.strip(), json.dumps(base64.b64encode(bytes(value)).decode('utf-8')))
            except TypeError:
                # py3
                # set encoding on string and convert to bytes as required for b64encode
                # decode bytes for json serialization as required for json dumps
                data = self.db.create(
                    key.strip(), json.dumps(
                        base64.b64encode(bytes(value, 'utf-8')).decode('utf-8')))
        else:
            self.tcex.log.warning(u'The key or value field was None.')
        return data

    def read_binary(self, key, b64decode=True, decode=True):
        """Read method of CRUD operation for binary data.

        Args:
            key (string): The variable to read from the DB.
            b64decode (bool): If true the data will be base64 decoded.
            decode (bool): If true the data will be decoded to a String.

        Returns:
            (bytes|string): Results retrieved from DB.
        """
        data = None
        if key is not None:
            data = self.db.read(key.strip())
            if data is not None:
                data = json.loads(data)
                if b64decode:
                    # if requested decode the base64 string
                    data = base64.b64decode(data)
                    if decode:
                        try:
                            # if requested decode bytes to a string
                            data = data.decode('utf-8')
                        except UnicodeDecodeError:
                            # for data written an upstream java App
                            data = data.decode('latin-1')
        else:
            self.tcex.log.warning(u'The key field was None.')
        return data

    def create_binary_array(self, key, value):
        """Create method of CRUD operation for binary array data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write.
        """
        data = None
        if key is not None and value is not None:
            value_encoded = []
            for v in value:
                try:
                    # py2
                    # convert to bytes as required for b64encode
                    # decode bytes for json serialization as required for json dumps
                    value_encoded.append(base64.b64encode(bytes(v)).decode('utf-8'))
                except TypeError:
                    # py3
                    # set encoding on string and convert to bytes as required for b64encode
                    # decode bytes for json serialization as required for json dumps
                    value_encoded.append(base64.b64encode(bytes(v, 'utf-8')).decode('utf-8'))
            data = self.db.create(key.strip(), json.dumps(value_encoded))
        else:
            self.tcex.log.warning(u'The key or value field was None.')
        return data

    def read_binary_array(self, key, b64decode=True, decode=True):
        """Read method of CRUD operation for binary array data.

        Args:
            key (string): The variable to read from the DB.
            b64decode (bool): If true the data will be base64 decoded.
            decode (bool): If true the data will be decoded to a String.

        Returns:
            (list): Results retrieved from DB.
        """
        data = None
        if key is not None:
            data = self.db.read(key.strip())
            if data is not None:
                data_decoded = []
                for d in json.loads(data):
                    if b64decode:
                        # if requested decode the base64 string
                        dd = base64.b64decode(d)
                        if decode:
                            # if requested decode bytes to a string
                            try:
                                dd = dd.decode('utf-8')
                            except UnicodeDecodeError:
                                # for data written an upstream java App
                                dd = dd.decode('latin-1')
                        data_decoded.append(dd)
                    else:
                        # for validation in tcrun it's easier to validate the base64 data
                        data_decoded.append(d)
                data = data_decoded
        else:
            self.tcex.log.warning(u'The key field was None.')
        return data

    def create_key_value(self, key, value):
        """Create method of CRUD operation for key/value data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write
        """
        data = None
        if key is not None and value is not None:
            if isinstance(value, (dict, list)):
                data = self.db.create(key.strip(), json.dumps(value))
            else:
                # used to save raw value with embedded variables
                data = self.db.create(key.strip(), value)
        else:
            self.tcex.log.warning(u'The key or value field was None.')
        return data

    def read_key_value(self, key, embedded=True):
        """Read method of CRUD operation for key/value data.

        Args:
            key (string): The variable to read from the DB.
            embedded (boolean): Resolve embedded variables.

        Returns:
            (dictionary): Results retrieved from DB.
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.db.read(key.strip())
            # embedded variable can be unquoted, which breaks JSON.
            data = self.wrap_embedded_keyvalue(data)
            if embedded:
                data = self.read_embedded(data, key_type)
            if data is not None:
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = u'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self.tcex.log.error(err)
                    self.tcex.message_tc(err)
                    self.tcex.exit(1)
        else:
            self.tcex.log.warning(u'The key field was None.')
        return data

    def create_key_value_array(self, key, value):
        """Create method of CRUD operation for key/value array data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write.
        """
        data = None
        if key is not None and value is not None:
            if isinstance(value, (dict, list)):
                data = self.db.create(key.strip(), json.dumps(value))
            else:
                # used to save raw value with embedded variables
                data = self.db.create(key.strip(), value)
        else:
            self.tcex.log.warning(u'The key or value field was None.')
        return data

    def read_key_value_array(self, key, embedded=True):
        """Read method of CRUD operation for key/value array data.

        Args:
            key (string): The variable to read from the DB.
            embedded (boolean): Resolve embedded variables.

        Returns:
            (list): Results retrieved from DB.
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.db.read(key.strip())
            # embedded variable can be unquoted, which breaks JSON.
            data = self.wrap_embedded_keyvalue(data)
            if embedded:
                data = self.read_embedded(data, key_type)
            if data is not None:
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = u'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self.tcex.log.error(err)
                    self.tcex.message_tc(err)
                    self.tcex.exit(1)
        else:
            self.tcex.log.warning(u'The key field was None.')
        return data

    def create_raw(self, key, value):
        """Create method of CRUD operation for raw data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write.
        """
        data = None
        if key is not None and value is not None:
            data = self.db.create(key.strip(), value)
        else:
            self.tcex.log.warning(u'The key or value field was None.')
        return data

    def read_raw(self, key):
        """Read method of CRUD operation for raw data.

        Args:
            key (string): The variable to read from the DB.

        Returns:
            (any): Results retrieved from DB.
        """
        data = None
        if key is not None:
            data = self.db.read(key.strip())
        else:
            self.tcex.log.warning(u'The key field was None.')
        return data

    def create_string(self, key, value):
        """Create method of CRUD operation for string data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write.
        """
        data = None
        if key is not None and value is not None:
            if isinstance(value, (bool, list, int, dict)):
                # value = str(value)
                value = u'{}'.format(value)
            # data = self.db.create(key.strip(), str(json.dumps(value)))
            data = self.db.create(key.strip(), u'{}'.format(json.dumps(value)))
        else:
            self.tcex.log.warning(u'The key or value field was None.')
        return data

    def read_string(self, key, embedded=True):
        """Read method of CRUD operation for string data.

        Args:
            key (string): The variable to read from the DB.
            embedded (boolean): Resolve embedded variables.

        Returns:
            (string): Results retrieved from DB.
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.db.read(key.strip())
            if embedded:
                data = self.read_embedded(data, key_type)
            if data is not None:
                # handle improperly saved string
                try:
                    data = json.loads(data)
                    if data is not None:
                        # reverted the previous change where data was encoded due to issues where
                        # it broke the operator method in py3 (e.g. b'1' ne '1').
                        # data = str(data)
                        data = u'{}'.format(data)
                except ValueError as e:
                    err = u'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self.tcex.log.error(err)
        else:
            self.tcex.log.warning(u'The key field was None.')
        return data

    def create_string_array(self, key, value):
        """Create method of CRUD operation for string array data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write.
        """
        data = None
        if key is not None and value is not None:
            if isinstance(value, (list)):
                data = self.db.create(key.strip(), json.dumps(value))
            else:
                # used to save raw value with embedded variables
                data = self.db.create(key.strip(), value)
        else:
            self.tcex.log.warning(u'The key or value field was None.')
        return data

    def read_string_array(self, key, embedded=True):
        """Read method of CRUD operation for string array data.

        Args:
            key (string): The variable to read from the DB.
            embedded (boolean): Resolve embedded variables.

        Returns:
            (list): Results retrieved from DB.
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.db.read(key.strip())
            if embedded:
                data = self.read_embedded(data, key_type)
            if data is not None:
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = u'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self.tcex.log.error(err)
                    self.tcex.message_tc(err)
                    self.tcex.exit(1)
        else:
            self.tcex.log.warning(u'The key field was None.')
        return data

    # tc entity
    def create_tc_entity(self, key, value):
        """Create method of CRUD operation for TC entity data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write.
        """
        data = None
        if key is not None and value is not None:
            data = self.db.create(key.strip(), json.dumps(value))
        else:
            self.tcex.log.warning(u'The key or value field was None.')
        return data

    def read_tc_entity(self, key, embedded=True):
        """Read method of CRUD operation for TC entity data.

        Args:
            key (string): The variable to read from the DB.
            embedded (boolean): Resolve embedded variables.

        Returns:
            (dictionary): Results retrieved from DB.
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.db.read(key.strip())
            if embedded:
                # untested. this is not a current use case.
                data = self.read_embedded(data, key_type)
            if data is not None:
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = u'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self.tcex.log.error(err)
                    self.tcex.message_tc(err)
                    self.tcex.exit(1)
        else:
            self.tcex.log.warning(u'The key field was None.')
        return data

    # tc entity array
    def create_tc_entity_array(self, key, value):
        """Create method of CRUD operation for TC entity array data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write.
        """
        data = None
        if key is not None and value is not None:
            data = self.db.create(key.strip(), json.dumps(value))
        else:
            self.tcex.log.warning(u'The key or value field was None.')
        return data

    def read_tc_entity_array(self, key, embedded=True):
        """Read method of CRUD operation for TC entity array data.

        Args:
            key (string): The variable to read from the DB.
            embedded (boolean): Resolve embedded variables.

        Returns:
            (list): Results retrieved from DB.
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.db.read(key.strip())
            if embedded:
                # untested. this is not a current use case.
                data = self.read_embedded(data, key_type)
            if data is not None:
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = u'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self.tcex.log.error(err)
                    self.tcex.message_tc(err)
                    self.tcex.exit(1)
        else:
            self.tcex.log.warning(u'The key field was None.')
        return data

    #
    # Static Methods
    #

    @staticmethod
    def entity_to_bulk(entities, resource_type_parent):
        """Convert Single TC Entity to Bulk format.

        .. Attention:: This method is subject to frequent changes

        Args:
            entities (dictionary): TC Entity to be converted to Bulk.
            resource_type_parent (string): The resource parent type of the tc_data provided.

        Returns:
            (dictionary): A dictionary representing TC Bulk format.
        """
        if not isinstance(entities, list):
            entities = [entities]

        bulk_array = []
        for e in entities:
            bulk = {
                'type': e.get('type'),
                'ownerName': e.get('ownerName')
            }
            if resource_type_parent in ['Group', 'Task', 'Victim']:
                bulk['name'] = e.get('value')
            elif resource_type_parent in ['Indicator']:
                bulk['confidence'] = e.get('confidence')
                bulk['rating'] = e.get('rating')
                bulk['summary'] = e.get('value')

            bulk_array.append(bulk)

        if len(bulk_array) == 1:
            return bulk_array[0]
        return bulk_array

    @staticmethod
    def indicator_arrays(tc_entity_array):
        """Convert TCEntityArray to Indicator Type dictionary.

        Args:
            tc_entity_array (dictionary): The TCEntityArray to convert.

        Returns:
            (dictionary): Dictionary containing arrays of indicators for each indicator type.
        """
        type_dict = {}
        for ea in tc_entity_array:
            type_dict.setdefault(ea['type'], []).append(ea['value'])
        return type_dict

    @staticmethod
    def json_to_bulk(tc_data, value_fields, resource_type, resource_type_parent):
        """Convert ThreatConnect JSON response to a Bulk Format.

        .. Attention:: This method is subject to frequent changes

        Args:
            tc_data (dictionary): Array of data returned from TC API call.
            value_fields (list): Field names that contain the "value" data.
            resource_type (string): The resource type of the tc_data provided.
            resource_type_parent (string): The resource parent type of the tc_data provided.

        Returns:
            (list): A dictionary representing a TCEntityArray

        """
        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        bulk_array = []
        for d in tc_data:

            # value
            values = []
            for field in value_fields:
                if d.get(field) is not None:
                    values.append(d.get(field))
                    del d[field]

            if resource_type_parent in ['Group', 'Task', 'Victim']:
                d['name'] = ' : '.join(values)
            elif resource_type_parent in ['Indicator']:
                d['summary'] = ' : '.join(values)

            if 'owner' in d:
                d['ownerName'] = d['owner']['name']
                del d['owner']

            # type
            if d.get('type') is None:
                d['type'] = resource_type

            bulk_array.append(d)

        return bulk_array

    @staticmethod
    def json_to_entity(tc_data, value_fields, resource_type, resource_type_parent):
        """Convert ThreatConnect JSON response to a TCEntityArray.

        .. Attention:: This method is subject to frequent changes.

        Args:
            tc_data (dictionary): Array of data returned from TC API call.
            value_fields (list): Field names that contain the "value" data.
            resource_type (string): The resource type of the tc_data provided.
            resource_type_parent (string): The resource parent type of the tc_data provided.

        Returns:
            (list): A list representing a TCEntityArray.

        """
        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        entity_array = []
        for d in tc_data:
            entity = {
                'id': d.get('id'),
                'webLink': d.get('webLink')
            }

            # value
            values = []
            if 'summary' in d:
                values.append(d.get('summary'))
            else:
                for field in value_fields:
                    if d.get(field) is not None:
                        values.append(d.get(field))
            entity['value'] = ' : '.join(values)

            # type
            if d.get('type') is not None:
                entity['type'] = d.get('type')
            else:
                entity['type'] = resource_type

            if resource_type_parent in ['Indicator']:
                entity['confidence'] = d.get('confidence')
                entity['rating'] = d.get('rating')
                entity['threatAssessConfidence'] = d.get('threatAssessConfidence')
                entity['threatAssessRating'] = d.get('threatAssessRating')
                entity['dateLastModified'] = d.get('lastModified')

            if resource_type_parent in ['Indicator', 'Group']:
                if 'owner' in d:
                    entity['ownerName'] = d['owner']['name']
                else:
                    entity['ownerName'] = d.get('ownerName')
                entity['dateAdded'] = d.get('dateAdded')

            if resource_type_parent in ['Victim']:
                entity['ownerName'] = d.get('org')

            entity_array.append(entity)

        return entity_array

    @staticmethod
    def json_to_key_value(json_data, key_field, value_field=None, array=False):
        """Convert JSON data to a KeyValue/KeyValueArray.

        Args:
            json_data (dictionary|list): Array/List of JSON data.
            key_field (string): Field name for the key.
            value_field (string): Field name for the value or use the value of the key field.
            array (boolean): Always return array even if only on result.

        Returns:
            (dictionary|list): A dictionary or list representing a KeyValue or KeyValueArray.

        """
        if not isinstance(json_data, list):
            json_data = [json_data]

        key_value_array = []
        for d in json_data:
            if d.get(key_field) is not None and value_field is None:
                # key / value based off same entry
                key = key_field
                value = d.get(key_field)
            elif d.get(key_field) is not None and d.get(value_field) is not None:
                # key / value data are from separate entries
                key = d.get(key_field)
                value = d.get(value_field)
            else:
                continue

            key_value_array.append({
                'key': key,
                'value': value
            })

        if len(key_value_array) == 1 and not array:
            return key_value_array[0]

        return key_value_array
