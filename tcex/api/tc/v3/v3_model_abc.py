"""TcEx Framework Module"""

# standard library
import datetime
import hashlib
import json
import logging
from abc import ABC
from json import JSONEncoder
from typing import Any, Self

# third-party
from pydantic import BaseModel, PrivateAttr

# first-party
from tcex.logger.trace_logger import TraceLogger

# get tcex logger

_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class CustomJSONEncoder(JSONEncoder):
    """Format object in JSON data."""

    def default(self, o: Any) -> str:
        """Format object"""
        if isinstance(o, BaseModel):
            raise ValueError(
                f'Object of type {type(o)} is not JSON serializable. '
                'Please verify that the object has been converted to a dictionary.'
            )
        if isinstance(o, datetime.date | datetime.datetime):
            return o.isoformat()
        return o


class V3ModelABC(BaseModel, ABC, allow_population_by_field_name=True):
    """V3 Base Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _dict_hash: str = PrivateAttr()
    _log = _logger
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)
    id: int | None = None

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(**kwargs)

        # when "id" field is present it indicates that the data was returned from the
        # API, otherwise the assumption is that the developer staged the data during
        # instantiation of the object. Keyword Section Model is the only exception to
        # this rule.
        # pylint: disable=no-member
        if (
            kwargs
            and hasattr(self, 'id')
            and self.id is None
            and self.__config__.title != 'Keyword Section Model'
        ):
            self._staged = True

        # store initial dict hash of model
        self._dict_hash = self.gen_model_hash(self.json(sort_keys=True))

    def _calculate_field_inclusion(
        self, field: str, method: str, mode: str | None, nested: bool, property_: dict, value: Any
    ) -> bool:
        """Return True if the field is calculated to be included."""

        # INDICATOR ID RULE: If an indicator has a ID set, then the indicator fields
        #     cannot be provided (updateable is false) or the API request will fail.
        #     Since Note model CAN update the `text` field we need to specifically state
        #     that this test is for the `Indicator Model` only.
        if (
            self.__config__.title == 'Indicator Model'
            and self.id is not None
            and field
            in [
                'address',
                'file',
                'hostName',
                'ip',
                'md5',
                'sha1',
                'sha256',
                'text',
                'url',
                'value1',
                'value2',
                'value3',
            ]
        ):
            return False

        # MODE DELETE RULE: The "id" should be the only field included when delete mode
        #     is enabled. "relationship" is required for FileActions upon delete mode as well.
        if mode == 'delete' and nested is True and field not in ['id', 'name', 'relationship']:
            return False

        # ID RULE: The "id" should not be included for ANY HTTP method on parent object,
        #     but for nested objects the "id" field should be included when available.
        #     PLAT-4074 - updating nested object using "replace"
        if field == 'id' and nested is True and value:
            return True

        # NESTED RULE: For nested objects the body should use the valid POST fields
        #    instead of the PUT fields if id is not available. This handles including
        #    artifact type, attributes and other fields that are needed on the nested object.
        if method == 'PUT' and nested is True and not self.id:  # pylint: disable=no-member
            method = 'POST'

        # SHARED TYPE RULE: For nested "shared types" objects the body should use the valid
        #    PUT methods instead of the POST fields.  This handles not sending owner field
        #    for tag.
        if method == 'POST' and nested is True and self._shared_type is True:
            method = 'PUT'

        # METHOD RULE: If the current method is in the property "methods" list the
        #     field should be included when available.
        if method in property_.get('methods', []) and (value or value in [0, False]):
            return True

        # DEFAULT RULE -> Fields should not be included unless the match a previous rule.
        return False

    # pylint: disable=too-many-return-statements
    def _calculate_nested_inclusion(self, method: str, mode: str | None, model: Self) -> bool:
        """Return True if the field is calculated to be included.

        Case Management Nested Logic:
        * CM Types (e.g., artifacts, notes, task, etc) -> behavior is APPEND and duplicates will
            be created if resent. Object with an ID should never be sent in parent update. Updating
            the nested object should be done directly on the object.
        * User/User Group Types -> ???
        * Attributes -> behavior uses MODE and supports append, delete, and replace.
        * Tags -> behavior is REPLACE on tags so all tags that need to be on the CM object should
            be include in both POST and PUT.

        Threat Intelligence Nested Logic:
        * Associations (e.g., groups, indicators, victim assets) -> behavior uses MODE and supports
            append, delete, and replace.
        * Attributes -> behavior uses MODE and supports append, delete, and replace.
        * Tags -> behavior uses MODE and supports append, delete, and replace.
        * Security Labels -> behavior uses MODE and supports append, delete, and replace.

        """
        # EMPTY RULE: If there is no value in the model it should NOT be INCLUDED.
        if not model:
            return False

        # METHOD RULE: When HTTP method is DELETE or GET nested objects should NOT be INCLUDED.
        if method in ['DELETE', 'GET']:
            return False

        # STAGED RULE: Any nested object provided by developer should be INCLUDED.
        if model._staged is True:
            return True

        # POST RULE: When method is POST all nested object should be INCLUDED.
        if method == 'POST':
            return True

        # Current Object Restrictions:
        # * The method is PUT
        # * The nested object was NOT added via the stage_xxx method
        # * The nested object contains a ID or Name Field
        # * The nested object could either have been set during initializing the object or fetched.

        # CM and TI endpoint behaves differently. Start with rules based on the parent type,
        # then add more specific rules.

        if self._cm_type is True:
            #
            # CM PARENT TYPES
            #

            # Nested Types:
            # * CM Types (Artifact, Artifact Type, Case, Note, Task, Workflow Event/Template)
            # * Attributes
            # * Group (currently read-only)
            # * Tags
            # * Users

            # Coverage:
            # * Downloaded from API (e.g., case.get(id=123))
            # * Added on instantiation
            # * Added with stage_xxx() method

            if model._cm_type is True:
                # RULE: Short-Circuit Nested CM Types
                # Nested CM types are updated through their direct endpoints and should
                #    never be INCLUDED when updating the parent. For new nested CM types
                #    added with the stage_xxx() method, the STAGED RULE would trigger
                #    before this rule.
                return False

            if model._shared_type is True:
                # RULE: Nested Tags
                # Nested tags on a parent CM type behave as REPLACE mode and need to be
                #     INCLUDED to prevent being removed.
                return True

            # RULE: Nested Attributes w/ APPEND mode
            # Nested attributes on a parent CM type use the mode feature. When the mode
            #     is APPEND and has been UPDATED, then the attributes should be INCLUDED.
            #     For new nested objects added with the stage_xxx() method, the STAGED
            #     RULE would trigger first.
            # A secondary PATTERN consideration is that attributes can be immediately
            #     updated using the attribute.updated() method. While this isn't as
            #     efficient as updating them all in one request, it's is a simpler
            #     development design pattern.

            if mode == 'replace':
                # RULE: Nested Attributes w/ REPLACE mode
                # Nested attributes on a parent CM type use the mode feature. When the mode
                #     is REPLACE the attributes should be INCLUDED.
                return True

            # RULE: Nested Attributes w/ DELETE mode
            # Nested attributes on a parent CM type use the mode feature. When the mode
            #     is DELETE the attribute should NOT be INCLUDED. Any attribute that was
            #     added by the developer using the stage_xxx() method would have hit the
            #     STAGED RULE above and would be INCLUDED.
            # A secondary PATTERN consideration is that attributes can be immediately
            #     deleted using the attribute.delete() method. While this isn't as
            #     efficient as deleting them all in one request, it's is a simpler
            #     development design pattern.

            # All non-matching nested object that did not match a rule above will NOT be INCLUDED.
            return False

        #
        # TI PARENT TYPES (Groups, Indicators, Victim, and Victims Assets)
        #

        # Nested Types:
        # * Associations (Groups, Indicators, Victim Assets)
        # * Attributes
        # * Security Labels
        # * Tags

        # Coverage:
        # * Downloaded from API
        # * Added on instantiation
        # * Added with stage_xxx() method

        if mode == 'append' and self._associated_type:
            # RULE: Nested Object w/ APPEND mode
            # Nested object on a parent CM type use the mode feature. When the mode
            #     is APPEND and not STAGED the object should NOT be INCLUDED.
            return True

        if mode == 'replace':
            # RULE: Nested Object w/ REPLACE mode
            # Nested object on a parent TI type use the mode feature. When the mode
            #     is REPLACE the object should be INCLUDED.
            return True

        # * security_label -> delete (support id or name only)
        # * tag -> delete (support id or name only)
        if (
            mode == 'delete'
            and (model._shared_type is True or self._associated_type is True)
            and (model.id is not None or model.name is not None)  # type: ignore
        ):
            # RULE: Nested Shared Object w/ DELETE mode (TAGS, SECURITY LABELS)
            # Nested shared object on a parent TI type use the mode feature. When the mode
            #     is DELETE the shard object should not be INCLUDED. Any object that was
            #     added by the developer would have hit the STAGED RULE above and would
            #     be INCLUDED.
            return True

        # * associated -> delete (support id only)
        # * attribute -> delete (support id only)
        # RULE: Nested Object w/ DELETE mode
        # Nested object on a parent TI type use the mode feature. When the mode
        #     is DELETE the object should not be INCLUDED. Any object that was
        #     added by the developer would have hit the STAGED RULE above and would
        #     be INCLUDED.

        # All non-matching nested object that did not match a rule above will NOT be INCLUDED.
        return False

    def _process_nested_data_array(self, method: str, mode: str | None, nested_object: Self):
        """Process the nested data object (e.g., GroupsModel.data).

        Nested Object Inclusion Rules:
        * If the method is not PUT.
        * The model doesn't have an "id" field.
          * Object was created using the "add_xxx" method on the parent object.
        * The model's "updated" field is True.
          * Object was modified after it was created. Since object pulled from the API
              are create using **kwargs they are not updated.
        """
        _data = []
        for model in nested_object.data:  # type: ignore
            if self._calculate_nested_inclusion(method, mode, model):
                data = model.gen_body(method, mode, nested=True)
                if data:
                    _data.append(data)

        return _data

    def _process_nested_data_object(self, method: str, mode: str | None, nested_object: Self):
        """Process the nested data object (e.g., GroupsModel.data).

        Nested Object Inclusion Rules:
        * If the method is not PUT.
        * The model doesn't have an "id" field.
          * Object was created using the "add_xxx" method on the parent object.
        * The model's "updated" field is True.
          * Object was modified after it was created. Since object pulled from the API
              are create using **kwargs they are not updated.
        """
        if self._calculate_nested_inclusion(method, mode, nested_object.data):  # type: ignore
            data = nested_object.data.gen_body(method, mode, nested=True)  # type: ignore
            if data:
                return data
        return None

    def _properties(self) -> dict[str, dict[str, str]]:
        """Return properties of the current model."""
        schema = self.schema(by_alias=False)
        if schema.get('properties') is not None:
            return schema.get('properties', {})
        return schema.get('definitions', {}).get(self.__class__.__name__, {}).get('properties', {})

    @staticmethod
    def gen_model_hash(json_: str) -> str:
        """Return the current dict hash."""
        # get hash of dict
        hash_ = hashlib.sha256()  # nosec
        encoded = json_.encode()
        hash_.update(encoded)
        return hash_.hexdigest()

    def gen_body(
        self,
        method: str,
        mode: str | None = None,
        exclude_none: bool = True,
        nested: bool = False,
    ) -> dict:
        """Return the generated body.

        The field included in the body depend on the HTTP Method and whether or not the object
        is nested. For example the ID should not be send on the parent object on a POST or PUT,
        but should be added for a PUT on a nested object.
        """
        _body = {}
        schema_properties = self._properties()
        for name, value in self:
            if exclude_none is True and value is None:
                continue

            # get the current field from the schema to us in validating method membership.
            if schema_properties.get(name) is None:
                # a field not being available does not indicate a failure, it could simple
                # be the incorrect field was passed to the object, which will be dropped.
                self._log.warning(
                    f'action=schema-check, type={self.__class__.__name__}, '
                    f'property={name}, result=not-found'
                )
                continue

            property_ = schema_properties.get(name, {})
            key = property_['title']
            if isinstance(value, BaseModel) and property_.get('read_only') is False:
                value: Self  # type: ignore
                # Handle nested model that should be included in the body (non-read-only).

                if hasattr(value, 'data') and isinstance(value.data, list):  # type: ignore
                    # Handle nested object types where the "data" field contains an array of model.
                    _data = self._process_nested_data_array(method, mode, value)  # type: ignore
                    if _data:
                        _body.setdefault(key, {})['data'] = _data

                        # value as a model can be ArtifactTypeModel, ArtifactModel, etc.
                        if value._mode_support:  # type: ignore
                            # Use the default mode defined in the model ("append") or the
                            # mode passed into this method as an override.
                            _body.setdefault(key, {})['mode'] = mode or value.mode  # type: ignore

                elif hasattr(value, 'data'):
                    # Handle "non-standard" condition for Assignee where the nested "data"
                    # field contains an object instead of an Array.
                    _data = self._process_nested_data_object(method, mode, value)  # type: ignore
                    if _data:
                        _body.setdefault(key, {})['data'] = _data

                        # Handle the extra "type" field that is only on Assignee objects.
                        if hasattr(value, 'type'):
                            _body.setdefault(key, {})['type'] = value.type  # type: ignore

                else:
                    # Handle nested object types where field contains an object.
                    # (e.g., CaseModel -> workflowTemplate field)
                    # if method == 'POST' or value.id is None or value.updated is True:
                    if self._calculate_nested_inclusion(method, mode, value):  # type: ignore
                        _data = value.gen_body(method, mode, nested=True)  # type: ignore
                        if _data:
                            _body[key] = _data

            elif self._calculate_field_inclusion(key, method, mode, nested, property_, value):
                # Handle non-nested fields and their values based on well defined rules.
                if value and isinstance(value, list) and isinstance(value[0], BaseModel):
                    value: list[Self]
                    _data = []
                    for model in value:  # type: ignore
                        if self._calculate_nested_inclusion(method, mode, model):
                            data = model.gen_body(method, mode, nested=True)
                            if data:
                                _data.append(data)
                    _body[key] = _data
                else:
                    _body[key] = value

        return _body

    def gen_body_json(
        self,
        method: str,
        mode: str | None = None,
        indent: int | None = None,
        sort_keys: bool = False,
    ) -> str:
        """Wrap gen_body method returning JSON instead of dict."""
        # ensure mode is set to lower case if provided on gen_body entry point
        if mode is not None:
            mode = mode.lower()

        body = self.gen_body(method, mode)
        return json.dumps(
            body,
            cls=CustomJSONEncoder,
            indent=indent,
            sort_keys=sort_keys,
        )

    @property
    def updated(self):
        """Return True if model values have changed, else False."""
        return self._dict_hash != self.gen_model_hash(self.json(sort_keys=True))
