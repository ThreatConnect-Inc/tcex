"""Model Definition"""
# first-party
from tcex.input.models.api_model import ApiModel
from tcex.input.models.batch_model import BatchModel
from tcex.input.models.logging_model import LoggingModel
from tcex.input.models.path_model import PathModel
from tcex.input.models.proxy_model import ProxyModel


class CommonModel(ApiModel, BatchModel, LoggingModel, PathModel, ProxyModel):
    """Common Model"""
