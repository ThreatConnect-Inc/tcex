"""Functions that allow customization of existing types"""
# first-party
from tcex.input.field_types.binary_array import BinaryArray, BinaryArrayOptional
from tcex.input.field_types.exception import ConfigurationException
from tcex.input.field_types.group_array import GroupArray, GroupArrayOptional
from tcex.input.field_types.indicator_array import IndicatorArray, IndicatorArrayOptional
from tcex.input.field_types.intel_array import IntelArray, IntelArrayOptional
from tcex.input.field_types.key_value_array import KeyValueArray, KeyValueArrayOptional
from tcex.input.field_types.string_array import StringArray, StringArrayOptional
from tcex.input.field_types.tc_entity_array import TCEntityArray, TCEntityArrayOptional
from tcex.input.field_types.utils import ConfigurationUtils


def _is_optional(kwargs):
    """Check kwargs for optional value"""
    return kwargs.pop('optional', False)


def _custom_array(array_type, namespace=None, **kwargs):
    """Allow for dynamic configuration of an Array type.

    This method contains the logic to override configuration items that apply to all Array
    types. An optional namespace may be passed in, which would be generated from a function that
    handles configuration items that are specific to a particular Array type. Functions that
    are specific to a particular Array type should only be concerned with building a namespace
    with configuration items that are specific to said Array type and should not be concerned
    with adding global configuration items to the namespace (global configuration items are
    configuration items that apply to all Array types).

    :param array_type: The Array Type to configure (StringArray, BinaryArray, etc.)
    :param namespace: a preconfigured namespace object to extend with kwargs passed to this function
    :kwarg allow_empty_members: If array is initialized with a list, this flag decides if
    the list may contain empty members
    :kwarg allow_null_members: If array is initialized with a list, this flag decides if
    the list may contain null members
    """
    namespace = namespace if namespace is not None else {}
    namespace['_allow_empty_array_members'] = kwargs.get('allow_empty_members', True)
    namespace['_allow_null_array_members'] = kwargs.get('allow_null_members', True)
    return type(f'{array_type.__name__}Custom', (array_type,), namespace)


def custom_binary_array(**kwargs):
    """Allow for dynamic configuration of a BinaryArray.

    Builds a namespace with configuration items found in kwargs. This method only inspects kwargs
    for configuration items that are specific to this Array Type. Other kwargs are passed through
    to the base custom_array function.

    :kwarg optional: Boolean denoting whether to return an Optional variant of the Array or not.
    """
    # placeholder set in place in case customizations specific to this Array Type are needed
    namespace = {}
    return _custom_array(
        BinaryArrayOptional if _is_optional(kwargs) else BinaryArray, namespace, **kwargs
    )


def custom_string_array(**kwargs):
    """Allow for dynamic configuration of a StringArray.

    Builds a namespace with configuration items found in kwargs. This method only inspects kwargs
    for configuration items that are specific to this Array Type. Other kwargs are passed through
    to the base custom_array function.

    :kwarg optional: Boolean denoting whether to return an Optional variant of the Array or not.
    :kwarg split_on: String value upon which the value that initializes StringArray should be
    split on. This has an effect if StringArray is initialized with a single String. If StringArray
    is initialized with a StringArray, this option has no effect.
    :kwarg strip_on_split: Boolean value that denotes whether the Strings that result from the
    split operation on split_on should be stripped.
    """
    _split_on = kwargs.pop('split_on', None)
    _strip = kwargs.pop('strip_on_split', True)
    _strip = True if _strip is None else _strip

    if _split_on is not None and not isinstance(_split_on, str):
        raise ConfigurationException(
            'Value of "split_on" customization option must be a String or None. '
            f'Received type: {type(_split_on)}'
        )

    if not isinstance(_strip, bool):
        raise ConfigurationException(
            'Value of "strip_on_split" customization option must be a boolean or None. '
            f'Received type: {type(_split_on)}'
        )

    namespace = {'_split_on': _split_on, '_strip_on_split': _strip}
    return _custom_array(
        StringArrayOptional if _is_optional(kwargs) else StringArray, namespace, **kwargs
    )


