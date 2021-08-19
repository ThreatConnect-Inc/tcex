"""Field Type Validator methods"""

# first-party
from tcex.sessions import TcSessionSingleton
from tcex.threat_intelligence import ThreatIntelUtils

from .exception import ConfigurationException


def array_validator(value: list) -> None:
    """Validate value is a non-empty array."""
    if not value:
        raise ValueError('Array must have a least one element.')


def ti_utils() -> ThreatIntelUtils:
    """Return Threat Intel Utils instance.

    Use the TC session singleton to initialize TI Utils. At this point
    the singleton should already be initialize so no need to pass args.
    """
    return ThreatIntelUtils(session=TcSessionSingleton(None, None, None).session)


class ConfigurationUtils:
    """Class that holds logic used to validate Type configuration values"""

    def __init__(self):
        """Initialize ConfigurationUtils"""
        self.ti_utils = ti_utils()
        self.INDICATOR = self.ti_utils.INDICATOR
        self.GROUP = self.ti_utils.GROUP

    def validate_intel_types(self, config_item, types_list, restrict_to=None):
        """Wrap ti_utils.validate_intel_types and raise ConfigurationException on error.

        types_list will be validated to contain only strings that are valid Indicator/Group types.

        :param config_item: The name of the configuration item that houses the type list to
        validate. This param is used for error generation purposes.
        :param types_list: The value of the configuration item to validate.
        :param restrict_to: If None, types_list will be checked for both indicator and group types.
        Otherwise, this parameter is expected to be set to either self.INDICATOR or self.GROUP.
        """
        try:
            self.ti_utils.validate_intel_types(types_list, restrict_to=restrict_to)
        except (ValueError, TypeError) as ex:
            if restrict_to is None:
                _type = 'Intel'
            else:
                _type = self.INDICATOR if restrict_to == self.INDICATOR else self.GROUP
            raise ConfigurationException(
                f'{config_item} must be a list of valid {_type} types. Got: {types_list}'
            ) from ex
