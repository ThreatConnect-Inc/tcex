"""TcEx Framework Module"""
# pylint: disable=no-member,no-self-argument,wrong-import-position

# third-party
from pydantic import BaseModel

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class KeywordModel(BaseModel):
    """Model Definition"""

    value: str | None


class KeywordSectionModel(
    V3ModelABC,
    title='Keyword Section Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Model Definition

    {
        "compareValue": "includes",
        "keywords": [
            {
                "value": "test"
            }
        ]
    }
    """

    compareValue: str | None
    keywords: list[KeywordModel] | None