def custom_tc_entity_array(**kwargs):
    """Allow for dynamic configuration of a BinaryArray.

    Builds a namespace with configuration items found in kwargs. This method only inspects kwargs
    for configuration items that are specific to this Array Type. Other kwargs are passed through
    to the base custom_array function.

    :kwarg optional: Boolean denoting whether to return an Optional variant of the Array or not.
    """
    # placeholder set in place in case customizations specific to this Array Type are needed
    namespace = {}
    return _custom_array(
        TCEntityArrayOptional if _is_optional(kwargs) else TCEntityArray, namespace, **kwargs
    )


def custom_key_value_array(**kwargs):
    """Allow for dynamic configuration of a BinaryArray.

    Builds a namespace with configuration items found in kwargs. This method only inspects kwargs
    for configuration items that are specific to this Array Type. Other kwargs are passed through
    to the base custom_array function.

    :kwarg optional: Boolean denoting whether to return an Optional variant of the Array or not.
    """
    # placeholder set in place in case customizations specific to this Array Type are needed
    namespace = {}
    return _custom_array(
        KeyValueArrayOptional if _is_optional(kwargs) else KeyValueArray, namespace, **kwargs
    )


def custom_intel_array(intel_array_descendant=None, namespace=None, **kwargs):
    """Allow for dynamic configuration of a IntelArray.

    Builds a namespace with configuration items found in kwargs. This method only inspects kwargs
    for configuration items that are specific to this Array Type. Other kwargs are passed through
    to the base custom_array function.

    :param intel_array_descendant: As some Types inherit from IntelArray, this function accepts a
    descendant of IntelArray via this argument. A ConfigurationException is raised if the passed-in
    value is not an IntelArray descendant.
    :param namespace: namespace passed in from a function that customizes a descendant of
    IntelArray. This value is only used when a descendant of IntelArray is passed in via
    intel_array_descendant.
    :kwarg optional: Boolean denoting whether to return an Optional variant of the Array or not.
    """
    _namespace = {}
    utils = ConfigurationUtils()
    types = kwargs.pop('entity_filter_types', None)

    if intel_array_descendant:
        if not issubclass(intel_array_descendant, IntelArray):
            raise ConfigurationException(
                'intel_array_descendant must be a descendant of IntelArray'
            )

        _namespace = namespace if namespace else _namespace

    if types is not None:
        utils.validate_intel_types('entity_filter_types', types)
        _namespace['_entity_filter_types'] = types

    intel_array_variant = IntelArrayOptional if _is_optional(kwargs) else IntelArray

    return _custom_array(intel_array_descendant or intel_array_variant, _namespace, **kwargs)


def custom_indicator_array(**kwargs):
    """Allow for dynamic configuration of a IndicatorArray.

    Builds a namespace with configuration items found in kwargs. This method only inspects kwargs
    for configuration items that are specific to this Array Type. Other kwargs are passed through
    to the custom_intel_array function.

    :kwarg optional: Boolean denoting whether to return an Optional variant of the Array or not.
    """
    utils = ConfigurationUtils()
    namespace = {}

    # do not pop value, simply validate. Value will be popped in custom_intel_array
    types = kwargs.get('entity_filter_types')

    if types is not None:
        utils.validate_intel_types('entity_filter_types', types, restrict_to=utils.INDICATOR)

    return custom_intel_array(
        IndicatorArrayOptional if _is_optional(kwargs) else IndicatorArray, namespace, **kwargs
    )


def custom_group_array(**kwargs):
    """Allow for dynamic configuration of a GroupArray.

    Builds a namespace with configuration items found in kwargs. This method only inspects kwargs
    for configuration items that are specific to this Array Type. Other kwargs are passed through
    to the custom_intel_array function.

    :kwarg optional: Boolean denoting whether to return an Optional variant of the Array or not.
    """
    utils = ConfigurationUtils()
    namespace = {}

    # do not pop value, simply validate. Value will be popped in custom_intel_array
    types = kwargs.get('entity_filter_types')

    if types is not None:
        utils.validate_intel_types('entity_filter_types', types, restrict_to=utils.GROUP)

    return custom_intel_array(
        GroupArrayOptional if _is_optional(kwargs) else GroupArray, namespace, **kwargs
    )
