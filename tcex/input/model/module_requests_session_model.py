"""TcEx Framework Module"""

# third-party
from pydantic import ConfigDict

# first-party
from tcex.input.model.api_model import ApiModel
from tcex.input.model.proxy_model import ProxyModel


class ModuleRequestsSessionModel(ApiModel, ProxyModel):
    """Model Definition

    This model provides all the inputs required by the "tcex.requests_session" module.
    """

    model_config = ConfigDict(extra='ignore')
