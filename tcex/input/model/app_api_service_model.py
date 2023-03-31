"""TcEx Framework Module"""

# first-party
from tcex.input.model.common_model import CommonModel
from tcex.input.model.playbook_common_model import PlaybookCommonModel
from tcex.input.model.service_model import ServiceModel


class AppApiServiceModel(CommonModel, PlaybookCommonModel, ServiceModel):
    """Model Definition"""
