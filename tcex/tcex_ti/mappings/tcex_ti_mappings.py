from tcex.tcex_ti.tcex_ti_tc_request import TiTcRequest
import json
from tcex.tcex_utils import TcExUtils


class TIMappings(object):
    def __init__(self, tcex, type, api_type, sub_type, api_entity, **kwargs):
        """Initialize Class Properties.

        Args:
            group_type (str): The ThreatConnect define Group type.
            name (str): The name for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        self._tcex = tcex
        # self._data = {'xid': kwargs.get('xid', str(uuid.uuid4()))}
        self._data = {}

        self._type = type
        self._api_sub_type = sub_type
        self._api_type = api_type
        self._unique_id = None
        self._api_entity = api_entity

        self._utils = TcExUtils()
        self._tc_requests = TiTcRequest(self._tcex)

    @property
    def type(self):
        """Return Group type."""
        return self._type

    @property
    def api_sub_type(self):
        """Return Group type."""
        return self._api_sub_type

    @property
    def xid(self):
        """Return Group xid."""
        return self._data.get('xid')

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def tc_requests(self):
        return self._tc_requests

    @property
    def api_type(self):
        """Return Group type."""
        return self._api_type

    @property
    def api_entity(self):
        """Return Group type."""
        return self._api_entity

    @api_entity.setter
    def api_entity(self, api_entity):
        self._api_entity = api_entity

    @api_type.setter
    def api_type(self, api_type):
        self._api_type = api_type

    @tc_requests.setter
    def tc_requests(self, tc_requests):
        self._tc_requests = tc_requests

    @api_sub_type.setter
    def api_sub_type(self, sub_type):
        """Return Group type."""
        self._api_sub_type = sub_type

    @unique_id.setter
    def unique_id(self, unique_id):
        self._unique_id = unique_id

    @property
    def data(self):
        """Return Group xid."""
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def create(self, owner):
        if not self.can_create():
            return

        response = self.tc_requests.create(self.api_type, self.api_sub_type, self._data, owner)

        if self.tc_requests.success(response):
            self._set_unique_id(response.json().get('data').get(self.api_entity))

        return response

    def delete(self):
        if not self.can_delete():
            return

        return self.tc_requests.delete(self.api_type, self.api_sub_type, self.unique_id)

    def update(self):
        if not self.can_update():
            return

        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, self._data)

    def single(self, **kwargs):
        return self.tc_requests.single(self.api_type, self.api_sub_type, self.unique_id, **kwargs)

    def many(self, **kwargs):
        yield from self.tc_requests.many(self.api_type, self.api_sub_type, self.api_entity, **kwargs)

    def request(self, result_limit, result_offset, **kwargs):
        return self.tc_requests.request(self.api_type, self.api_sub_type, result_limit, result_offset, **kwargs)

    def tags(self):
        if not self.can_update():
            return

        return self.tc_requests.tags(self.api_type, self.api_sub_type, self.unique_id)

    def tag(self, name, action='ADD'):
        if not self.can_update():
            return

        if action == 'GET':
            return self.tc_requests.tag(self.api_type, self.api_sub_type, self.unique_id, name, action=action)

        if action == 'ADD':
            return self.tc_requests.tag(self.api_type, self.api_sub_type, self.unique_id, name, action=action)

        if action == 'DELETE':
            return self.tc_requests.tag(self.api_type, self.api_sub_type, self.unique_id, name, action=action)

    def add_tag(self, name):
        if not self.can_update():
            return

        return self.tc_requests.add_tag(self.api_type, self.api_sub_type, self.unique_id, name)

    def get_tag(self, name):
        if not self.can_update():
            return

        return self.tc_requests.tag(self.api_type, self.api_sub_type, self.unique_id, name)

    def delete_tag(self, name):
        if not self.can_update():
            return

        return self.tc_requests.delete_tag(self.api_type, self.api_sub_type, self.unique_id, name)

    def labels(self):
        if not self.can_update():
            return

        return self.tc_requests.labels(self.api_type, self.api_sub_type, self.unique_id)

    def label(self, label, action='ADD'):
        if not self.can_update():
            return
        if action == 'GET':
            return self.tc_requests.get_label(self.api_type, self.api_sub_type, self.unique_id, label)

        if action == 'ADD':
            return self.tc_requests.add_label(self.api_type, self.api_sub_type, self.unique_id, label)

        if action == 'DELETE':
            return self.tc_requests.delete_tag(self.api_type, self.api_sub_type, self.unique_id, label)

        return None

    def add_label(self, label):
        if not self.can_update():
            return

        return self.tc_requests.add_label(self.api_type, self.api_sub_type, self.unique_id, label)

    def get_label(self, label):
        if not self.can_update():
            return

        return self.tc_requests.get_label(self.api_type, self.api_sub_type, self.unique_id, label)

    def delete_label(self, label):
        if not self.can_update():
            return

        return self.tc_requests.delete_label(self.api_type, self.api_sub_type, self.unique_id, label)

    def indicator_associations(self):
        if not self.can_update():
            return

        return self.tc_requests.indicator_associations(self.api_type, self.api_sub_type, self.unique_id)

    def group_associations(self):
        if not self.can_update():
            return

        return self.tc_requests.group_associations(self.api_type, self.api_sub_type, self.unique_id)

    def victim_asset_associations(self):
        if not self.can_update():
            return

        return self.tc_requests.victim_asset_associations(self.api_type, self.api_sub_type, self.unique_id)

    def indicator_associations_types(self, type):
        if not self.can_update():
            return

        return self.tc_requests.indicator_associations_types(self.api_type, self.api_sub_type, self.unique_id, type)

    def group_associations_types(self, type, api_entity=None, api_branch=None):
        if not self.can_update():
            return

        return self.tc_requests.group_associations_types(self.api_type, self.api_sub_type, self.unique_id, type,
                                                        api_entity=api_entity, api_branch=api_branch)

    def victim_asset_associations_type(self, type):
        if not self.can_update():
            return

        return self.tc_requests.victim_asset_associations(self.api_type, self.api_sub_type, self.unique_id, type)

    def add_association(self, target):
        if not self.can_update():
            return

        if not target.can_update():
            return

        return self.tc_requests.add_association(self.api_type, self.api_sub_type, self.unique_id,
                                                target.api_type, target.api_sub_type, target.unique_id)

    def delete_association(self, target):
        if not self.can_update():
            return

        if not target.can_update():
            return

        return self.tc_requests.delete_association(self.api_type, self.api_sub_type, self.unique_id,
                                                   target.api_type, target.api_sub_type, target.unique_id)

    def create_observers(self, count, date_observed):
        if not self.can_update():
            return

        data = {
            'count': count,
            'dataObserved': self._utils.format_datetime(date_observed, date_format='%Y-%m-%dT%H:%M:%SZ')
        }

        return self.tc_requests.observations(self.api_type, self.api_sub_type, self.unique_id, data)

    def add_false_positive(self):
        if not self.can_update():
            return

        return self.tc_requests.add_false_positive(self.api_type, self.api_sub_type, self.unique_id)

    def attributes(self):
        if not self.can_update():
            return

        return self.tc_requests.attributes(self.api_type, self.api_sub_type, self.unique_id)

    def attribute(self, attribute_id, action='GET'):
        if not self.can_update():
            return

        if action == 'GET':
            return self.tc_requests.get_attribute(self.api_type, self.api_sub_type, self.unique_id, attribute_id)

        if action == 'DELETE':
            return self.tc_requests.delete_attribute(self.api_type, self.api_sub_type, self.unique_id, attribute_id)

    def add_attribute(self, attribute_type, attribute_value):
        if not self.can_update():
            return

        return self.tc_requests.add_attribute(self.api_type, self.api_sub_type, self.unique_id,
                                              attribute_type, attribute_value)

    def attribute_labels(self, attribute_id):
        if not self.can_update():
            return

        return self.tc_requests.attribute_labels(self.api_type, self.api_sub_type, self.unique_id, attribute_id)

    def attribute_label(self, attribute_id, label, action='GET'):
        if not self.can_update():
            return

        if action == 'GET':
            return self.tc_requests.get_attribute_label(self.api_type, self.api_sub_type, self.unique_id,
                                                        attribute_id, label)
        if action == 'DELETE':
            return self.tc_requests.delete_attribute_label(self.api_type, self.api_sub_type, self.unique_id,
                                                           attribute_id, label)

    def add_attribute_label(self, attribute_id, label):
        if not self.can_update():
            return

        return self.tc_requests.add_attribute_label(self.api_type, self.api_sub_type, self.unique_id,
                                                    attribute_id, label)

    def _base_request(self):
        return {'unique_id': self.unique_id,
                'type': self.api_type,
                'sub_type': self.api_sub_type}

    def can_create(self):
        pass

    def can_delete(self):
        if self.unique_id:
            return True
        return False

    def can_update(self):
        if self.unique_id:
            return True
        return False

    """ Over ridden by the sub classes"""
    def _set_unique_id(self, response_json):
        pass

    def __str__(self):
        """Return string representation of object."""
        return json.dumps(self.data, indent=4)
