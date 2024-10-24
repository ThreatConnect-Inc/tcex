"""TcEx Framework Module"""

# standard library
import json
import logging
from functools import lru_cache
from typing import TYPE_CHECKING
from urllib.parse import unquote

# third-party
from requests import Response

# first-party
from tcex.api.tc.v2.threat_intelligence.tcex_ti_tc_request import TiTcRequest
from tcex.exit.error_code import TcExErrorCode
from tcex.logger.trace_logger import TraceLogger
from tcex.util import Util

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import (
        ThreatIntelligence,  # CIRCULAR-IMPORT
    )


# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class Mapping:
    """Common API calls for for Indicators/SecurityLabels/Groups and Victims"""

    def __init__(
        self,
        ti: 'ThreatIntelligence',
        main_type,
        api_type,
        sub_type,
        api_entity,
        api_branch,
        owner,
    ):
        """Initialize instance properties"""
        self._api_branch = api_branch
        self._api_entity = api_entity
        self._api_sub_type = sub_type
        self._api_type = api_type
        self._owner = owner
        self._session = ti.session_tc
        self.ti = ti
        self._type = main_type

        # properties
        self._data = {}
        self.log = _logger
        self.util = Util()
        self._tc_requests = TiTcRequest(ti.session_tc)
        self._unique_id = None

    @property
    @lru_cache
    def _error_codes(self) -> TcExErrorCode:
        """Return TcEx error codes."""
        return TcExErrorCode()

    @property
    def _excluded_properties(self):
        """Return a list of properties to exclude when creating the child Class."""
        return ['tcex', 'kwargs', 'api_endpoint']

    def _handle_error(
        self, code: int, message_values: list | None = None, raise_error: bool = True
    ):
        """Raise RuntimeError

        Args:
            code: The error code from API or SDK.
            message_values: The error message from API or SDK.
            raise_error: Raise a Runtime error. Defaults to True.

        Raises:
            RuntimeError: Raised a defined error.
        """
        try:
            if message_values is None:
                message_values = []
            message = self._error_codes.message(code).format(*message_values)
            self.log.error(f'Error code: {code}, {message}')
        except AttributeError:
            self.log.error(f'Incorrect error code provided ({code}).')
            raise RuntimeError(100, 'Generic Failure, see logs for more details.')
        except IndexError:
            self.log.error(
                f'Incorrect message values provided for error code {code} ({message_values}).'
            )
            raise RuntimeError(100, 'Generic Failure, see logs for more details.')
        if raise_error:
            raise RuntimeError(code, message)

    @property
    def as_entity(self):  # pragma: no cover
        """Return the object as an entity."""
        raise NotImplementedError('Child class must implement this method.')

    @property
    def as_dict(self):
        """Return the dict representation of the case management object."""
        properties = vars(self)
        as_dict = {}
        for key, value in properties.items():
            key = key.lstrip('_')
            if key in self._excluded_properties:
                continue
            try:
                value = value.as_dict
            except AttributeError:
                pass
            if value is None:
                continue
            as_dict[key] = value
        if not as_dict:
            return None
        return as_dict

    @property
    def type(self):
        """Return main type."""
        return self._type

    @property
    def api_sub_type(self):
        """Return sub type."""
        return self._api_sub_type

    @property
    def unique_id(self):
        """Return unique id."""
        return self._unique_id

    @property
    def tc_requests(self):
        """Return tc request object."""
        return self._tc_requests

    @property
    def api_type(self):
        """Return api type."""
        return self._api_type

    @property
    def api_branch(self):
        """Return api entity."""
        return self._api_branch

    @property
    def api_entity(self):
        """Return api entity."""
        return self._api_entity

    @property
    def owner(self):
        """Return unique id."""
        return self._owner

    @owner.setter
    def owner(self, owner):
        self._owner = owner

    @api_branch.setter
    def api_branch(self, api_branch):
        """Set the Api Entity."""
        self._api_branch = api_branch

    @api_entity.setter
    def api_entity(self, api_entity):
        """Set the Api Entity."""
        self._api_entity = api_entity

    @api_type.setter
    def api_type(self, api_type):
        """Set the Api Type."""
        self._api_type = api_type

    @tc_requests.setter
    def tc_requests(self, tc_requests):
        """Set the Tc Request Object."""
        self._tc_requests = tc_requests

    @api_sub_type.setter
    def api_sub_type(self, sub_type):
        """Set the Api Sub Type."""
        self._api_sub_type = sub_type

    @unique_id.setter
    def unique_id(self, unique_id):
        """Set the Unique Id."""
        self._unique_id = unique_id

    @property
    def data(self):
        """Return data."""
        return self._data

    @data.setter
    def data(self, data):
        """Set the data."""
        self._data = data
        if not self.unique_id:
            self._set_unique_id(data)

    def set(self, **kwargs):
        """Provide a generic way to update the attributes of a TC data object."""
        for arg, value in kwargs.items():
            if hasattr(self, 'add_key_value'):
                self.add_key_value(arg, value)  # type: ignore
            else:
                self._data[arg] = value

    def create(self):
        """Create the Indicator/Group/Victim or Security Label given Owner."""
        if not self.can_create():
            self._handle_error(920, [self.type])

        response = self.tc_requests.create(self.api_type, self.api_branch, self._data, self.owner)

        if self.tc_requests.success(response):
            self._set_unique_id(response.json().get('data').get(self.api_entity))

        return response

    def delete(self):
        """Delete the Indicator/Group/Victim or Security Label."""
        if not self.can_delete():
            self._handle_error(915, [self.type])

        return self.tc_requests.delete(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def update(self):
        """Update the Indicator/Group/Victim or Security Label."""
        if not self.can_update():
            self._handle_error(905, [self.type])

        return self.tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, self._data, owner=self.owner
        )

    def single(self, filters=None, params=None):
        """Get the Indicator/Group/Victim or Security Label."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        return self.tc_requests.single(
            self.api_type,
            self.api_branch,
            self.unique_id,
            filters=filters,
            owner=self.owner,
            params=params,
        )

    def many(self, filters=None, params=None):
        """Get the Indicator/Group/Victim or Security Labels."""
        yield from self.tc_requests.many(
            self.api_type,
            self.api_branch,
            self.api_entity,
            owner=self.owner,
            filters=filters,
            params=params,
        )

    def request(self, result_limit, result_start, filters=None, params=None):
        """Get the Indicator/Group/Victim or Security Labels."""
        return self.tc_requests.request(
            self.api_type,
            self.api_branch,
            result_limit,
            result_start,
            owner=self.owner,
            filters=filters,
            params=params,
        )

    def tags(self, filters=None, params=None):
        """Get the tags from a Indicator/Group/Victim/Security Labels."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        yield from self.tc_requests.tags(
            self.api_type,
            self.api_branch,
            self.unique_id,
            owner=self.owner,
            filters=filters,
            params=params,
        )

    def tag(self, name, action='ADD', params=None):
        """Add a tag to a Indicator/Group/Victim/Security Label."""
        if not name:
            self._handle_error(925, ['name', 'tag', 'name', 'name', name])

        if not self.can_update():
            self._handle_error(910, [self.type])

        if action in ['GET', 'ADD', 'DELETE']:
            return self.tc_requests.tag(
                self.api_type,
                self.api_branch,
                self.unique_id,
                name,
                action=action,
                owner=self.owner,
                params=params,
            )
        self._handle_error(925, ['action', 'tag', 'action', 'action', action])
        return None

    def add_tag(self, name):
        """Add a tag to a Indicator/Group/Victim/Security Label."""
        return self.tag(name, action='ADD')

    def get_tag(self, name, params=None):
        """Get a tag from a Indicator/Group/Victim/Security Label."""
        return self.tag(name, action='GET', params=params)

    def delete_tag(self, name):
        """Delete a tag from a Indicator/Group/Victim/Security Label."""

        return self.tag(name, action='DELETE')

    def labels(self, filters=None, params=None):
        """Get the security labels from a Indicator/Group/Victim."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        yield from self.tc_requests.labels(
            self.api_type,
            self.api_branch,
            self.unique_id,
            owner=self.owner,
            filters=filters,
            params=params,
        )

    def label(self, label, action='ADD', params=None) -> Response | None:
        """Add a Security Label to a Indicator/Group or Victim."""

        if params is None:
            params = {}

        if not label:
            self._handle_error(925, ['label', 'Security Label', 'label', 'label', label])

        if not self.can_update():
            self._handle_error(910, [self.type])

        if action == 'GET':
            return self.tc_requests.get_label(
                self.api_type,
                self.api_branch,
                self.unique_id,
                label,
                owner=self.owner,
                params=params,
            )

        if action == 'ADD':
            return self.tc_requests.add_label(
                self.api_type, self.api_branch, self.unique_id, label, owner=self.owner
            )

        if action == 'DELETE':
            return self.tc_requests.delete_label(
                self.api_type, self.api_branch, self.unique_id, label, owner=self.owner
            )

        self._handle_error(925, ['action', 'label', 'action', 'action', action])
        return None

    def add_label(self, label):
        """Add a label to a Indicator/Group/Victim."""
        return self.label(label, action='ADD')

    def get_label(self, label, params=None):
        """Get a security label from a Indicator/Group/Victim."""
        return self.label(label, action='GET', params=params)

    def delete_label(self, label):
        """Delete a security label from a Indicator/Group/Victim."""
        return self.label(label, action='DELETE')

    def indicator_associations(self, params=None):
        """Get the indicator association from a Indicator/Group/Victim."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        if params is None:
            params = {}

        yield from self.tc_requests.indicator_associations(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner, params=params
        )

    def group_associations(self, params=None):
        """Get the group association from a Indicator/Group/Victim."""
        if params is None:
            params = {}

        if not self.can_update():
            self._handle_error(910, [self.type])

        yield from self.tc_requests.group_associations(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner, params=params
        )

    def victim_asset_associations(self, params=None):
        """Get the victim asset association from a Indicator/Group/Victim."""
        if params is None:
            params = {}
        if not self.can_update():
            self._handle_error(910, [self.type])

        return self.tc_requests.victim_asset_associations(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner, params=params
        )

    def indicator_associations_types(
        self, indicator_type, api_entity=None, api_branch=None, params=None
    ):
        """Get the indicator association from a Indicator/Group/Victim."""
        if params is None:
            params = {}
        if not self.can_update():
            self._handle_error(910, [self.type])

        target = self.ti.indicator(indicator_type)
        yield from self.tc_requests.indicator_associations_types(
            self.api_type,
            self.api_branch,
            self.unique_id,
            target,
            api_entity=api_entity,
            api_branch=api_branch,
            owner=self.owner,
            params=params,
        )

    def group_associations_types(self, group_type, api_entity=None, api_branch=None, params=None):
        """Get the group association from a Indicator/Group/Victim."""
        if params is None:
            params = {}
        if not self.can_update():
            self._handle_error(910, [self.type])

        target = self.ti.group(group_type)
        yield from self.tc_requests.group_associations_types(
            self.api_type,
            self.api_branch,
            self.unique_id,
            target,
            api_entity=api_entity,
            api_branch=api_branch,
            owner=self.owner,
            params=params,
        )

    def victim_asset_associations_type(self, victim_asset_type, params=None):
        """Get the victim association from a Indicator/Group/Victim."""
        if params is None:
            params = {}
        if not self.can_update():
            self._handle_error(910, [self.type])

        return self.tc_requests.victim_asset_associations(
            self.api_type,
            self.api_branch,
            self.unique_id,
            victim_asset_type,
            owner=self.owner,
            params=params,
        )

    def add_association(self, target, api_type=None, api_branch=None, unique_id=None):
        """Add a association to a Indicator/Group/Victim."""
        api_type = api_type or target.api_type
        api_branch = api_branch or target.api_branch
        unique_id = unique_id or target.unique_id
        if not self.can_update():
            self._handle_error(910, [self.type])

        if not target.can_update():
            self._handle_error(910, [target.type])

        return self.tc_requests.add_association(
            self.api_type,
            self.api_branch,
            self.unique_id,
            api_type,
            api_branch,
            unique_id,
            owner=self.owner,
        )

    def delete_association(self, target, api_type=None, api_branch=None, unique_id=None):
        """Delete a association from a Indicator/Group/Victim."""
        api_type = api_type or target.api_type
        api_branch = api_branch or target.api_branch
        unique_id = unique_id or target.unique_id
        if not self.can_update():
            self._handle_error(910, [self.type])

        if not target.can_update():
            self._handle_error(910, [target.type])

        return self.tc_requests.delete_association(
            self.api_type,
            self.api_branch,
            self.unique_id,
            api_type,
            api_branch,
            unique_id,
            owner=self.owner,
        )

    def attributes(self, params=None):
        """Get the attributes from a Group/Indicator or Victim."""
        if params is None:
            params = {}
        if not self.can_update():
            self._handle_error(910, [self.type])

        yield from self.tc_requests.attributes(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner, params=params
        )

    def attribute(self, attribute_id, action='GET', params=None):
        """Get the attribute from a Group/Indicator or Victim."""
        if params is None:
            params = {}
        action = action.upper()
        if not self.can_update():
            self._handle_error(910, [self.type])

        if action == 'GET':
            return self.tc_requests.get_attribute(
                self.api_type,
                self.api_branch,
                self.unique_id,
                attribute_id,
                owner=self.owner,
                params=params,
            )

        if action == 'DELETE':
            return self.tc_requests.delete_attribute(
                self.api_type, self.api_branch, self.unique_id, attribute_id, owner=self.owner
            )

        self._handle_error(925, ['action', 'attribute', 'action', 'action', action])
        return None

    def add_attribute(
        self, attribute_type, attribute_value, source=None, displayed=None, params=None
    ):
        """Add a attribute to a Group/Indicator or Victim."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        if params is None:
            params = {}

        return self.tc_requests.add_attribute(
            self.api_type,
            self.api_branch,
            self.unique_id,
            attribute_type,
            attribute_value,
            source=source,
            displayed=displayed,
            owner=self.owner,
            params=params,
        )

    def update_attribute(
        self, attribute_value, attribute_id, source=None, displayed=None, params=None
    ):
        """Add a attribute to a Group/Indicator or Victim."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        if params is None:
            params = {}

        return self.tc_requests.update_attribute(
            self.api_type,
            self.api_branch,
            self.unique_id,
            attribute_value,
            attribute_id,
            source=source,
            displayed=displayed,
            owner=self.owner,
            params=params,
        )

    def delete_attribute(self, attribute_id):
        """Delete a attribute from a Group/Indicator or Victim."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        return self.tc_requests.delete_attribute(
            self.api_type, self.api_branch, self.unique_id, attribute_id, owner=self.owner
        )

    def attribute_labels(self, attribute_id, params=None):
        """Get the security labels from a attribute."""
        if params is None:
            params = {}
        if not self.can_update():
            self._handle_error(910, [self.type])

        yield from self.tc_requests.attribute_labels(
            self.api_type,
            self.api_branch,
            self.unique_id,
            attribute_id,
            owner=self.owner,
            params=params,
        )

    def attribute_label(self, attribute_id, label, action='GET', params=None):
        """Get a security labels from a attribute."""
        if params is None:
            params = {}
        if not self.can_update():
            self._handle_error(910, [self.type])

        if action == 'GET':
            return self.tc_requests.get_attribute_label(
                self.api_type,
                self.api_branch,
                self.unique_id,
                attribute_id,
                label,
                owner=self.owner,
                params=params,
            )
        if action == 'DELETE':
            return self.tc_requests.delete_attribute_label(
                self.api_type,
                self.api_branch,
                self.unique_id,
                attribute_id,
                label,
                owner=self.owner,
            )

        self._handle_error(925, ['action', 'attribute_label', 'action', 'action', action])
        return None

    def add_attribute_label(self, attribute_id, label):
        """Add a security labels to a attribute."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        return self.tc_requests.add_attribute_label(
            self.api_type, self.api_branch, self.unique_id, attribute_id, label, owner=self.owner
        )

    def can_create(self):
        """Determine if the object can be created."""
        return True

    def can_delete(self):
        """Determine if the object can be deleted."""
        return self.unique_id is not None

    def can_update(self):
        """Determine if the object can be updated."""
        return self.unique_id is not None

    @staticmethod
    def is_indicator():
        """Determine if the object is a Indicator."""
        return False

    @staticmethod
    def is_group():
        """Determine if the object is a Group."""
        return False

    @staticmethod
    def is_victim():
        """Determine if the object is a Victim."""
        return False

    @staticmethod
    def is_tag():
        """Determine if the object is a Tag."""
        return False

    @staticmethod
    def is_security_label():
        """Determine if the object is a Security Label."""
        return False

    @staticmethod
    def is_task():
        """Determine if the object is a Task."""
        return False

    @staticmethod
    def is_encoded(uri):
        """Determine if a uri is currently encoded"""
        uri = uri or ''

        return uri != unquote(uri)

    def fully_decode_uri(self, uri):
        """Decode a url till it is no longer encoded."""
        safety_valve = 0

        while self.is_encoded(uri):
            uri = unquote(uri)
            safety_valve += 1
            if safety_valve > 10:
                break

        return uri

    def _set_unique_id(self, json_response):
        """Set the Unique Id given a json"""
        self.unique_id = json_response.get('id')

    def __str__(self):
        """Return string representation of object."""
        return json.dumps(self.data, indent=4)
