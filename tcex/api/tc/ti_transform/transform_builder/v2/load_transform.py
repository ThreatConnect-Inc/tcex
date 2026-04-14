"""Utility to load transform files."""

# ruff: noqa: TRY301
# standard library
import json
import logging
from inspect import signature
from typing import Literal

# first-party
from tcex.api.tc.ti_transform.model.transform_model import (
    GroupTransformModel,
    IndicatorTransformModel,
)
from tcex.api.tc.ti_transform.ti_predefined_functions import ProcessingFunctions
from tcex.api.tc.ti_transform.transform_builder.v2.errors import TransformError, TransformErrorCause
from tcex.logger.trace_logger import TraceLogger
from tcex.util import Util

_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class LoadTransform:
    """Load and process transform mapping JSON."""

    def __init__(
        self,
        processing_functions: ProcessingFunctions,
        log: logging.Logger = _logger,
    ):
        """Initialize class properties."""
        self.util = Util()
        self.log = log
        self.fns = processing_functions

    def load_transform(
        self,
        mapping_json: dict,
    ) -> GroupTransformModel | IndicatorTransformModel:  # type: ignore
        """Load and process the transform mapping JSON."""
        metadata = mapping_json.pop('metadata', {})
        ti_type = metadata['threatIntelType']
        # transformSchemaVersion = metadata.get('transformSchemaVersion', '1')
        match ti_type:
            case 'group':
                return GroupTransformModel(**self._transform_data(self._normalize(mapping_json)))
            case 'indicator':
                return IndicatorTransformModel(
                    **self._transform_data(self._normalize(mapping_json))
                )

    def _normalize(self, data: dict) -> dict:
        """Normalize the transform data."""
        normalized = {}
        for key, value in data.items():
            normalized_key = self.util.camel_to_snake(key)
            if isinstance(value, dict):
                normalized[normalized_key] = self._normalize(value)
            elif isinstance(value, list):
                normalized[normalized_key] = [
                    self._normalize(item) if isinstance(item, dict) else item for item in value
                ]
            else:
                normalized[normalized_key] = value

        return normalized

    def _transform_data(self, body: dict) -> dict:
        """Transform the data."""
        fields_copy = {**body}
        fields_copy.pop('associated_indicators', None)

        transform_data = {}

        for j, (field_key, field_value) in enumerate(fields_copy.items()):
            match field_key:
                case 'associated_groups' | 'security_labels' | 'tags':
                    for i, item in enumerate(field_value):
                        value = item.get('value', {})
                        try:
                            metadata = item.pop('metadata', {})
                            transform_data.setdefault(field_key, []).append(item)

                            if isinstance(value, dict):
                                self._translate_processing_function(value)
                        except Exception:
                            # best effort to continue processing other items
                            self.log.exception(
                                TransformError(
                                    message=f'Error processing {field_key} field',
                                    cause=TransformErrorCause(
                                        section=self._field_type_to_error_type(field_key),
                                        index=i,
                                        name=self._field_type_to_error_type(field_key),
                                    ),
                                    definition=value,
                                )
                            )
                            raise

                case 'associated_indicators' | 'attributes' | 'file_occurrences':
                    # Remove metadata from attribute objects
                    for i, field in enumerate(field_value):
                        try:
                            metadata = field.pop('metadata', {})
                            if metadata.get('disabled', False):
                                continue

                            for af, ad in list(field.items()):
                                if isinstance(ad, dict):
                                    metadata = ad.pop('metadata', {})
                                    if (
                                        af
                                        in (
                                            'type',
                                            'value',
                                            'summary',
                                            'association_type',
                                        )
                                        and not ad.get('path')
                                        and not ad.get('default')
                                    ):
                                        field.pop(af, None)
                                        self.log.error(
                                            TransformError(
                                                message='{af} required',
                                                cause=TransformErrorCause(
                                                    section=self._field_type_to_error_type(
                                                        field_key
                                                    ),
                                                    index=i,
                                                    name=self._field_type_to_error_type(field_key),
                                                ),
                                                definition=field,
                                            )
                                        )
                                        msg = '{af} required'
                                        raise RuntimeError(msg)

                                    self._translate_processing_function(field[af])

                            transform_data.setdefault(field_key, []).append(field)
                        except Exception:
                            # best effort to continue processing other items
                            self.log.exception(
                                TransformError(
                                    message=f'Error processing {field_key} field',
                                    cause=TransformErrorCause(
                                        section=self._field_type_to_error_type(field_key),
                                        index=i,
                                        name=self._field_type_to_error_type(field_key),
                                    ),
                                    definition=field,
                                )
                            )
                            raise

                case _:
                    try:
                        # skip null configured fields
                        if not field_value:
                            self.log.error(
                                TransformError(
                                    message='missing value',
                                    cause=TransformErrorCause(
                                        section=self._field_type_to_error_type(field_key),
                                        name=field_key,
                                    ),
                                    definition=field_value,
                                )
                            )
                            msg = 'missing value'
                            raise RuntimeError(msg)

                        # Remove metadata from standard fields
                        metadata = field_value.pop('metadata', {})

                        # do not transform disabled fields or fields without path/default
                        if metadata.get('disabled', False) or not (
                            field_value.get('path') or field_value.get('default')
                        ):
                            self.log.error(
                                TransformError(
                                    message='missing value',
                                    cause=TransformErrorCause(
                                        section=self._field_type_to_error_type(field_key),
                                        index=j,
                                        name=field_key,
                                    ),
                                    definition=field_value,
                                )
                            )
                            msg = 'missing value'
                            raise RuntimeError(msg)
                        transform_data[field_key] = field_value

                        self._translate_processing_function(field_value)

                    except Exception:
                        # best effort to continue processing other items
                        self.log.exception(
                            TransformError(
                                message=f'Error processing {field_key} field',
                                cause=TransformErrorCause(
                                    section=self._field_type_to_error_type(field_key),
                                    index=j,
                                    name=field_key,
                                ),
                                definition=field_value,
                            )
                        )
                        raise

        # Clean the transform data by removing empty lists, dicts, and None values
        return self._clean_empty_values(transform_data)

    def _clean_empty_values(self, data: dict) -> dict:
        """Remove keys with empty lists, dicts, or None values recursively."""
        clean_data = {}
        for key, value in data.items():
            if value is None:
                continue

            if isinstance(value, dict):
                # Recursively clean nested dictionaries
                cleaned_dict = self._clean_empty_values(value)
                if cleaned_dict:  # Only add if the cleaned dict is not empty
                    clean_data[key] = cleaned_dict
            elif isinstance(value, list):
                # Recursively clean items in lists
                cleaned_list = []
                for item in value:
                    if isinstance(item, dict):
                        cleaned_item = self._clean_empty_values(item)
                        if cleaned_item:  # Only add if the cleaned dict is not empty
                            cleaned_list.append(cleaned_item)
                    elif item is not None:  # Keep non-None list items
                        cleaned_list.append(item)
                if cleaned_list:  # Only add if the cleaned list is not empty
                    clean_data[key] = cleaned_list
            else:
                # Keep all other non-None values
                clean_data[key] = value
        return clean_data

    def _translate_processing_function(self, mapping: dict):
        """Translate a function definition in transform builder/API format to an actual function."""
        # convert transform function names to callables
        transforms_with_callable = []
        for function in mapping.get('transform', []) or []:
            transforms_with_callable.append(self._function_name_to_callable(function))
        if transforms_with_callable:
            mapping['transform'] = transforms_with_callable
        else:
            mapping.pop('transform', None)

    def _function_name_to_callable(self, function_data: dict):
        """Translate a function definition in transform builder/API format to an actual function."""

        try:
            translated = function_data.copy()
            type_ = 'method' if 'method' in function_data else 'for_each'

            fn_name = function_data[type_]

            # REMOVE: if name is already a callable, return it
            if callable(fn_name):
                return function_data

            fn = getattr(self.fns, fn_name)

            if not fn:
                msg = f'Function {fn_name} not found.'
                raise RuntimeError(msg)

            translated[type_] = fn

            if 'kwargs' in function_data:
                sig = signature(fn)

                for kwarg in function_data['kwargs']:
                    if kwarg not in sig.parameters:
                        msg = f'Unknown argument ("{kwarg}") for function {fn_name}.'
                        raise RuntimeError(msg)

                    annotation = sig.parameters[kwarg].annotation
                    match annotation():
                        case dict():
                            translated['kwargs'][kwarg] = json.loads(function_data['kwargs'][kwarg])
                        case _:
                            translated['kwargs'][kwarg] = sig.parameters[kwarg].annotation(
                                function_data['kwargs'][kwarg]
                            )
        except Exception as ex:
            self.log.exception('Error translating function definition')
            msg = 'Error loading function'
            raise RuntimeError(msg) from ex
        return translated

    def _field_type_to_error_type(
        self,
        field_key: str,
    ) -> Literal[
        'Metadata', 'Associations', 'Attributes', 'File Occurrences', 'Security Labels', 'Tags'
    ]:
        match field_key:
            case 'associated_groups' | 'associated_indicators':
                return 'Associations'
            case 'security_labels':
                return 'Security Labels'
            case 'tags':
                return 'Tags'
            case 'attributes':
                return 'Attributes'
            case 'file_occurrences':
                return 'File Occurrences'
            case _:
                return 'Metadata'
