"""TcEx Framework Module"""
# pylint: disable=no-member,no-self-argument,wrong-import-position

# third-party
from pydantic import Field

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class KeywordModel(
    V3ModelABC,
    title='Keyword Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Model Definition"""

    value: str | None = Field(
        None,
        description='The value of the keyword.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='value',
    )


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

    section_number: int | None = Field(
        None,
        description='The section number of the keyword section.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='sectionNumber',
    )
    compareValue: str | None = Field(
        None,
        description='The compare value for the keyword section.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='compareValue',
    )
    keywords: list[KeywordModel] | None = Field(
        None,
        description='A list of keywords for the keyword section.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='keywords',
    )
