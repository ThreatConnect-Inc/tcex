"""Gen Code App Input Map"""

app_input_map = {
    'Any': {
        'optional': {'type': 'Any', 'field_type': None},
        'required': {'type': 'Any', 'field_type': None},
    },
    'Binary': {
        'optional': {'type': 'Binary', 'field_type': 'Binary'},
        'required': {'type': 'binary(allow_empty=False)', 'field_type': 'binary'},
    },
    'BinaryArray': {
        'optional': {'type': 'List[Binary]', 'field_type': 'Binary'},
        'required': {'type': 'List[binary(allow_empty=False)]', 'field_type': 'binary'},
    },
    'Choice': {
        'optional': {'type': 'Choice', 'field_type': 'Choice'},
        'required': {'type': 'Choice', 'field_type': 'Choice'},
    },
    'EditChoice': {
        'optional': {'type': 'EditChoice', 'field_type': 'EditChoice'},
        'required': {'type': 'EditChoice', 'field_type': 'EditChoice'},
    },
    'Encrypt': {
        'optional': {'type': 'Sensitive', 'field_type': 'Sensitive'},
        'required': {'type': 'sensitive(allow_empty=False)', 'field_type': 'sensitive'},
    },
    'KeyValue': {
        'optional': {'type': 'KeyValue', 'field_type': 'KeyValue'},
        'required': {'type': 'KeyValue', 'field_type': 'KeyValue'},
    },
    'KeyValueArray': {
        'optional': {'type': 'List[KeyValue]', 'field_type': 'KeyValue'},
        'required': {'type': 'List[KeyValue]', 'field_type': 'KeyValue'},
    },
    'KeyValueList': {
        'optional': {'type': 'List[KeyValue]', 'field_type': 'KeyValue'},
        'required': {'type': 'List[KeyValue]', 'field_type': 'KeyValue'},
    },
    'MultiChoice': {
        'optional': {'type': 'List[Choice]', 'field_type': 'Choice'},
        'required': {'type': 'List[Choice]', 'field_type': 'Choice'},
    },
    'String': {
        'optional': {'type': 'String', 'field_type': 'String'},
        'required': {'type': 'string(allow_empty=False)', 'field_type': 'string'},
    },
    'StringArray': {
        'optional': {'type': 'List[String]', 'field_type': 'String'},
        'required': {'type': 'List[string(allow_empty=False)]', 'field_type': 'string'},
    },
    'TCEntity': {
        'optional': {'type': 'TCEntity', 'field_type': 'TCEntity'},
        'required': {'type': 'TCEntity', 'field_type': 'TCEntity'},
    },
    'TCEntityArray': {
        'optional': {'type': 'List[TCEntity]', 'field_type': 'TCEntity'},
        'required': {'type': 'List[TCEntity]', 'field_type': 'TCEntity'},
    },
}
