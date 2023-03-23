"""Model Definition"""

# third-party
from pydantic import Extra

# first-party
from tcex.input.model.api_model import ApiModel
from tcex.input.model.path_model import PathModel
from tcex.input.model.playbook_common_model import PlaybookCommonModel
from tcex.input.model.playbook_model import PlaybookModel
from tcex.input.model.proxy_model import ProxyModel


class ModuleAppModel(ApiModel, PathModel, PlaybookCommonModel, PlaybookModel, ProxyModel):
    """Model Definition

    This model provides all the inputs required by the "tcex.app" module.
    """

    class Config:
        """Model Config"""

        extra = Extra.ignore
