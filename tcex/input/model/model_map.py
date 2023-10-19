"""TcEx Framework Module"""

# first-party
from tcex.input.model.advanced_request_model import AdvancedRequestModel
from tcex.input.model.app_api_service_model import AppApiServiceModel
from tcex.input.model.app_external_model import AppExternalModel
from tcex.input.model.app_feed_api_service_model import AppFeedApiServiceModel
from tcex.input.model.app_organization_model import AppOrganizationModel
from tcex.input.model.app_playbook_model import AppPlaybookModel
from tcex.input.model.app_system_model import AppSystemModel
from tcex.input.model.app_trigger_service_model import AppTriggerServiceModel
from tcex.input.model.app_webhook_trigger_service_model import AppWebhookTriggerServiceModel
from tcex.input.model.cal_setting_model import CalSettingModel

# from tcex.input.model.service_model import ServiceModel
from tcex.input.model.smtp_setting_model import SmtpSettingModel

# define feature to model map
feature_map = {
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

# define runtime level to model map
runtime_level_map = {
    'apiservice': AppApiServiceModel,
    'feedapiservice': AppFeedApiServiceModel,
    'external': AppExternalModel,
    'organization': AppOrganizationModel,
    'playbook': AppPlaybookModel,
    # special case for non-supported system based Apps
    'system': AppSystemModel,
    'triggerservice': AppTriggerServiceModel,
    'webhooktriggerservice': AppWebhookTriggerServiceModel,
}

tc_action_map = {
    'Advanced Request': [AdvancedRequestModel],
}
