"""TcEx Framework Module

This module provides the EditChoice field type for TcEx Apps, which handles validation
and processing of choice-based input fields with pre-defined values.

The EditChoice field type is designed to work with App parameters that have a limited
set of valid values defined in the install.json configuration. It provides strict
validation against these predefined choices while offering flexibility through
customization options.

Key Features:
- Validates input against predefined choices from install.json
- Case-insensitive matching with proper case preservation
- Optional support for additional values not in the predefined list
- Value transformation capabilities for mapping internal to display values
- Integration with ThreatConnect's variable resolution system
- Comprehensive error handling with descriptive messages

Usage Examples:
    # Basic usage with strict validation
    my_choice: EditChoice = Field(...)

    # Allow additional values beyond predefined choices
    flexible_choice: edit_choice(allow_additional=True) = Field(...)

    # Transform values for display or processing
    transformed_choice: edit_choice(
        value_transformations={'internal': 'Display Value'}
    ) = Field(...)
"""

import re
from typing import Any, ClassVar

from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic.dataclasses import dataclass
from pydantic_core import core_schema

from tcex.api.tc.util.threat_intel_util import ThreatIntelUtil
from tcex.app.config.install_json import InstallJson
from tcex.input.field_type.exception import InvalidEmptyValue, InvalidInput, InvalidType
from tcex.registry import registry


