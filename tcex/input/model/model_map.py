"""Model Map"""

# first-party
from tcex.input.model.advanced_request_model import _AdvancedRequestModel
from tcex.input.model.aot_execution_enabled_model import AotExecutionEnabledModel
from tcex.input.model.cal_setting_model import CalSettingModel

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

tc_action_map = {
    'Advanced Request': [_AdvancedRequestModel],
}
