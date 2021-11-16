"""ThreatConnect API V3 Base Model."""
# standard library
import datetime
import hashlib
import json
import logging
from abc import ABC
from json import JSONEncoder
from typing import Any, Optional

# third-party
from pydantic import BaseModel, PrivateAttr

# get tcex logger
logger = logging.getLogger('tcex')


class CustomJSONEncoder(JSONEncoder):
    """Format object in JSON data."""

    def default(self, o: Any) -> str:
        """Format object"""
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return o


class V3ModelABC(BaseModel, ABC):
    """V3 Base Model"""

    _dict_hash: str = PrivateAttr()
    _log = logger

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(**kwargs)

        # store initial dict hash of model
        self._dict_hash = self.gen_model_hash(self.json(sort_keys=True))

    def _calculate_field_inclusion(
        self, field: str, method: str, mode: str, nested: bool, property_: dict, value: Any
    ) -> str:
        """Return True if the field is calculated to be included."""
        # MODE DELETE RULE: The "id" should be the only field included when delete mode
        #     is enabled.
        if mode == 'delete' and nested is True and field not in ['id', 'name']:
            return False

        # ID RULE: The "id" should not be included for ANY method on parent object,
        #     but for nested objects the "id" field should be included when available.
        #     PLAT-4074 - updating nested object using "replace"
        if field == 'id' and nested is True and value:
            return True

        # CM NESTED RULE: For nested CM objects the body should use the valid POST fields
        #    instead of the PUT fields. This handles including artifact type and other
        #    fields that are needed on the nested object.
        # if method == 'PUT' and nested is True and self._method_override is True:
        #     method = 'POST'

        # NESTED RULE: For nested objects the body should use the valid POST fields
        #    instead of the PUT fields if not id is available. This handles including
        #    artifact type, attributes and other fields that are needed on the nested object.
        if method == 'PUT' and nested is True and not self.id:  # this is a new nested deal
            method = 'POST'

        # SHARED TYPE RULE: For nested "shared types" objects the body should use the valid
        #    PUT methods instead of the POST fields.  This handles not sending owner field
        #    for tag.
        if method == 'POST' and nested is True and self._shared_type is True:
            method = 'PUT'

        # METHOD RULE: If the current method is in the property "methods" list the
        #     field should be included when available.
        if method in property_.get('methods', []) and value:
            return True

        # DEFAULT RULE -> Fields should not be included unless the match a previous rule.
        return False

    @staticmethod
    def _calculate_nested_inclusion(method: str, mode: str, model: 'BaseModel') -> str:
        """Return True if the field is calculated to be included."""
        # EMPTY RULE: If there is not value in the model it should not be included.
        if not model:
            return False

        # METHOD RULE: When HTTP method is DELETE or GET no nested objects should be included.
        if method in ['DELETE', 'GET']:
            return False

        # INCLUDE RULE:
        # * HTTP Post Method -> Sub types should always be included.
        # * ID is None       -> Indicates that and add_xxx method was used to add the nested model.
        # * Model Updated    -> Indicates the model has changed.
        # * Mode [delete]    -> Include for mode delete so that all nested items are deleted appropriately.
        # * Mode [replace]   -> Include for mode replace or nested models would be removed by core.
        if (
            method == 'POST'
            or model.id is None
            or model.updated is True
            or mode in ['delete', 'replace']
        ):
            return True

        # DEFAULT RULE: Fields should not be included unless the match a previous rule.
        return False

    def _process_nested_data_array(self, method: str, mode: str, nested_object: 'BaseModel'):
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
        for model in nested_object.data:
            if self._calculate_nested_inclusion(method, mode, model):
                data = model.gen_body(method, mode, nested=True)
                if data:
                    _data.append(data)

        return _data

    def _process_nested_data_object(self, method: str, mode: str, nested_object: 'BaseModel'):
        """Process the nested data object (e.g., GroupsModel.data).

        Nested Object Inclusion Rules:
        * If the method is not PUT.
        * The model doesn't have an "id" field.
          * Object was created using the "add_xxx" method on the parent object.
        * The model's "updated" field is True.
          * Object was modified after it was created. Since object pulled from the API
              are create using **kwargs they are not updated.
        """
        if self._calculate_nested_inclusion(method, mode, nested_object.data):
            data = nested_object.data.gen_body(method, mode, nested=True)
            if data:
                return data
        return None

    def _properties(self):
        """Return properties of the current model."""
        schema = self.schema(by_alias=False)
        if schema.get('properties') is not None:
            return schema.get('properties')
        return schema.get('definitions').get(self.__class__.__name__).get('properties')

    @staticmethod
    def gen_model_hash(json_: str) -> str:
        """Return the current dict hash."""
        # get hash of dict
        hash_ = hashlib.md5()  # nosec
        encoded = json_.encode()
        hash_.update(encoded)
        return hash_.hexdigest()

    def gen_body(
        self,
        method: str,
        mode: Optional[str] = None,
        exclude_none: Optional[bool] = True,
        nested: Optional[bool] = False,
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
            property_ = schema_properties.get(name)
            if property_ is None:
                # a field not being available does not indicate a failure, it could simple
                # be the incorrect field was passed to the object, which will be dropped.
                self._log.warning(
                    f'action=schema-check, type={self.__class__.__name__}, '
                    f'property={name}, result=not-found'
                )
                continue

            key = property_.get('title')
            if isinstance(value, BaseModel) and property_.get('read_only') is False:
                # Handle nested models that should be included in the body (non-read-only).

                if hasattr(value, 'data') and isinstance(value.data, list):
                    # Handle nested object types where the "data" field contains an array of models.
                    _data = self._process_nested_data_array(method, mode, value)
                    if _data:
                        _body.setdefault(key, {})['data'] = _data

                        if value._mode_support:
                            # Use the default mode defined in the model ("append") or the mode passed
                            # into this method as an override.
                            _body.setdefault(key, {})['mode'] = mode or value.mode

                elif hasattr(value, 'data'):
                    # Handle "non-standard" condition for Assignee where the nested "data"
                    # field contains an object instead of an Array.
                    _data = self._process_nested_data_object(method, mode, value)
                    if _data:
                        _body.setdefault(key, {})['data'] = _data

                        # Handle the extra "type" field that is only on Assignee objects.
                        if hasattr(value, 'type'):
                            _body.setdefault(key, {})['type'] = value.type

                else:
                    # Handle nested object types where field contains an object.
                    # (e.g., CaseModel -> workflowTemplate field)
                    # if method == 'POST' or value.id is None or value.updated is True:
                    if self._calculate_nested_inclusion(method, mode, value):
                        _data = value.gen_body(method, mode, nested=True)
                        if _data:
                            _body[key] = _data

            elif self._calculate_field_inclusion(key, method, mode, nested, property_, value):
                # Handle non-nested fields and their values based on well defined rules.
                _body[key] = value

        return _body

    def gen_body_json(
        self,
        method: str,
        mode: Optional[str] = None,
        indent: Optional[int] = None,
        sort_keys: Optional[bool] = False,
    ) -> str:
        """Wrap gen_body method returning JSON instead of dict."""
        # ensure mode is set to lower case if provided on gen_body entry point
        if mode is not None:
            mode = mode.lower()

        return json.dumps(
            self.gen_body(method=method, mode=mode),
            cls=CustomJSONEncoder,
            indent=indent,
            sort_keys=sort_keys,
        )

    @property
    def updated(self):
        """Return True if model values have changed, else False."""
        return self._dict_hash != self.gen_model_hash(self.json(sort_keys=True))
