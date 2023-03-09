"""Model Map"""

# first-party
from tcex.input.model.advanced_request_model import _AdvancedRequestModel
from tcex.input.model.aot_execution_enabled_model import AotExecutionEnabledModel
from tcex.input.model.cal_setting_model import CalSettingModel
from tcex.input.model.common_advanced_model import CommonAdvancedModel
from tcex.input.model.common_model import CommonModel
from tcex.input.model.organization_model import OrganizationModel

# from tcex.input.model.playbook_common_model import PlaybookCommonModel
from tcex.input.model.playbook_model import PlaybookModel

# from tcex.input.model.service_model import ServiceModel
from tcex.input.model.smtp_setting_model import SmtpSettingModel

# define feature to model map
feature_map = {
    'aotExecutionEnabled': [AotExecutionEnabledModel],
    'appBuilderCompliant': [],
    # 'advancedRequest': [],
    'CALSettings': [CalSettingModel],
    'fileParams': [],
    'layoutEnabledApp': [],
    'secureParams': [],
    'smtpSettings': [SmtpSettingModel],
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
