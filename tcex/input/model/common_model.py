"""TcEx Framework Module"""

# first-party
from tcex.input.model.api_model import ApiModel
from tcex.input.model.batch_model import BatchModel
from tcex.input.model.cert_model import CertModel
from tcex.input.model.logging_model import LoggingModel
from tcex.input.model.path_model import PathModel
from tcex.input.model.proxy_model import ProxyModel


class CommonModel(ApiModel, BatchModel, CertModel, LoggingModel, PathModel, ProxyModel):
    """Model Definition"""
