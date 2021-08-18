[
    # binary is not a valid indicator type (not String and not TCEntity),
    b'not valid indicator',
    # has no value key
    {'type': 'Address', 'id': '100'},
    # has no type key
    {'value': '8.8.8.8', 'id': '100'},
    # type is empty string
    {'type': '', 'value': '8.8.8.8', 'id': '100'},
    # type is None
    {'type': None, 'value': '8.8.8.8', 'id': '100'},
    # type is not one of the valid indicator types
    {'type': 'Adversary', 'value': 'Adversary Name', 'id': '100'},
    # type is anything else
    {'type': [], 'value': '8.8.8.8', 'id': '100'},
    # missing id
    {'type': 'Address', 'value': '8.8.8.8'},
    # id is blank
    {'type': 'Address', 'value': '8.8.8.8', 'id': ''},
    # id is None
    {'type': 'Address', 'value': '8.8.8.8', 'id': None},
    # value must be a string
    {'type': [], 'value': [], 'id': '100'},
    # same scenarios as above, except using array inputs
    [b'not valid indicator'],
    # has no value key
    [{'type': 'Address', 'id': '100'}],
    # has no type key
    [{'value': '8.8.8.8', 'id': '100'}],
    # type is empty string
    [{'type': '', 'value': '8.8.8.8', 'id': '100'}],
    # type is None
    [{'type': None, 'value': '8.8.8.8', 'id': '100'}],
    # type is not one of the valid indicator types
    [{'type': 'Adversary', 'value': 'Adversary Name', 'id': '100'}],
    # type is anything else
    [{'type': [], 'value': '8.8.8.8', 'id': '100'}],
    # missing id
    [{'type': 'Address', 'value': '8.8.8.8'}],
    # id is blank
    [{'type': 'Address', 'value': '8.8.8.8', 'id': ''}],
    # id is None
    [{'type': 'Address', 'value': '8.8.8.8', 'id': None}],
    # value must be a string
    [{'type': [], 'value': [], 'id': '100'}],
]
