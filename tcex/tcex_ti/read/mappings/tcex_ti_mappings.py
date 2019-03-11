from tcex.tcex_ti.tcex_ti_tc_request import TiTcRequest
import json
from tcex.tcex_utils import TcExUtils


class TIMappings(object):
    def __init__(self, tcex, type, **kwargs):
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
        self._unique_id = kwargs.get('unique_id', None)

        self._utils = TcExUtils()
        self._tc_requests = TiTcRequest(self._tcex)

    @property
    def type(self):
        """Return Group type."""
        return self._type

    @property
    def sub_type(self):
        """Return Group type."""
        return self._data.get('sub_type')

    @property
    def xid(self):
        """Return Group xid."""
        return self._data.get('xid')

    @property
    def unique_id(self):
        self._data.get('unique_id')

    @unique_id.setter
    def unique_id(self, unique_id):
        self._data['unique_id'] = unique_id

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

        response = self._tc_requests.create(owner, self._data)

        # if self._tc_requests.success(response):
        #     self._data['id'] = response.json().get('data', {}).get(self.data.get('sub_type')).get('id')

        return response

    def delete(self):
        if not self.can_delete():
            return

        return self._tc_requests.delete(self._data)

    def update(self):
        if not self.can_update():
            return

        return self._tc_requests.update(self._data)

    def tag(self, name, action='CREATE'):
        if not self.can_update():
            return

        return self._tc_requests._tag(self._data, name, action=action.upper())

    def label(self, label, action='CREATE'):
        if not self.can_update():
            return

        return self._tc_requests._label(self._data, label, action=action.upper())

    def association(self, target, action='CREATE'):
        if not self.can_update():
            return

        return self._tc_requests._association(self._data, target._data, action)

    def create_observers(self, count, date_observed):
        if not self.can_update():
            return

        data = {
            'type': self.type,
            'sub_type': self.sub_type,
            'unique_id': self.unique_id,
            'count': count,
            'dataObserved': self._utils.format_datetime(date_observed, date_format='%Y-%m-%dT%H:%M:%SZ')
        }

        return self._tc_requests._observations(data)

    def create_false_positive(self):
        if not self.can_update():
            return

        return self._tc_requests._create_false_positive()

    def attribute(self, attribute_type, value, id=None, action='CREATE'):
        if not self.can_update():
            return

        return self._tc_requests._attribute(self._data, attribute_type, value, attribute_id=id, action=action.upper())

    def attribute_label(self, attribute_id, label, action='CREATE'):
        if not self.can_update():
            return

        return self._tc_requests._attribute_label(self._data, attribute_id, label, action=action.upper())

    def _base_request(self):
        return {'unique_id': self.unique_id,
                'type': self.type,
                'sub_type': self.sub_type}

    def create_tag(self, name):
        return self.tag(name)

    def delete_tag(self, name):
        return self.tag(name, action='DELETE')

    def add_attribute_labels(self, id, label):
        return self.attribute_label(id, label)

    def delete_attribute_labels(self, id, label):
        return self.attribute_label(id, label, action='DELETE')

    def create_attribute(self, attribute_type, value):
        return self.attribute(attribute_type, value)

    def delete_attribute(self, attribute_id):
        return self.attribute(None, None, id=attribute_id, action='DELETE')

    def create_label(self, name):
        return self.label(name)

    def delete_label(self, name):
        return self.label(name, action='DELETE')

    def create_association(self, target):
        return self.association(target)

    def delete_association(self, target):
        return self.association(target, action='DELETE')

    def can_create(self):
        pass

    def can_delete(self):
        if self._data.get('unique_id'):
            return True
        return False

    def can_update(self):
        if self._data.get('unique_id'):
            return True
        return False

    def __str__(self):
        """Return string representation of object."""
        return json.dumps(self.data, indent=4)
