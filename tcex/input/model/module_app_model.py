"""TcEx Framework Module"""

from pydantic import ConfigDict

from tcex.input.model.api_model import ApiModel
from tcex.input.model.cert_model import CertModel
from tcex.input.model.path_model import PathModel
from tcex.input.model.playbook_common_model import PlaybookCommonModel
from tcex.input.model.playbook_model import PlaybookModel
from tcex.input.model.proxy_model import ProxyModel
from tcex.input.model.service_model import ServiceModel


class ModuleAppModel(
    ApiModel, CertModel, PathModel, PlaybookCommonModel, PlaybookModel, ProxyModel, ServiceModel
):
    """Model Definition

    This model provides all the inputs required by the "tcex.app" module.
    """

    model_config = ConfigDict(extra='ignore')
