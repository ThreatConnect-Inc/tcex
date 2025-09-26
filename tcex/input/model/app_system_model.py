"""TcEx Framework Module"""

from tcex.input.model.common_model import CommonModel
from tcex.input.model.organization_model import OrganizationModel


class AppSystemModel(CommonModel, OrganizationModel):
    """Model Definition"""
