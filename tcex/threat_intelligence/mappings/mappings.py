# -*- coding: utf-8 -*-
"""ThreatConnect TI Generic Mappings Object"""
# standard library
import json
from urllib.parse import unquote

# first-party
from tcex.utils import Utils

from ..tcex_ti_tc_request import TiTcRequest


class Mappings:
    """Common API calls for for Indicators/SecurityLabels/Groups and Victims"""

    def __init__(self, tcex, main_type, api_type, sub_type, api_entity, api_branch, owner):
        """Initialize Class Properties.

        Args:
            tcex:
            main_type:
            api_type:
            sub_type:
            api_entity:
        """
        self._tcex = tcex
        self._data = {}

        self._owner = owner
        self._type = main_type
        self._api_sub_type = sub_type
        self._api_type = api_type
        self._unique_id = None
        self._api_entity = api_entity
        self._api_branch = api_branch

        self._utils = Utils()
        self._tc_requests = TiTcRequest(self._tcex)

    @property
    def _excluded_properties(self):
        """
        Returns a list of properties to exclude when creating a dict of the children Classes.
        """
        return ['tcex', 'kwargs', 'api_endpoint']

    @property
    def as_entity(self):  # pragma: no cover
        """Return the object as an entity."""
        raise NotImplementedError('Child class must implement this method.')

    @property
    def as_dict(self):
        """
        Returns the dict representation of the case management object.
        """
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
        """
        Sets the Api Entity
        Args:
            api_branch:

        Returns:

        """
        self._api_branch = api_branch

    @api_entity.setter
    def api_entity(self, api_entity):
        """
        Sets the Api Entity
        Args:
            api_entity:

        Returns:

        """
        self._api_entity = api_entity

    @api_type.setter
    def api_type(self, api_type):
        """
        Sets the Api Type
        Args:
            api_type:

        Returns:

        """
        self._api_type = api_type

    @tc_requests.setter
    def tc_requests(self, tc_requests):
        """
        Sets the Tc Request Object
        Args:
            tc_requests:

        Returns:

        """
        self._tc_requests = tc_requests

    @api_sub_type.setter
    def api_sub_type(self, sub_type):
        """
        Sets the Api Sub Type
        Args:
            sub_type:

        Returns:

        """
        self._api_sub_type = sub_type

    @unique_id.setter
    def unique_id(self, unique_id):
        """
        Sets the Unique Id
        Args:
            unique_id:

        Returns:

        """
        self._unique_id = unique_id

    @property
    def data(self):
        """Return data."""
        return self._data

    @data.setter
    def data(self, data):
        """
        Sets the data
        Args:
            data:

        Returns:

        """
        self._data = data
        if not self.unique_id:
            self._set_unique_id(data)

    def set(self, **kwargs):
        """
        A generic way to update the attributes of a TC data object.
        Args:
            **kwargs:

        Returns:

        """
        for arg, value in kwargs.items():
            if hasattr(self, 'add_key_value'):
                self.add_key_value(arg, value)  # pylint: disable=no-member
            else:
                self._data[arg] = value

    def create(self):
        """
        Creates the Indicator/Group/Victim or Security Label given Owner

        Args:
        """
        if not self.can_create():
            self._tcex.handle_error(920, [self.type])

        response = self.tc_requests.create(self.api_type, self.api_branch, self._data, self.owner)

        if self.tc_requests.success(response):
            self._set_unique_id(response.json().get('data').get(self.api_entity))

        return response

    def delete(self):
        """
        Deletes the Indicator/Group/Victim or Security Label
        """
        if not self.can_delete():
            self._tcex.handle_error(915, [self.type])

        return self.tc_requests.delete(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def update(self):
        """
        Updates the Indicator/Group/Victim or Security Label
        """
        if not self.can_update():
            self._tcex.handle_error(905, [self.type])

        return self.tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, self._data, owner=self.owner
        )

    def single(self, filters=None, params=None):
        """
        Gets the Indicator/Group/Victim or Security Label
        Args:
            filters:
            params: parameters to pass in to get the object

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.single(
            self.api_type,
            self.api_branch,
            self.unique_id,
            filters=filters,
            owner=self.owner,
            params=params,
        )

    def many(self, filters=None, params=None):
        """
        Gets the Indicator/Group/Victim or Security Labels
        Args:
            filters:
            owner:
            params: parameters to pass in to get the objects

        Yields: A Indicator/Group/Victim json

        """
        yield from self.tc_requests.many(
            self.api_type,
            self.api_branch,
            self.api_entity,
            owner=self.owner,
            filters=filters,
            params=params,
        )

    def request(self, result_limit, result_start, filters=None, params=None):
        """
        Gets the Indicator/Group/Victim or Security Labels
        Args:
            filters:
            owner:
            result_limit:
            result_start:
            params: parameters to pass in to get the objects

        Returns:

        """
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
        """
         Gets the tags from a Indicator/Group/Victim/Security Labels
         Args:
             filters:
             owner:
             params: parameters to pass in to get the objects

         Yields: A tag json

         """

        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        yield from self.tc_requests.tags(
            self.api_type,
            self.api_branch,
            self.unique_id,
            owner=self.owner,
            filters=filters,
            params=params,
        )

    def tag(self, name, action='ADD', params=None):
        """
         Adds a tag to a Indicator/Group/Victim/Security Label
         Args:
             params:
             action:
             name: The name of the tag

         """
        if not name:
            self._tcex.handle_error(925, ['name', 'tag', 'name', 'name', name])

        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

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
        self._tcex.handle_error(925, ['action', 'tag', 'action', 'action', action])
        return None

    def add_tag(self, name):
        """
         Adds a tag to a Indicator/Group/Victim/Security Label
         Args:
             name: The name of the tag

         """
        return self.tag(name, action='ADD')

    def get_tag(self, name, params=None):
        """
         Gets a tag from a Indicator/Group/Victim/Security Label
         Args:
             name: The name of the tag
             params:
         """
        return self.tag(name, action='GET', params=params)

    def delete_tag(self, name):
        """
         Deletes a tag from a Indicator/Group/Victim/Security Label
         Args:
             name: The name of the tag
         """

        return self.tag(name, action='DELETE')

    def labels(self, filters=None, params=None):
        """
         Gets the security labels from a Indicator/Group/Victim

         Yields: A Security label

         """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        yield from self.tc_requests.labels(
            self.api_type,
            self.api_branch,
            self.unique_id,
            owner=self.owner,
            filters=filters,
            params=params,
        )

    def label(self, label, action='ADD', params=None):
        """
         Adds a Security Label to a Indicator/Group or Victim
         Args:
             params:
             label: The name of the Security Label
             action:

         """

        if params is None:
            params = {}

        if not label:
            self._tcex.handle_error(925, ['label', 'Security Label', 'label', 'label', label])

        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

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

        self._tcex.handle_error(925, ['action', 'label', 'action', 'action', action])
        return None

    def add_label(self, label):
        """
         Adds a label to a Indicator/Group/Victim
         Args:
             label: The name of the Security Label
         """
        return self.label(label, action='ADD')

    def get_label(self, label, params=None):
        """
         Gets a security label from a Indicator/Group/Victim
         Args:
             label: The name of the Security Label
             params:
         """
        return self.label(label, action='GET', params=params)

    def delete_label(self, label):
        """
         Deletes a security label from a Indicator/Group/Victim
         Args:
             label: The name of the Security Label
         """
        return self.label(label, action='DELETE')

    def indicator_associations(self, params=None):
        """
         Gets the indicator association from a Indicator/Group/Victim

         Yields: Indicator Association

         """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if params is None:
            params = {}

        yield from self.tc_requests.indicator_associations(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner, params=params
        )

    def group_associations(self, params=None):
        """
         Gets the group association from a Indicator/Group/Victim

         Yields: Group Association

         """
        if params is None:
            params = {}

        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        yield from self.tc_requests.group_associations(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner, params=params
        )

    def victim_asset_associations(self, params=None):
        """
         Gets the victim asset association from a Indicator/Group/Victim

         Yields: Victim Association json

         """
        if params is None:
            params = {}
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.victim_asset_associations(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner, params=params
        )

    def indicator_associations_types(
        self, indicator_type, api_entity=None, api_branch=None, params=None
    ):
        """
        Gets the indicator association from a Indicator/Group/Victim

        Args:
            indicator_type:
            api_entity:
            api_branch:
            params:

        Returns:

        """
        if params is None:
            params = {}
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        target = self._tcex.ti.indicator(indicator_type)
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
        """
        Gets the group association from a Indicator/Group/Victim

        Args:
            group_type:
            api_entity:
            api_branch:
            params:

        Returns:

        """
        if params is None:
            params = {}
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        target = self._tcex.ti.group(group_type)

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
        """
        Gets the victim association from a Indicator/Group/Victim

        Args:
            victim_asset_type:
            params:

        Returns:

        """
        if params is None:
            params = {}
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.victim_asset_associations(
            self.api_type,
            self.api_branch,
            self.unique_id,
            victim_asset_type,
            owner=self.owner,
            params=params,
        )

    def add_association(self, target, api_type=None, api_branch=None, unique_id=None):
        """
        Adds a association to a Indicator/Group/Victim

        Args:
            target:
            api_type:
            api_branch:
            unique_id:

        Returns:

        """
        api_type = api_type or target.api_type
        api_branch = api_branch or target.api_branch
        unique_id = unique_id or target.unique_id
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if not target.can_update():
            self._tcex.handle_error(910, [target.type])

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
        """
        Deletes a association from a Indicator/Group/Victim

        Args:
            target:
            api_type:
            api_branch:
            unique_id:

        Returns:

        """
        api_type = api_type or target.api_type
        api_branch = api_branch or target.api_branch
        unique_id = unique_id or target.unique_id
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if not target.can_update():
            self._tcex.handle_error(910, [target.type])

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
        """
        Gets the attributes from a Group/Indicator or Victim

        Yields: attribute json

        """
        if params is None:
            params = {}
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        yield from self.tc_requests.attributes(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner, params=params
        )

    def attribute(self, attribute_id, action='GET', params=None):
        """
        Gets the attribute from a Group/Indicator or Victim


        Args:
            action:
            params:
            attribute_id:

        Returns: attribute json

        """
        if params is None:
            params = {}
        action = action.upper()
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

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

        self._tcex.handle_error(925, ['action', 'attribute', 'action', 'action', action])
        return None

    def add_attribute(
        self, attribute_type, attribute_value, source=None, displayed=None, params=None
    ):
        """
        Adds a attribute to a Group/Indicator or Victim


        Args:
            source:
            displayed:
            params:
            attribute_type:
            attribute_value:

        Returns: attribute json

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

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
        """
        Adds a attribute to a Group/Indicator or Victim


        Args:
            source:
            displayed:
            params:
            attribute_type:
            attribute_value:

        Returns: attribute json

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

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
        """
        Deletes a attribute from a Group/Indicator or Victim


        Args:
            attribute_id:

        Returns: attribute json

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.delete_attribute(
            self.api_type, self.api_branch, self.unique_id, attribute_id, owner=self.owner
        )

    def attribute_labels(self, attribute_id, params=None):
        """
        Gets the security labels from a attribute

        Yields: Security label json

        """
        if params is None:
            params = {}
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        yield from self.tc_requests.attribute_labels(
            self.api_type,
            self.api_branch,
            self.unique_id,
            attribute_id,
            owner=self.owner,
            params=params,
        )

    def attribute_label(self, attribute_id, label, action='GET', params=None):
        """
        Gets a security labels from a attribute

        Args:
            attribute_id:
            label:
            action:
            params:

        Returns: Security label json
        """
        if params is None:
            params = {}
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

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

        self._tcex.handle_error(925, ['action', 'attribute_label', 'action', 'action', action])
        return None

    def add_attribute_label(self, attribute_id, label):
        """
        Adds a security labels to a attribute

        Args:
            attribute_id:
            label:

        Returns: A response json
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.add_attribute_label(
            self.api_type, self.api_branch, self.unique_id, attribute_id, label, owner=self.owner
        )

    def can_create(self):  # pylint: disable=no-self-use
        """ Determines if the object can be created. """
        return True

    def can_delete(self):
        """ Determines if the object can be deleted. """
        return self.unique_id is not None

    def can_update(self):
        """ Determines if the object can be updated. """
        return self.unique_id is not None

    @staticmethod
    def is_indicator():
        """ Determines if the object is a Indicator. """
        return False

    @staticmethod
    def is_group():
        """ Determines if the object is a Group. """
        return False

    @staticmethod
    def is_victim():
        """ Determines if the object is a Victim. """
        return False

    @staticmethod
    def is_tag():
        """ Determines if the object is a Tag. """
        return False

    @staticmethod
    def is_security_label():
        """ Determines if the object is a Security Label. """
        return False

    @staticmethod
    def is_task():
        """ Determines if the object is a Task. """
        return False

    @staticmethod
    def is_encoded(uri):
        """Determines if a uri is currently encoded"""
        uri = uri or ''

        return uri != unquote(uri)

    def fully_decode_uri(self, uri):
        """Decodes a url till it is no longer encoded."""
        saftey_valve = 0

        while self.is_encoded(uri):
            uri = unquote(uri)
            saftey_valve += 1
            if saftey_valve > 10:
                break

        return uri

    def _set_unique_id(self, json_response):
        """ Sets the Unique Id given a json """
        self.unique_id = json_response.get('id')

    def __str__(self):
        """Return string representation of object."""
        return json.dumps(self.data, indent=4)
