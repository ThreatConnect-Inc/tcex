"""Model Definition"""
# first-party
from tcex.input.models import ApiModel, BatchModel, LoggingModel, PathModel, ProxyModel


class CommonModel(ApiModel, BatchModel, LoggingModel, PathModel, ProxyModel):
    """Common Model"""
