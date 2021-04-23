"""TCEntity Model"""
# third-party
from pydantic import BaseModel, Extra


class TCEntityModel(BaseModel):
    """Model for TCEntity Input."""

    id: int
    type: str
    value: str

    class Config:
        """Model Config"""

        validate_assignment = True
        extra = Extra.allow
