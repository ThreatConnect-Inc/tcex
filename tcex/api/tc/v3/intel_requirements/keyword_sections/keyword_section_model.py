"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position

# third-party
from pydantic import Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


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

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    section_number: int | None = Field(
        None,
        description='The section number of the keyword section.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='sectionNumber',
    )
    compare_value: str | None = Field(
        None,
        description='The compare value for the keyword section.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='compareValue',
    )
    keywords: list[dict] | None = Field(
        [],
        description='A list of keywords for the keyword section.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='keywords',
    )
