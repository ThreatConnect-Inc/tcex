"""Model Map"""

# first-party
from tcex.input.models.advanced_settings_model import AdvancedSettingsModel
from tcex.input.models.aot_execution_enabled_model import AotExecutionEnabledModel
from tcex.input.models.api_model import ApiModel
from tcex.input.models.batch_model import BatchModel
from tcex.input.models.cal_settings_model import CalSettingsModel
from tcex.input.models.logging_model import LoggingModel
from tcex.input.models.organization_model import OrganizationModel
from tcex.input.models.path_model import PathModel
from tcex.input.models.playbook_common_model import PlaybookCommonModel
from tcex.input.models.playbook_model import PlaybookModel
from tcex.input.models.proxy_model import ProxyModel
from tcex.input.models.service_model import ServiceModel
from tcex.input.models.smtp_settings_model import SmtpSettingsModel

# define feature to model map
feature_map = {
    'aotExecutionEnabled': [AotExecutionEnabledModel],
    'appBuilderCompliant': [],
    'advancedRequest': [AdvancedSettingsModel],
    'CALSettings': [CalSettingsModel],
    'fileParams': [],
    'layoutEnabledApp': [],
    'secureParams': [],
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
    'external': [
        ApiModel,
        BatchModel,
        LoggingModel,
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
        # ServiceModel,
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
