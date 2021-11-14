"""ThreatConnect API V3 Base Model."""
# standard library
import hashlib
import json
import logging
from abc import ABC
import datetime
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
    _method_override = PrivateAttr(False)
    _log = logger

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(**kwargs)

        # store initial dict hash of model
        self._dict_hash = self.gen_model_hash(self.json(sort_keys=True))

    @staticmethod
    def _calculate_method(method: str, model: 'BaseModel', nested: bool) -> str:
        """Return the appropriate HTTP method value.

        The method value control the behavior of included field for a DELETE, GET, POST or PUT.
        """
        if not model.id and method == 'PUT':
            method = 'POST'
        elif model._method_override and method.upper() not in ['GET', 'DELETE']:
            method = 'PUT'
        return method

    @staticmethod
    def _calculate_field_inclusion(
        field: str, method: str, mode: str, nested: bool, property_: dict, value: Any
    ) -> str:
        """Return True if the field is calculated to be included."""
        # MODE DELETE Rule - The "id" should be the only field included when delete mode
        #     is enabled.
        if nested is True and field != 'id' and mode and mode == 'delete':
            return False

        # ID Rule - The "id" should not be included for ANY method on parent object,
        #     but for nested objects the "id" field should be included when available.
        if field == 'id' and nested is True and value:
            return True

        # if method == 'POST' and nested is True:
        #     pass

        # if method == 'PUT' and nested is True:
        #     pass

        # METHOD Rule - If the current method is in the property "methods" list the
        #     field should be included when available.
        if method in property_.get('methods', []) and value:
            return True

        # DEFAULT Rule - Fields should not be included unless the match a previous rule.
        return False

    def _gen_body(
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
                self._log.warning(f'action=schema-check, property={name}, result=not-found')
                continue

            # TODO: [med] talk to @bpurdy about switching to alias field
            key = property_.get('title')
            if isinstance(value, BaseModel) and property_.get('read_only') is False:
                # For the threatconnect API the data structure for an object should have
                # a data array with nested object or be an object.
                # @bsummer - Updated this because not all nested objects are a array (assignee
                # for example)
                if hasattr(value, 'data'):# and isinstance(value.data, list):
                    _data = self._process_nested_data_object(method, mode, nested, value)
                    if _data:
                        _body.setdefault(key, {})['data'] = _data
                        # This is for Assignee since it has more than just a data field
                        if hasattr(value, 'type'):
                            _body.setdefault(key, {})['type'] = value.type
                        if mode or hasattr(value, 'mode'):
                            _body.setdefault(key, {})['mode'] = mode or value.mode
                        # _body[key] = {}
                        # _body[key]['data'] = _data
                else:
                    if method == 'POST' or value.id is None or value.updated is True:
                        _data = value._gen_body(method, mode, nested=True)
                        if _data:
                            _body[key] = _data
            elif self._calculate_field_inclusion(key, method, mode, nested, property_, value):
                _body[key] = value
        return _body

    def _process_nested_data_object( self,
        method: str, mode: str, nested: bool, nested_object: 'BaseModel'
    ):
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
        # @bsummers - Updating this to support both data dicts and arrays
        if nested_object.data is None:
            return _data
        nested_data = nested_object.data.copy()
        if not isinstance(nested_object.data, list):
            nested_data = [nested_data]
        for model in nested_data:
            # @bpurdy - Never include nested object for get or delete? - Ben 'Yeap'
            if method in ['DELETE', 'GET']:
                continue

            if method == 'POST' or model.id is None or model.updated is True or mode == 'delete':
                method = self._calculate_method(method, model, nested)
                data = model._gen_body(method, mode, nested=True)
                if data:
                    if isinstance(nested_object.data, list):
                        _data.append(data)
                    else:
                        _data = data
        return _data

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
        indent: Optional[int] = 0,
        sort_keys: Optional[bool] = False,
    ):
        """Return the post body."""
        # ensure mode is set to lower case if provided on gen_body entry point
        if mode is not None:
            mode = mode.lower()

        return json.dumps(
            self._gen_body(method=method, mode=mode),
            cls=CustomJSONEncoder,
            indent=indent,
            sort_keys=sort_keys,
        )

    @property
    def updated(self):
        """Return True if model values have changed, else False."""
        return self._dict_hash != self.gen_model_hash(self.json(sort_keys=True))
