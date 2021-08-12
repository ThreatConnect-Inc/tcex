"""Abstract Array class containing base validation behavior"""

# standard library
from abc import ABC, abstractmethod
from typing import Any, Generator, Union

from .exception import EmptyArrayException, HeterogenousArrayException, InvalidMemberException


class AbstractArray(list, ABC):
    """Abstract Array class that Array implementations should inherit from"""

    _optional = False

    @classmethod
    def assert_homogenous(cls, value: list):
        """Assert that Array contains only members of Array implementation's type.

        An empty Array will not raise a ValueError.

        This method relies on is_array_member, which is specific to the current Array
        implementation.
        """
        for member in value:
            try:
                cls.assert_is_member(member)
            except InvalidMemberException as ex:
                raise HeterogenousArrayException(
                    f'Value {value} contains invalid member. {ex}'
                ) from ex

    @classmethod
    def assert_is_array(cls, value: Any):
        """Assert that value is an Array"""
        if not cls.is_array(value):
            raise ValueError(f'Value "{value}" is not an Array.')

    @classmethod
    def assert_is_member(cls, value: Any):
        """Assert that the value is of the Array's type.

        In other words, check that the value could be a member of the current Array implementation.
        """
        if not cls.is_array_member(value):
            raise InvalidMemberException(
                f'Value "{value}" of type {type(value)} is not of Array\'s type.'
            )

    @classmethod
    def assert_not_empty(cls, value: list):
        """Assert that Array is an Array and is not empty.

        if Array implementation is marked as optional, this method only asserts that the passed-in
        value is an Array (list) and will not assert that the value is not empty.
        """
        if cls.is_empty(value) and not cls._optional:
            raise EmptyArrayException('Array must have at least one element.')

    @classmethod
    def assert_not_empty_member(cls, value: Any):
        """Assert that value is of Array's type and that it is not empty.

        If Array implementation is marked as optional, this method only asserts that the value is of
        the Array's type and will not assert that the value is not empty.
        """
        cls.assert_is_member(value)

        if not cls._optional and cls.is_empty_member(value):
            raise InvalidMemberException(
                f'Value "{value}" may not be empty. Consider using Optional field '
                'definition if empty values are necessary.'
            )

    @classmethod
    def is_array(cls, value: Any) -> bool:
        """Return True if value is Array (list), False otherwise."""
        return isinstance(value, list)

    @classmethod
    @abstractmethod
    def is_array_member(cls, value: Any) -> bool:
        """Check if value is of the StringArray's type.

        Each Array implementation must define its own version of this method.
        Return True if value is considered to be a member of the Array implementation
        (is of the Array's type), False otherwise.
        """
        # inheriting from ABC and list causes abstractmethod to not be enforced. Safety check added.
        # abstractmethod decorator still used, as it provides helpful IDE cues.
        raise NotImplementedError(
            'is_array_member method must be implemented by child class of AbstractArray'
        )

    @classmethod
    def is_empty(cls, value: list) -> bool:
        """Check if Array is empty. Return True if empty, False otherwise.

        This method asserts that the passed-in value is an Array (list). A ValueError will
        be raised if the passed-in value is not an Array.
        """
        try:
            cls.assert_is_array(value)
        except ValueError as ex:
            raise ValueError(
                f'Unable to check if Array is empty. Value is not an Array: {value}'
            ) from ex

        return not bool(value)

    @classmethod
    @abstractmethod
    def is_empty_member(cls, value: Any) -> bool:
        """Check if value is equal to what is considered the empty value of the Array's Type

        Example, for StringArray, the empty value would be considered an empty string: ''.
        This method would return True if the passed-in value is equal to '' in a StringArray
        implementation. Value can be easily checked against multiple empty values using the "in"
        keyword, as in "return value in ['', ...]". Each Array implementation must define
        its own version of this method.

        Return True if value equal to the Array's empty value, False otherwise.
        """
        # inheriting from ABC and list causes abstractmethod to not be enforced. Safety check added.
        # abstractmethod decorator still used, as it provides helpful IDE cues.
        raise NotImplementedError(
            'is_empty_member method must be implemented by child class of AbstractArray'
        )

    @classmethod
    def assert_type(cls, value: Any) -> Union[Any, list[Any]]:
        """Assert that the value is either an Array or an Array member.

        if Array implementation is not marked as optional and the passed-in value is an Array, this
        method asserts that the value is not an empty Array.

        if passed-in value is an Array, it will be asserted to contain only values that are of
        the Array implementation's type regardless of whether Array implementation is marked as
        optional or not.

        If the value is not an Array, it will be asserted to be a value of the Array's type
        regardless of whether the Array implementation is marked as optional or not. If the Array
        implementation is not marked as optional, then the value will also be asserted to not be an
        empty array member. See is_empty_member class method for details.

        Note: this method combines the different assertion methods of this class in order to
        provide a validator that can be easily leveraged within the __get_validators__ method,
        as this class is meant to be used as a Pydantic type. Returns unchanged value in order
        to conform to Pydantic validator behavior
        """
        if cls.is_array(value):
            cls.assert_not_empty(value)
            cls.assert_homogenous(value)
        else:
            cls.assert_not_empty_member(value)

        return value

    @classmethod
    def wrap(cls, value: Any) -> list[Any]:
        """Wrap value in Array (list) if not already an Array."""
        return cls([value]) if not cls.is_array(value) else cls(value)

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Define one or more validators for Pydantic custom type."""
        yield from [cls.assert_type, cls.wrap]
