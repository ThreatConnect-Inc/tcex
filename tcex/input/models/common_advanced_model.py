"""Model Definition"""

# first-party
from tcex.input.models.common_model import CommonModel
from tcex.input.models.playbook_common_model import PlaybookCommonModel
from tcex.input.models.playbook_model import PlaybookModel
from tcex.input.models.service_model import ServiceModel


# pylint: disable=too-many-ancestors
class CommonAdvancedModel(CommonModel, PlaybookCommonModel, PlaybookModel, ServiceModel):
    """Model Definition"""