@dataclass(frozen=True, init=False)
class EditChoice(str):
    """EditChoice Field Type for TcEx Apps

    A specialized string-based field type that validates input values against a predefined
    set of choices defined in the App's install.json configuration. This field type ensures
    data integrity by restricting input to valid options while providing flexibility through
    customization features.

    Key Characteristics:
    - Inherits from str for seamless string operations
    - Immutable (frozen=True) to prevent modification after creation
    - Validates against install.json valid_values configuration
    - Supports case-insensitive matching with proper case preservation
    - Integrates with ThreatConnect's variable resolution system

    Supported App Parameter Types:
    - EditChoice (pre-defined values from install.json)

    Limitations:
    - Magic Variables (e.g. ${OWNERS}) are not supported
    - Dynamic choice values are not supported (use pre-defined only)

    Class Variables:
        _allow_additional (bool): Controls whether values outside the predefined
            choices are permitted. Default: False
        _value_transformations (dict | None): Optional mapping for transforming
            input values to different output values
    """

    _allow_additional: ClassVar[bool] = False
    _value_transformations: ClassVar[dict | None] = None

    @classmethod
    def _validate(cls, value: str, info: core_schema.ValidationInfo) -> str:
        """Primary validation method for EditChoice fields.

        This method orchestrates the complete validation pipeline for EditChoice values,
        ensuring that input data meets all requirements before being accepted. It serves
        as the entry point for Pydantic's validation system.

        Validation Pipeline:
        1. Type validation - Ensures input is a string
        2. Value modification - Strips whitespace from input
        3. Choice validation - Validates against predefined valid values
        4. Transformation - Applies any configured value transformations

        Args:
            value (str): The input value to validate and process
            info (core_schema.ValidationInfo): Pydantic validation context containing
                field metadata such as field_name

        Returns:
            str: The validated and potentially transformed value

        Note:
            If field_name is None (which can happen in certain Pydantic contexts),
            the value is returned without validation. This is a safety mechanism
            to prevent validation errors in edge cases.

        Raises:
            InvalidType: If the input value is not a string
            InvalidEmptyValue: If the input value is an empty string
            InvalidInput: If the input value is not in the valid choices and
                additional values are not allowed
        """
        """Run validators / modifiers on input."""
        if info.field_name is None:
            return value

        field_name = info.field_name
        value = cls.validate_type(value, field_name)
        value = cls.modifier_strip(value)
        value = cls.validate_valid_values(value, field_name)
        return value  # noqa: RET504

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.AfterValidatorFunctionSchema:
        """Configure Pydantic core schema for EditChoice validation.

        This method is part of Pydantic v2's core schema system and defines how
        the EditChoice field should be validated within the Pydantic framework.
        It sets up the validation pipeline that will be executed when Pydantic
        processes fields of this type.

        The method creates a validation schema that:
        - Starts with basic string validation (core_schema.str_schema())
        - Applies custom validation through _validate method
        - Passes validation context information including field name
        - Ensures validation occurs after basic type conversion

        Args:
            source (type[Any]): The source type being processed (typically EditChoice)
            handler (GetCoreSchemaHandler): Pydantic's schema generation handler
                that provides access to field metadata and context

        Returns:
            core_schema.AfterValidatorFunctionSchema: A Pydantic core schema
                configuration that defines the validation pipeline for this field type

        Technical Details:
            - Uses with_info_after_validator_function to access validation context
            - Ensures field_name is available during validation for error reporting
            - Integrates seamlessly with Pydantic's validation system
        """
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            field_name=handler.field_name,
        )

    @classmethod
    def modifier_strip(cls, value: str) -> str:
        r"""Strip leading and trailing whitespace from the input value.

        This modifier method removes whitespace from both ends of the input string,
        ensuring consistent data formatting and preventing issues caused by
        accidental whitespace in user input or configuration files.

        Features:
        - Removes leading whitespace (spaces, tabs, newlines)
        - Removes trailing whitespace (spaces, tabs, newlines)
        - Preserves internal whitespace within the value
        - Safe operation that doesn't modify the original string

        Args:
            value (str): The input string to strip of whitespace

        Returns:
            str: The input string with leading and trailing whitespace removed

        Examples:
            >>> EditChoice.modifier_strip('  hello world  ')
            "hello world"
            >>> EditChoice.modifier_strip('\tvalue\n')
            "value"
            >>> EditChoice.modifier_strip('no  internal  change')
            "no  internal  change"
        """
        return value.strip()

    @classmethod
    def validate_type(cls, value: str, field_name: str) -> str:
        """Validate that the input value is of string type.

        This method performs type validation to ensure that the input value is
        a string, which is required for EditChoice fields. Type validation is
        the first step in the validation pipeline and prevents processing of
        incompatible data types.

        Type Safety Features:
        - Strict type checking using isinstance()
        - Clear error messages with field context
        - Prevention of implicit type conversions
        - Early validation to catch type mismatches

        Args:
            value (str): The input value to validate for string type
            field_name (str): The name of the field being validated, used for
                error reporting and context

        Returns:
            str: The original value if it passes type validation

        Raises:
            InvalidType: If the input value is not a string type. The exception
                includes detailed information about:
                - The field name where the error occurred
                - The expected type (str)
                - The actual type that was provided

        Examples:
            >>> EditChoice.validate_type('valid_string', 'my_field')
            "valid_string"
            >>> EditChoice.validate_type(123, 'my_field')
            InvalidType: Field 'my_field' expected type (str), got <class 'int'>
        """
        if not isinstance(value, str):
            raise InvalidType(
                field_name=field_name,
                expected_types='(str)',
                provided_type=type(value),
            )
        return value

    @classmethod
    def validate_valid_values(cls, value: str, field_name: str) -> str:
        """Validate input value against predefined choices and apply transformations.

        This is the core validation method that ensures the input value matches one of
        the predefined valid choices from the App's install.json configuration. It
        implements sophisticated matching logic, variable resolution, and value
        transformation capabilities.

        Validation Process:
        1. Empty value check - Rejects empty strings
        2. Install.json lookup - Retrieves valid values for the field
        3. Field name normalization - Handles multichoice field naming conventions
        4. Variable resolution - Processes ThreatConnect variables in valid values
        5. Case-insensitive matching - Finds matches regardless of case
        6. Case preservation - Maintains the original case from valid values
        7. Additional values check - Optionally allows values not in predefined list
        8. Value transformation - Applies configured value mappings

        Args:
            value (str): The input value to validate against predefined choices
            field_name (str): The field name used for lookup in install.json and
                error reporting

        Returns:
            str: The validated value, potentially with:
                - Corrected case (matching the predefined choice)
                - Applied transformations (if configured)

        Raises:
            InvalidEmptyValue: If the input value is an empty string
            InvalidInput: If the input value doesn't match any valid choice and
                additional values are not allowed

        Technical Details:
            - Supports multichoice fields (handles underscore-prefixed field names)
            - Integrates with ThreatConnect's variable resolution system
            - Implements case-insensitive matching with case preservation
            - Allows runtime configuration of additional value acceptance
            - Supports value transformation for internal-to-display mapping

        Configuration Options:
            - _allow_additional: Allow values not in predefined list
            - _value_transformations: Dictionary mapping input to output values

        Examples:
            # Case-insensitive matching with case preservation
            valid_values = ["Option1", "Option2"]
            validate_valid_values("option1", "field") -> "Option1"

            # Value transformation
            _value_transformations = {"internal": "Display Value"}
            validate_valid_values("internal", "field") -> "Display Value"
        """
        if value == '':
            raise InvalidEmptyValue(field_name)

        # fix addressing PLAT-14751
        pattern = re.compile(r'^\${(users|user_groups):.*?}$', re.IGNORECASE)
        if pattern.match(value):
            value = re.sub(r'^\${(users|user_groups):|}$', '', value, flags=re.IGNORECASE)

        ij = InstallJson()
        param = ij.model.get_param(field_name)

        # TODO: [high] figure out a better way ...
        if param is None:
            # for a multichoice input field, pydantic prefixes the name with an underscore,
            # this breaks the lookup based on the "name" field in the install.json. Strip
            # the underscore to get the correct param name.
            param = ij.model.get_param(field_name.lstrip('_'))

        ti_utils = ThreatIntelUtil(registry.session_tc)
        valid_values = [] if param is None else param.valid_values
        _valid_values = ti_utils.resolve_variables(valid_values)
        for vv in _valid_values:
            if vv.lower() == value.lower():
                value = vv
                break
        else:
            if cls._allow_additional is False:
                raise InvalidInput(
                    field_name=field_name,
                    error=f'provided value {value} is not a valid value {_valid_values}',
                )

        if isinstance(cls._value_transformations, dict):
            value = cls._value_transformations.get(value, value)

        return value


