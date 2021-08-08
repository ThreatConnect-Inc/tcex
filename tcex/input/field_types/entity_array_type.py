"""Always Array Validator"""
# standard library
from typing import Callable, Iterator, Optional, Union

# first-party
from tcex.input.field_types.utils import array_validator


class EntityArrayType(list):
    """IndicatorArray Field Types"""

    __input_type__ = 'String'
    __playbook_data_type__ = ['String', 'StringArray', 'TCEntity', 'TCEntityArray']
    _optional = False

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Define one or more validators for Pydantic custom type."""
        yield cls._validate

    def __iter__(self) -> Iterator[Union[dict, str]]:
        """Iterate over all items."""
        # auto-filter: only include indicator types
        yield from self._auto_filter(list(super().__iter__()))

    @classmethod
    def _auto_filter(cls, items: list) -> list[dict, str]:
        """Auto filter list - only include specific types."""
        return items  # pragma: no cover

    @classmethod
    def _validate(cls, value: Union[dict, list[dict], list[str], str]) -> list[str]:
        """Ensure an list is always returned.

        Due to the way that pydantic does validation the
        method will never be called if value is None.
        """
        # Coerce provided value to list type if required
        if not isinstance(value, list):
            value = [value]

        # run auto filter
        value = [v for v in cls._auto_filter(value)]  # pylint: disable=unnecessary-comprehension

        # validate data if type is not Optional
        if cls._optional is False:
            array_validator(value)

        return cls(value)

    def filter(
        self, key: str, values: Union[list[str], str], return_key: Optional[str] = None
    ) -> list:
        """Filter value by type and optional return a single value for provided key."""
        if isinstance(values, str):
            values = [values]

        for item in self:
            if isinstance(item, dict):  # TCEntity
                if key in item and item.get(key) in values:
                    if return_key is not None:
                        yield item.get(return_key)
                    else:
                        yield item

    def filter_type(self, values: Union[list[str], str], return_key: Optional[str] = None) -> list:
        """Filter value by type and optional return a single value for provided key."""
        yield from self.filter(key='type', values=values, return_key=return_key)

    def values(self, values: Union[list[str], str]) -> list:
        """Return only the value field if TcEntity types are provided."""
        yield from self.filter(key='type', values=values, return_key='value')
