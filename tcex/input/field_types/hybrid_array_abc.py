"""Abstract Array class for Arrays that are composed of multiple types"""

# standard library
from abc import abstractmethod
from typing import Any

from .array_abc import AbstractArray


class AbstractHybridArray(AbstractArray):
    """Abstract Array that is used to build Arrays that may hold members of more than one Type.

    For example, an Array implementation that is allowed to hold both String and Binary types
    could be implemented by inheriting from this abstract class. Working is_array_member and
    is_empty_member functionality would be provided out of the box and could be extended if needed.

    Child classes must implement the internal, protected _type_compositions method, which should
    return a list of the Type classes that make up the implemented HybridArray. In the above
    example, _type_compositions would return a list containing StringArray and BinaryArray types.
    Note that this means that _type_compositions is expected to return Types that inherit
    from AbstractArray.
    """

    @classmethod
    @abstractmethod
    def _type_compositions(cls) -> list[AbstractArray]:
        """Return list of Types that make up the HybridArray implementation

        Types contained in the returned list should inherit from HybridArray.
        """
        # inheriting from ABC and list causes abstractmethod to not be enforced. Safety check added.
        # abstractmethod decorator still used, as it provides helpful IDE cues.
        raise NotImplementedError(
            '_type_compositions property must be implemented by child class of AbstractHybridArray'
        )

    @classmethod
    def is_array_member(cls, value: Any) -> bool:
        """Provide base implementation of abstract method in Array parent class.

        In order for a value to be considered a member of HybridArray, it must be considered
        a member of at least one of the HybridArray's type compositions.
        """
        return any([composition.is_array_member(value) for composition in cls._type_compositions()])

    @classmethod
    def is_empty_member(cls, value: Any) -> bool:
        """Provide base implementation of abstract method in Array parent class.

        In order for a value to be considered an empty member of HybridArray, it must first pass
        the checks performed in is_array_member (must first be determined to be a member of
        HybridArray). Once the value is determined to be a member of HybridArray, it must then
        be considered empty by at least one of the HybridArray's type compositions.
        """
        return cls.is_array_member(value) and (
            any([composition.is_empty_member(value) for composition in cls._type_compositions()])
        )

    @classmethod
    def is_null_member(cls, value: Any) -> bool:
        """Extend implementation of method in Array parent class.

        In order for a value to be considered a null member of HybridArray, it must first pass
        the checks performed in is_array_member (must first be determined to be a member of
        HybridArray). Once the value is determined to be a member of HybridArray, it must then
        be considered null by at least one of the HybridArray's type compositions.
        """
        return cls.is_array_member(value) and (
            super().is_null_member(value)
            or any([composition.is_null_member(value) for composition in cls._type_compositions()])
        )
