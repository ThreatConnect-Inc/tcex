# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module"""

from tcex.tcex_ti.write.mappings.tcex_ti_mappings import TIMappings

# import local modules for dynamic reference
module = __import__(__name__)


class Victim(TIMappings):
    def __init__(self, tcex, name, **kwargs):
        super(Victim, self).__init__(tcex, 'Victim', 'victims', None, **kwargs)
        self._data['name'] = name

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    def can_create(self):
        if self._data.get('name'):
            return True
        return False
    
    def add_key_value(self, key, value):
        self._data[key] = value

    @property
    def name(self):
        """Return Indicator summary."""
        return self._data.get('name')

    def asset(self, asset_type, name, type=None, id=None, action='CREATE'):
        return self.tc_requests.victim_asset(self.unique_id, asset_type, name, type=type, id=id, action=action)

    def update_asset(self, asset_type, name, id, type=None):
        return self.asset(asset_type, name, type=type, id=id, action='UPDATE')

    def delete_asset(self, asset_type, id):
        return self.asset(asset_type, None, id=id, action='DELETE')

    def create_asset(self, asset_type, name, type=None):
        return self.asset(asset_type, name, type=type)

    def create_email_asset(self, name, type):
        return self.create_asset('EMAIL', name, type=type)

    def update_email_asset(self, name, type, id):
        return self.update_asset('EMAIL', name, id, type=type)

    def delete_email_asset(self, id):
        return self.delete_asset('EMAIL', id)

    def create_phone_asset(self, name):
        return self.create_asset('PHONE', name)

    def update_phone_asset(self, name, id):
        return self.update_asset('PHONE', name, id)

    def delete_phone_asset(self, id):
        return self.delete_asset('PHONE', id)

    def create_website_asset(self, name):
        return self.create_asset('WEBSITE', name)

    def update_website_asset(self, name, id):
        return self.update_asset('WEBSITE', name, id)

    def delete_website_asset(self, id):
        return self.delete_asset('WEBSITE', id)

    def create_network_accounts_asset(self, name, type):
        return self.create_asset('NETWORK', name, type=type)

    def update_network_accounts_asset(self, name, id, type=type):
        return self.update_asset('NETWORK', name, id, type=type)

    def delete_network_accounts_asset(self, id):
        return self.delete_asset('NETWORK', id)

    def create_social_networks_asset(self, name, type):
        return self.create_asset('SOCIAL', name, type=type)

    def update_social_networks_asset(self, name, type, id):
        return self.update_asset('SOCIAL', name, id, type=type)

    def delete_social_networks_asset(self, id):
        return self.delete_asset('SOCIAL', id)

