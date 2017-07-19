""" standard """
import base64
import codecs
import json
# import os
import re

""" third-party """
""" custom """


class TcExPlaybook(object):
    """Playbook methods for accessing Database
    """

    def __init__(self, tcex):
        """Initialize class data

        Initialize parent class for default values and logging method.
        """
        self._tcex = tcex
        self._create_data_type = {
            'Binary': self.create_binary,
            'BinaryArray': self.create_binary_array,
            'KeyValue': self.create_key_value,
            'KeyValueArray': self.create_key_value_array,
            'String': self.create_string,
            'StringArray': self.create_string_array,
            'TCEntity': self.create_tc_entity,
            'TCEntityArray': self.create_tc_entity_array
        }
        self._read_data_type = {
            'Binary': self.read_binary,
            'BinaryArray': self.read_binary_array,
            'KeyValue': self.read_key_value,
            'KeyValueArray': self.read_key_value_array,
            'String': self.read_string,
            'StringArray': self.read_string_array,
            'TCEntity': self.read_tc_entity,
            'TCEntityArray': self.read_tc_entity_array
        }
        self._out_variables = {}  # dict of output variable by name
        self._out_variables_type = {}  # dict of output variable by name-type
        self._var_parse = re.compile(
            r"""^#([A-Za-z]+):([\d]+):([A-Za-z0-9_.-]+)!([A-Za-z0-9_-]+)$""")
        self._vars_match = re.compile(
            r"""(\"?#(?:[A-Za-z]+):(?:[\d]+):(?:[A-Za-z0-9_.-]+)!(?:[A-Za-z0-9_-]+)\"?)""")

        # parse out variable
        self._parse_out_variable()

        if self._tcex._args.tc_playbook_db_type == 'Redis':
            try:
                from tcex_redis import TcExRedis
            except ImportError as e:
                self._tcex.log.error('Redis Module is not installed ({}).'.format(e))
                raise

            self._db = TcExRedis(
                self._tcex._args.tc_playbook_db_path,
                self._tcex._args.tc_playbook_db_port,
                self._tcex._args.tc_playbook_db_context
            )
        elif self._tcex._args.tc_playbook_db_type == 'TCKeyValueAPI':
            from tcex_key_value import TcExKeyValue
            self._db = TcExKeyValue(self._tcex, self._tcex._args.tc_playbook_db_context)
        else:
            err = 'Invalid DB Type: ({})'.format(self._tcex._args.tc_playbook_db_type)
            self._tcex.message_tc(err)
            self._tcex.log.error(err)
            self._tcex.exit(1)

    def _parse_out_variable(self):
        """Internal method to parse the tc_playbook_out_variable arg.

        **Example Variable Format**::

            #App:1234:status!String,#App:1234:status_code!String
        """
        if self._tcex._args.tc_playbook_out_variables is not None:
            variables = self._tcex._args.tc_playbook_out_variables.strip()
            for o in variables.split(','):
                parsed_key = self.parse_variable(o)
                variable_name = parsed_key['name']
                variable_type = parsed_key['type']
                self._out_variables[variable_name] = {
                    'variable': o
                }
                vt_key = '{}-{}'.format(variable_name, variable_type)
                self._out_variables_type[vt_key] = {
                    'variable': o
                }

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
        if variable in self._out_variables:
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
            (string): Result string of DB write
        """
        data = None
        if key is not None:
            key = key.strip()
            self._tcex.log.debug('create variable {}'.format(key))
            # bcs - only for debugging or binary might cause issues
            # self._tcex.log.debug('variable value: {0}'.format(value))
            parsed_key = self.parse_variable(key.strip())
            variable_type = parsed_key['type']
            if variable_type in self._read_data_type:
                data = self._create_data_type[variable_type](key, value)
            else:
                data = self.create_raw(key, value)
        return data

    def create_output(self, key, value, variable_type=None):
        """Wrapper for Create method of CRUD operation for working with KeyValue DB.

        This method will automatically check to see if provided variable was requested by
        a downstream app and if so create the data in the KeyValue DB.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.
            variable_type (string): The variable type being written

        Returns:
            (string): Result string of DB write
        """
        results = None
        if key is not None:
            key = key.strip()
            key_type = '{}-{}'.format(key, variable_type)
            if key_type in self._out_variables_type.keys():
                self._tcex.log.info(
                    'Variable {0} was requested by downstream app.'.format(key))
                if value is not None:
                    v = self._out_variables_type.get(key_type)
                    results = self.create(v['variable'], value)
                else:
                    self._tcex.log.info(
                        'Variable {0} has a none value an will not be written.'.format(key))
            elif key in self._out_variables.keys():
                self._tcex.log.info(
                    'Variable {0} was requested by downstream app.'.format(key))
                if value is not None:
                    v = self._out_variables.get(key)
                    results = self.create(v['variable'], value)
                else:
                    self._tcex.log.info(
                        'Variable {0} has a none value an will not be written.'.format(key))
            else:
                self._tcex.log.info(
                    'Variable {0} was NOT requested by downstream app.'.format(key))
        return results

    def exit(self, code=None):
        """Playbook wrapper on TcEx exit method

        Playbooks do not support partial failures so we change the exit method from 3 to 1 and call
        it a partial success instead.

        Args:
            code (Optional [integer]): The exit code value for the app.
        """
        if code is None:
            code = self._tcex._exit_code
            if code == 3:
                self._tcex.log.info('Changing exit code from 3 to 0.')
                code = 0  # playbooks doesn't support partial failure
        elif code not in [0, 1]:
            code = 1

        self._tcex.exit(code)

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
            self._tcex.log.debug('parse variable {}'.format(variable))
            if re.match(self._var_parse, variable):
                var = re.search(self._var_parse, variable)
                data = {
                    'root': var.group(1),
                    'job_id': var.group(2),
                    'name': var.group(3),
                    'type': var.group(4),
                }
        return data

    def read(self, key, array=False):
        """Read method of CRUD operation for working with KeyValue DB.

        This method will automatically check to see if a single variable is passed
        or if "mixed" data is passed and return the results from the DB. It will also
        automatically determine the variable type to read.

        Args:
            key (string): The variable to read from the DB.
            array (boolean): Convert string/dict to Array/List before returning.

        Returns:
            (any): Results retrieved from DB
        """
        self._tcex.log.debug('read variable {}'.format(key))
        data = None
        if key is not None:
            key = key.strip()
            key_type = self.variable_type(key)
            if re.match(self._var_parse, key):
                if key_type in self._read_data_type:
                    data = self._read_data_type[key_type](key)
                else:
                    data = self.read_raw(key)
            else:
                data = self.read_embedded(key, key_type)

        # return data as a list
        if array and not isinstance(data, list):
            if data is not None:
                data = [data]
            else:
                data = []

        # self._tcex.log.debug('read data {}'.format(self._tcex.s(data)))
        return data

    def read_embedded(self, data, parent_var_type):
        """Read method for "mixed" variable type.

        .. Note:: The ``read()`` method will automatically determine if the variable is embedded and
                  call this method.  There usually is no reason to call this method directly.

        This method will automatically covert keys/variables embedded in a string
        with data retrieved from DB. If there are no keys/variables the raw string
        will be returned.

        Args:
            data (string): The data to parsed and updated from the DB.

        Returns:
            (string): Results retrieved from DB
        """
        if data is not None:
            data = data.strip()
            variables = re.findall(self._vars_match, str(data))
            for var in variables:
                # regex will capture quotes around variables, which needs to be removed
                key_type = self.variable_type(var.strip('"'))

                # read raw value so escaped characters won't be removed
                val = self.read_raw(var.strip('"'))

                if val is None:
                    # None value should be replace with an empty string
                    val = '""'
                elif parent_var_type in ['String']:
                    # a parent type of String should not keep the quotes added by the JSON encoding
                    val = val.strip('"')
                    # a parent type of String should have escaped characters removed
                    val = codecs.getdecoder('unicode_escape')(val)[0]
                ## per slack conversation with danny on 3/22 all string data should already have
                ## quotes already since they are JSON values
                ## elif key_type in ['String']:
                ##     if not val.startswith('"') and not val.endswith('"'):
                ##         val = '"{}"'.format(val)

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
            # self._tcex.log.info('Variable {0}'.format(variable))
            if re.match(self._var_parse, variable):
                var_type = re.search(self._var_parse, variable).group(4)

        return var_type

    #
    # db methods
    #

    # binary
    def create_binary(self, key, value):
        """Create method of CRUD operation for binary data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write
        """
        data = None
        if key is not None and value is not None:
            data = self._db.create(key.strip(), json.dumps(base64.b64encode(bytes(value)).decode('utf-8')))
        else:
            self._tcex.log.warning('The key or value field was None.')
        return data

    def read_binary(self, key):
        """Read method of CRUD operation for binary data.

        Args:
            key (string): The variable to read from the DB.

        Returns:
            (): Results retrieved from DB
        """
        data = None
        if key is not None:
            data = self._db.read(key.strip())
            if data is not None:
                data = base64.b64decode(json.loads(data))
        else:
            self._tcex.log.warning('The key field was None.')
        return data

    # binary array
    def create_binary_array(self, key, value):
        """Create method of CRUD operation for binary array data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write
        """
        data = None
        if key is not None and value is not None:
            value_encoded = []
            for v in value:
                value_encoded.append(base64.b64encode(bytes(v)).decode('utf-8'))
            data = self._db.create(key.strip(), json.dumps(value_encoded))
        else:
            self._tcex.log.warning('The key or value field was None.')
        return data

    def read_binary_array(self, key):
        """Read method of CRUD operation for binary array data.

        Args:
            key (string): The variable to read from the DB.

        Returns:
            (): Results retrieved from DB
        """
        data = None
        if key is not None:
            data = self._db.read(key.strip())
            if data is not None:
                data_decoded = []
                for d in json.loads(data):
                    data_decoded.append(base64.b64decode(d))
        else:
            self._tcex.log.warning('The key field was None.')
        return data_decoded

    # key/value
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
            data = self._db.create(key.strip(), json.dumps(value))
        else:
            self._tcex.log.warning('The key or value field was None.')
        return data

    def read_key_value(self, key):
        """Read method of CRUD operation for key/value data.

        Args:
            key (string): The variable to read from the DB.

        Returns:
            (dictionary): Results retrieved from DB
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.read_embedded(self._db.read(key.strip()), key_type)
            if data is not None:
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = 'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self._tcex.log.error(err)
                    self._tcex.message_tc(err)
                    self._tcex.exit(1)
        else:
            self._tcex.log.warning('The key field was None.')
        return data

    # key/value array
    def create_key_value_array(self, key, value):
        """Create method of CRUD operation for key/value array data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write
        """
        data = None
        if key is not None and value is not None:
            data = self._db.create(key.strip(), json.dumps(value))
        else:
            self._tcex.log.warning('The key or value field was None.')
        return data

    def read_key_value_array(self, key):
        """Read method of CRUD operation for key/value array data.

        Args:
            key (string): The variable to read from the DB.

        Returns:
            (list): Results retrieved from DB
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.read_embedded(self._db.read(key.strip()), key_type)
            if data is not None:
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = 'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self._tcex.log.error(err)
                    self._tcex.message_tc(err)
                    self._tcex.exit(1)
        else:
            self._tcex.log.warning('The key field was None.')
        return data

    # raw
    def create_raw(self, key, value):
        """Create method of CRUD operation for raw data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write
        """
        data = None
        if key is not None and value is not None:
            data = self._db.create(key.strip(), value)
        else:
            self._tcex.log.warning('The key or value field was None.')
        return data

    def read_raw(self, key):
        """Read method of CRUD operation for raw data.

        Args:
            key (string): The variable to read from the DB.

        Returns:
            (): Results retrieved from DB
        """
        data = None
        if key is not None:
            data = self._db.read(key.strip())
        else:
            self._tcex.log.warning('The key field was None.')
        return data

    # string
    def create_string(self, key, value):
        """Create method of CRUD operation for string data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write
        """
        data = None
        if key is not None and value is not None:
            if isinstance(value, (bool, list, dict)):
                value = str(value)
            data = self._db.create(key.strip(), json.dumps(value))
        else:
            self._tcex.log.warning('The key or value field was None.')
        return data

    def read_string(self, key):
        """Read method of CRUD operation for string data.

        Args:
            key (string): The variable to read from the DB.

        Returns:
            (string): Results retrieved from DB
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.read_embedded(self._db.read(key.strip()), key_type)
            if data is not None:
                # handle improperly saved string
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = 'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self._tcex.log.error(err)
                    pass
        else:
            self._tcex.log.warning('The key field was None.')
        return data

    # string array
    def create_string_array(self, key, value):
        """Create method of CRUD operation for string array data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write
        """
        data = None
        if key is not None and value is not None:
            data = self._db.create(key.strip(), json.dumps(value))
        else:
            self._tcex.log.warning('The key or value field was None.')
        return data

    def read_string_array(self, key):
        """Read method of CRUD operation for string array data.

        Args:
            key (string): The variable to read from the DB.

        Returns:
            (list): Results retrieved from DB
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.read_embedded(self._db.read(key.strip()), key_type)
            if data is not None:
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = 'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self._tcex.log.error(err)
                    self._tcex.message_tc(err)
                    self._tcex.exit(1)
        else:
            self._tcex.log.warning('The key field was None.')
        return data

    # tc entity
    def create_tc_entity(self, key, value):
        """Create method of CRUD operation for TC entity data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write
        """
        data = None
        if key is not None and value is not None:
            data = self._db.create(key.strip(), json.dumps(value))
        else:
            self._tcex.log.warning('The key or value field was None.')
        return data

    def read_tc_entity(self, key):
        """Read method of CRUD operation for TC entity data.

        Args:
            key (string): The variable to read from the DB.

        Returns:
            (dictionary): Results retrieved from DB
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.read_embedded(self._db.read(key.strip()), key_type)
            if data is not None:
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = 'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self._tcex.log.error(err)
                    self._tcex.message_tc(err)
                    self._tcex.exit(1)
        else:
            self._tcex.log.warning('The key field was None.')
        return data

    # tc entity array
    def create_tc_entity_array(self, key, value):
        """Create method of CRUD operation for TC entity array data.

        Args:
            key (string): The variable to write to the DB.
            value (any): The data to write to the DB.

        Returns:
            (string): Result of DB write
        """
        data = None
        if key is not None and value is not None:
            data = self._db.create(key.strip(), json.dumps(value))
        else:
            self._tcex.log.warning('The key or value field was None.')
        return data

    def read_tc_entity_array(self, key):
        """Read method of CRUD operation for TC entity array data.

        Args:
            key (string): The variable to read from the DB.

        Returns:
            (list): Results retrieved from DB
        """
        data = None
        if key is not None:
            key_type = self.variable_type(key)
            data = self.read_embedded(self._db.read(key.strip()), key_type)
            if data is not None:
                try:
                    data = json.loads(data)
                except ValueError as e:
                    err = 'Failed loading JSON data ({}). Error: ({})'.format(data, e)
                    self._tcex.log.error(err)
                    self._tcex.message_tc(err)
                    self._tcex.exit(1)
        else:
            self._tcex.log.warning('The key field was None.')
        return data

    #
    # Static Methods
    #

    @staticmethod
    def entity_to_bulk(entities, resource_type_parent):
        """Convert Single TC Entity to Bulk format

        .. Attention:: This method is subject to frequent changes

        Args:
            entities (dictionary): TC Entity to be converted to Bulk.
            resource_type_parent (string): The resource parent type of the tc_data provided.

        Returns:
            (dictionary): A dictionary representing TC Bulk format

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
        """Convert TCEntityArray to Indicator Type dictionary

        Args:
            tc_entity_array (dictionary): The TCEntityArray to convert

        Returns:
            (dictionary): Dictionary containing arrays of indicators for each indicator type

        """
        type_dict = {}
        for ea in tc_entity_array:
            type_dict.setdefault(ea['type'], []).append(ea['value'])
        return type_dict

    @staticmethod
    def json_to_bulk(tc_data, value_fields, resource_type, resource_type_parent):
        """Convert ThreatConnect JSON response to a Bulk Format

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
        """Convert ThreatConnect JSON response to a TCEntityArray

        .. Attention:: This method is subject to frequent changes

        Args:
            tc_data (dictionary): Array of data returned from TC API call.
            value_fields (list): Field names that contain the "value" data.
            resource_type (string): The resource type of the tc_data provided.
            resource_type_parent (string): The resource parent type of the tc_data provided.

        Returns:
            (list): A list representing a TCEntityArray

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
        """Convert JSON data to a KeyValue/KeyValueArray

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
