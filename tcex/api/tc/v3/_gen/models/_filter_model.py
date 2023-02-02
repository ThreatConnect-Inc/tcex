"""Model Definition"""

# standard library
# from typing import Optional

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.backports import cached_property
from tcex.utils import Utils
from tcex.utils.string_operations import CamelString


# pylint: disable=no-self-argument,no-self-use
class ExtraModel(
    BaseModel,
    extra=Extra.forbid,
    title='Extra Model',
    validate_assignment=True,
):
    """Model Definition"""

    comment: str = Field('', description='The comment for the extra.')
    tql_type: str = Field(..., description='The TQL type.')
    typing_type: str = Field(..., description='The Python typing hint type.')


# pylint: disable=no-self-argument,no-self-use
class FilterModel(
    BaseModel,
    alias_generator=Utils().snake_to_camel,
    arbitrary_types_allowed=True,
    extra=Extra.forbid,
    keep_untouched=(cached_property,),
    title='Property Model',
    validate_assignment=True,
):
    """Model Definition"""

    description: str = Field('No description provided.', description='Description of the filter.')
    groupable: bool = Field(False, description='True if the filter is able to be grouped.')
    keyword: CamelString = Field(..., description='The filter keyword.')
    name: CamelString = Field(..., description='The name of the filter.')
    targetable: bool = Field(False, description='True if the filter is able to be targeted.')
    type: str = Field(..., description='The type of the filter.')

    @validator('keyword', 'name', always=True, pre=True)
    def _camel_string(cls, v):
        """Convert to CamelString."""
        return CamelString(v)

    @validator('description', always=True, pre=True)
    def _fix_first_letter_of_sentence(cls, v):
        """Convert to CamelString."""
        if v:
            # ensure the first letter of the sentence is capitalized
            v = v[0].capitalize() + v[1:]
        return v

    @cached_property
    def extra(self) -> ExtraModel:
        """Return the extra model."""
        extra_data = self.__extra_data()
        # print(self.name, self.type, extra_data)
        return ExtraModel(**extra_data)  # type: ignore

    def __extra_data(self) -> dict:
        """Return the extra data."""
        typing_type = self.__calculate_typing_type(self.type)
        tql_type = self.__calculate_tql_type(typing_type)
        return {
            'comment': self.__calculate_comment(self.keyword),
            'typing_type': typing_type,
            'tql_type': tql_type,
        }

    @classmethod
    def __calculate_comment(cls, keyword: str) -> str:
        """Return the calculated filter type."""
        if keyword in ['id', 'type']:
            return '  # pylint: disable=redefined-builtin'
        return ''

    @classmethod
    def __calculate_typing_type(cls, type_: str) -> str:
        """Return the calculated filter type."""
        # hint types for the filter method
        filter_type_map = {
            'Assignee': 'str',
            'BigInteger': 'int',
            'Boolean': 'bool',
            'Date': 'str',
            'DateTime': 'str',
            'Enum': 'str',
            'EnumToInteger': 'str',
            'Integer': 'int',
            'Long': 'int',
            'String': 'str',
            'StringCIDR': 'str',
            'StringLower': 'str',
            'StringUpper': 'str',
            'Undefined': 'str',
            'User': 'str',
        }
        hint_type = filter_type_map.get(type_)

        # fail on any unknown types (core added something new)
        if hint_type is None:
            raise RuntimeError(f'Invalid type of {type_} (Core team added something new?)')

        return hint_type

    @classmethod
    def __calculate_tql_type(cls, typing_type: str):
        """Return the calculated tql type."""
        # tql types for the add_filter method call
        tql_type_map = {
            'bool': 'TqlType.BOOLEAN',
            'int': 'TqlType.INTEGER',
            'str': 'TqlType.STRING',
        }
        return tql_type_map.get(typing_type)
