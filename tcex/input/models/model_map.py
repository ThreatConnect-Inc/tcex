"""Model Map"""

from .advanced_settings_model import AdvancedSettingsModel
from .aot_execution_enabled_model import AotExecutionEnabledModel
from .api_model import ApiModel
from .batch_model import BatchModel
from .cal_settings_model import CalSettingsModel
from .logging_model import LoggingModel
from .organization_model import OrganizationModel
from .path_model import PathModel
from .playbook_common_model import PlaybookCommonModel
from .playbook_model import PlaybookModel
from .proxy_model import ProxyModel
from .service_model import ServiceModel
from .smtp_settings_model import SmtpSettingsModel

# define feature to model map
feature_map = {
    'aotExecutionEnabled': [AotExecutionEnabledModel],
    'advancedRequest': [AdvancedSettingsModel],
    'CALSettings': [CalSettingsModel],
    'smtpSettings': [SmtpSettingsModel],
}

# define runtime level to model map
runtime_level_map = {
    'apiservice': [
        ApiModel,
        BatchModel,
        LoggingModel,
        PathModel,
        PlaybookCommonModel,
        ProxyModel,
        ServiceModel,
    ],
    'organization': [
        ApiModel,
        BatchModel,
        LoggingModel,
        OrganizationModel,
        PathModel,
        ProxyModel,
    ],
    'playbook': [
        ApiModel,
        BatchModel,
        LoggingModel,
        PathModel,
        PlaybookCommonModel,
        PlaybookModel,
        ProxyModel,
        ServiceModel,
    ],
    'triggerservice': [
        ApiModel,
        BatchModel,
        LoggingModel,
        PathModel,
        PlaybookCommonModel,
        ProxyModel,
        ServiceModel,
    ],
    'webhooktriggerservice': [
        ApiModel,
        BatchModel,
        LoggingModel,
        PathModel,
        PlaybookCommonModel,
        ProxyModel,
        ServiceModel,
    ],
}
