"""Model Validator/Modifier"""
# standard library
import operator
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# first-party
from tcex.input.field_types.exception import InvalidEmptyValue, InvalidInput

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField


def always_array(allow_empty: Optional[bool] = True) -> List[Any]:
    """Return customized validator that always returns a list."""

    def _always_array(value: Any, field: 'ModelField') -> List[Any]:
        """Return validator."""
        if allow_empty is False and value in [None, '', []]:
            raise InvalidEmptyValue(field_name={field.name})

        if value is None:
            value = []

        if not isinstance(value, list):
            value = [value]

        return value

    return _always_array


def conditional_required(rules: List[Dict[str, str]] = True) -> Any:
    """Return customized validator that validates conditional required fields.

    Example Usage:

    If the severity field is set to 'High' the action field is required.

    MyModel(BaseModel):
        severity: str  # Low, Medium, High
        action: Optional[str]

        _conditional_required = validator('action', allow_reuse=True, always=True, pre=True)(
            conditional_required(
                rules=[{'field': 'severity', 'operation': 'eq', 'value': 'High'}]
            )
        )
    """

    def is_in(input_: str, value: List) -> bool:
        """Return True if input is in value list."""
        return input_ in value

    def not_in(input_: str, value: List) -> bool:
        """Return True if input is NOT in value list."""
        return input_ not in value

    def get_operator(op):
        """Get the corresponding operator"""

        operators = {
            'eq': operator.eq,
            'in': is_in,
            'ne': operator.ne,
            'ni': not_in,
        }
        return operators.get(op, operator.eq)

    def _conditional_required(value: str, field: 'ModelField', values: Dict[str, Any]):
        """Return validator."""
        for rule in rules:
            # the conditional field must be set above the conditionally required field
            conditional_field = values.get(rule.get('field'))
            conditional_operator = get_operator(rule.get('op', 'eq'))
            conditional_value = rule.get('value')

            if conditional_operator(conditional_field, conditional_value) is True and not value:
                raise InvalidInput(field_name=field.name, error='input is conditionally required.')

        return value

    return _conditional_required
