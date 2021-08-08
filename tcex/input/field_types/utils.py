"""Field Type Validator methods"""
# first-party
from tcex.sessions import TcSessionSingleton
from tcex.threat_intelligence import ThreatIntelUtils


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
