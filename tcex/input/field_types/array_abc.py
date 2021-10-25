"""Abstract Array class containing base validation behavior"""

# standard library
from abc import ABC, abstractmethod
from typing import Any, Generator, List, Union

from .exception import (
    EmptyArrayException,
    EmptyMemberException,
    HeterogenousArrayException,
    InvalidMemberException,
    NullMemberException,
)


class AbstractArray(list, ABC):
    """Abstract Array class that Array implementations should inherit from"""

    _optional = False
    # if array is initialized with a list, this flag decides if the list may contain empty members
    _allow_empty_array_members = True
    # if array is initialized with a list, this flag decides if the list may contain null members
    _allow_null_array_members = True

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
        """Assert that Array is an Array and is not empty."""
        if cls.is_empty(value):
            raise EmptyArrayException('Array must have at least one element.')

    @classmethod
    def assert_not_empty_member(cls, value: Any):
        """Assert that value is of Array's type and that it is not empty."""
        cls.assert_is_member(value)

        if cls.is_empty_member(value):
            raise EmptyMemberException(
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
        """Check if value is of the Array's type.

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

        The passed-in value should be confirmed to be a member of the array before checking
        if it is considered empty. If not a member, InvalidMemberException should be raised.

        Example, for StringArray, the empty value would be considered an empty string: ''.
        This method would return True if the passed-in value is equal to '' in a StringArray
        implementation. Value can be easily checked against multiple empty values using the "in"
        keyword, as in "return value in ['', ...]". Each Array implementation must define
        its own version of this method.

        Return True if value is considered an empty member, False otherwise.
        """
        # inheriting from ABC and list causes abstractmethod to not be enforced. Safety check added.
        # abstractmethod decorator still used, as it provides helpful IDE cues.
        raise NotImplementedError(
            'is_empty_member method must be implemented by child class of AbstractArray'
        )

    @classmethod
    def is_null_member(cls, value: Any) -> bool:
        """Check if value is considered null.

        The passed-in value should be confirmed to be a member of the array before checking
        if it is considered null. If not a member, InvalidMemberException should be raised.

        This default implementation simply checks if the passed value is None; however, more
        complex types may require a more thorough check. For example, an Array member that is a
        dictionary may be considered null if a particular key on the dictionary is None.
        """
        cls.assert_is_member(value)
        return value is None

    @classmethod
    def _assert_homogenous(cls, value: list):
        """Assert that Array contains only members of Array implementation's type.

        An empty Array will not raise a ValueError.

        Note: This method does not take the following into account:

        _allow_empty_array_members
        _allow_null_array_members

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
    def _assert_type(cls, value: Any) -> Union[Any, List[Any]]:
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
            if not cls._optional:
                cls.assert_not_empty(value)
            cls._validate_list_members(value)
        else:
            if not cls._optional:
                cls.assert_not_empty_member(value)
            else:
                cls.assert_is_member(value)

        return value

    @classmethod
    def _validate_list_members(cls, value):
        """Check for empty and null list members depending on class configuration.

        When the Array type is initialized with a list, this internal method checks for null
        and empty members within said list.

        If _allow_empty_array_members is False and an empty member is found, EmptyMemberException
        will be raised.

        if _allow_null_array_members is False and a null member is found, NullMemberException
        will be raised.

        is_empty_member and is_null_member methods will be used to determine if a member is
        empty or null.

        Note: This method also detects when a value is not of the Array's type via is_null_member
        or is_empty_member. Proper exception is raised in that case.

        :param value: The list used to initialize the Array type.
        """

        for member in value:
            if cls.is_null_member(member) and not cls._allow_null_array_members:
                raise NullMemberException(
                    f'Array member "{member}" may not be null. Consider updating value so that '
                    'it is not considered null by Array implementation or set '
                    '_allow_null_array_members to True'
                )
            if cls.is_empty_member(member) and not cls._allow_empty_array_members:
                raise EmptyMemberException(
                    f'Array member "{member}" may not be empty. Consider updating value so '
                    'that it is not considered empty by Array implementation or set '
                    '_allow_empty_array_members to True'
                )

    @classmethod
    def _wrap(cls, value: Any) -> List[Any]:
        """Wrap value in Array (list) if not already an Array."""
        return cls([value]) if not cls.is_array(value) else cls(value)


    @classmethod
    def __get_validators__(cls) -> Generator:
        """Define one or more validators for Pydantic custom type."""
        yield from [cls._assert_type, cls._wrap]
