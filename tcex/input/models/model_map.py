"""Model Map"""

# first-party
from tcex.input.models.advanced_request_model import _AdvancedRequestModel
from tcex.input.models.aot_execution_enabled_model import AotExecutionEnabledModel
from tcex.input.models.cal_settings_model import CalSettingsModel
from tcex.input.models.common_advanced_model import CommonAdvancedModel
from tcex.input.models.common_model import CommonModel
from tcex.input.models.organization_model import OrganizationModel

# from tcex.input.models.playbook_common_model import PlaybookCommonModel
from tcex.input.models.playbook_model import PlaybookModel

# from tcex.input.models.service_model import ServiceModel
from tcex.input.models.smtp_settings_model import SmtpSettingsModel

# define feature to model map
feature_map = {
    'aotExecutionEnabled': [AotExecutionEnabledModel],
    'appBuilderCompliant': [],
    # 'advancedRequest': [],
    'CALSettings': [CalSettingsModel],
    'fileParams': [],
    'layoutEnabledApp': [],
    'secureParams': [],
    'smtpSettings': [SmtpSettingsModel],
    # features for TC Playbook loop prevention
    'CreatesGroup': [],
    'CreatesIndicator': [],
    'CreatesSecurityLabel': [],
    'CreatesTag': [],
    'DeletesGroup': [],
    'DeletesIndicator': [],
    'DeletesSecurityLabel': [],
    'DeletesTag': [],
}

# TODO: [HIGH] - rework this to code
# define runtime level to model map
runtime_level_map = {
    'apiservice': [
        CommonAdvancedModel
        # CommonModel,
        # PlaybookCommonModel,
        # ServiceModel,
    ],
    'feedapiservice': [
        CommonAdvancedModel
        # CommonModel,
        # PlaybookCommonModel,
        # ServiceModel,
    ],
    'external': [
        CommonModel,
    ],
    'organization': [
        CommonModel,
        OrganizationModel,
    ],
    'playbook': [
        CommonAdvancedModel,
        # CommonModel,
        # PlaybookCommonModel,
        PlaybookModel,
    ],
    'triggerservice': [
        CommonAdvancedModel
        # CommonModel,
        # PlaybookCommonModel,
        # ServiceModel,
    ],
    'webhooktriggerservice': [
        CommonAdvancedModel
        # CommonModel,
        # PlaybookCommonModel,
        # ServiceModel,
    ],
}

tc_action_map = {
    'Advanced Request': [_AdvancedRequestModel],
}
