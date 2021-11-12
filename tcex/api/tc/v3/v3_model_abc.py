"""ThreatConnect API V3 Base Model."""
# standard library
import hashlib
import logging
from abc import ABC

# third-party
from pydantic import BaseModel, PrivateAttr

# get tcex logger
logger = logging.getLogger('tcex')


class V3ModelABC(BaseModel, ABC):
    """V3 Base Model"""

    _dict_hash: str = PrivateAttr()
    _log = logger

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(**kwargs)

        # store initial dict hash of model
        self._dict_hash = self.gen_model_hash(self.json(sort_keys=True))

    def _properties(self):
        """Return properties of the current model."""
        schema = self.schema(by_alias=False)
        if schema.get('properties') is not None:
            return schema.get('properties')
        return schema.get('definitions').get(self.__class__.__name__).get('properties')

    def gen_body(self, method: str, exclude_none=True) -> dict:
        """Return the generated body."""
        _body = {}
        schema_properties = self._properties()
        for name, value in self:
            if exclude_none is True and value is None:
                continue

            # schema check
            property_ = schema_properties.get(name)
            if property_ is None:
                self._log.warning(f'action=schema-check, property={name}, result=not-found')
                continue

            key = property_.get('title')
            if isinstance(value, BaseModel):
                if hasattr(value, 'data') and isinstance(value.data, list):
                    # this is a nested collection (e.g., GroupsModel)
                    _data = []
                    for model in value.data:
                        # on PUT method:
                        # * don't put values with and id
                        # OR
                        # * don't put values that have not been updated
                        if method == 'PUT' and (model.id is not None or model.updated is True):
                            continue

                        _method = str(method)
                        if not model.id and _method == 'PUT':
                            _method = 'POST'
                        data = model.gen_body(_method)
                        if data:
                            _data.append(data)
                    if _data:
                        _body[key] = {}
                        _body[key]['data'] = _data
                else:
                    # handle nested values
                    if method != 'PUT' or value.updated is True:
                        data = value.gen_body(method)
                        if data:
                            _body[key] = data
            elif method in property_.get('methods', []) and value:
                _body[key] = value
        return _body

    @staticmethod
    def gen_model_hash(json_: str) -> str:
        """Return the current dict hash."""
        # get hash of dict
        hash_ = hashlib.md5()  # nosec
        encoded = json_.encode()
        hash_.update(encoded)
        return hash_.hexdigest()

    @property
    def updated(self):
        """Return True if model values have changed, else False."""
        return self._dict_hash != self.gen_model_hash(self.json(sort_keys=True))
