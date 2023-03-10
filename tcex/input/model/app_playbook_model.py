"""Model Definition"""

# first-party
from tcex.input.model.common_model import CommonModel
from tcex.input.model.playbook_common_model import PlaybookCommonModel
from tcex.input.model.playbook_model import PlaybookModel


# pylint: disable=too-many-ancestors
class AppPlaybookModel(CommonModel, PlaybookCommonModel, PlaybookModel):
    """Model Definition"""