def edit_choice(
    allow_additional: bool = False, value_transformations: dict[str, str] | None = None
) -> type[EditChoice]:
    """Create a customized EditChoice field type with specific validation behavior.

    This factory function creates a dynamically configured EditChoice class with
    custom validation rules and transformation capabilities. It enables fine-tuned
    control over how choice fields behave in different contexts without requiring
    inheritance or class modification.

    Configuration Capabilities:
    - Allow or restrict values outside predefined choices
    - Transform input values to different output representations
    - Maintain all standard EditChoice validation features
    - Create reusable field type configurations

    Use Cases:
    - Flexible choice fields that accept user-defined values
    - Choice fields with display name transformations
    - Legacy system integration with value mapping
    - Dynamic choice behavior based on runtime conditions

    Args:
        allow_additional (bool, optional): Controls whether the field accepts values
            that are not found in the install.json valid_values list. When True,
            any string value is accepted after basic validation. When False (default),
            only predefined values are allowed. Defaults to False.

        value_transformations (dict[str, str] | None, optional): A dictionary that
            defines how input values should be transformed to output values. The keys
            should match the valid values defined in install.json, and the values
            represent the desired output format. If a transformation is not found,
            the original value is preserved. Defaults to None.

    Returns:
        type[EditChoice]: A dynamically created EditChoice subclass with the
            specified configuration. This class can be used directly as a Pydantic
            field type annotation.

    Configuration Examples:
        # Standard strict validation (default behavior)
        basic_choice: edit_choice() = Field(...)

        # Allow additional values beyond predefined choices
        flexible_choice: edit_choice(allow_additional=True) = Field(...)

        # Transform internal values to display values
        display_choice: edit_choice(
            value_transformations={
                'db_value': 'Database Value',
                'api_value': 'API Value',
                'internal_code': 'User Friendly Name'
            }
        ) = Field(...)

        # Combine flexibility with transformations
        advanced_choice: edit_choice(
            allow_additional=True,
            value_transformations={'legacy': 'Modern Equivalent'}
        ) = Field(...)

    Transformation Behavior:
        When value_transformations is provided:
        1. Input validation occurs normally (type, empty, choice validation)
        2. If input matches a predefined choice, case is preserved from valid_values
        3. Transformation lookup is performed using the corrected value
        4. If transformation exists, the transformed value is returned
        5. If no transformation exists, the original (case-corrected) value is returned

    Integration Notes:
        - Fully compatible with Pydantic field definitions
        - Inherits all EditChoice validation and error handling
        - Maintains integration with ThreatConnect variable resolution
        - Works seamlessly with install.json configuration system
        - Supports all Pydantic field options (default, description, etc.)

    Technical Implementation:
        - Creates a new class dynamically using type()
        - Sets class variables as namespace attributes
        - Inherits all methods from the base EditChoice class
        - Maintains immutability and validation pipeline
    """
    namespace = {
        '_value_transformations': value_transformations,
        '_allow_additional': allow_additional,
    }
    return type('CustomEditChoice', (EditChoice,), namespace)
