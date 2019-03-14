# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module"""

from tcex.tcex_ti.mappings.tcex_ti_mappings import TIMappings

# import local modules for dynamic reference
module = __import__(__name__)


class Victim(TIMappings):
    def __init__(self, tcex, name, **kwargs):
        super(Victim, self).__init__(tcex, 'Victim', 'victims', None, 'victim', **kwargs)
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

    def add_asset(self, type, asset_name, asset_type):
        if type == 'PHONE':
            return self.tc_requests.add_victim_phone_asset(self.unique_id, asset_name)
        if type == 'EMAIL':
            return self.tc_requests.add_victim_email_asset(self.unique_id, asset_name, asset_type)
        if type == 'NETWORK':
            return self.tc_requests.add_victim_network_asset(self.unique_id, asset_name, asset_type)
        if type == 'SOCIAL':
            return self.tc_requests.add_victim_social_asset(self.unique_id, asset_name, asset_type)
        if type == 'WEB':
            return self.tc_requests.add_victim_web_asset(self.unique_id, asset_name)

    def update_asset(self, type, asset_id, asset_name, asset_type):
        if type == 'PHONE':
            return self.tc_requests.update_victim_phone_asset(self.unique_id, asset_id, asset_name)
        if type == 'EMAIL':
            return self.tc_requests.update_victim_email_asset(self.unique_id, asset_id, asset_name, asset_type)
        if type == 'NETWORK':
            return self.tc_requests.update_victim_network_asset(self.unique_id, asset_id, asset_name, asset_type)
        if type == 'SOCIAL':
            return self.tc_requests.update_victim_social_asset(self.unique_id, asset_id, asset_name, asset_type)
        if type == 'WEB':
            return self.tc_requests.update_victim_web_asset(self.unique_id, asset_id, asset_name)

    def asset(self, asset_id, type, action='GET'):
        if type == 'PHONE':
            return self.tc_requests.victim_phone_asset(self.api_type, self.api_sub_type, self.unique_id,
                                                          asset_id, action=action)
        if type == 'EMAIL':
            return self.tc_requests.victim_email_asset(self.api_type, self.api_sub_type, self.unique_id,
                                                          asset_id, action=action)
        if type == 'NETWORK':
            return self.tc_requests.victim_network_asset(self.api_type, self.api_sub_type, self.unique_id,
                                                           asset_id, action=action)
        if type == 'SOCIAL':
            return self.tc_requests.victim_social_asset(self.api_type, self.api_sub_type, self.unique_id,
                                                          asset_id, action=action)
        if type == 'WEB':
            return self.tc_requests.victim_web_asset(self.api_type, self.api_sub_type, self.unique_id,
                                                          asset_id, action=action)
        return None

    def assets(self, type=None):
        if not type:
            return self.tc_requests.victim_assets(self.api_type, self.api_sub_type, self.unique_id)
        if type == 'PHONE':
            return self.tc_requests.victim_phone_assets(self.api_type, self.api_sub_type, self.unique_id)
        if type == 'EMAIL':
            return self.tc_requests.victim_email_assets(self.api_type, self.api_sub_type, self.unique_id)
        if type == 'NETWORK':
            return self.tc_requests.victim_network_assets(self.api_type, self.api_sub_type, self.unique_id)
        if type == 'SOCIAL':
            return self.tc_requests.victim_social_assets(self.api_type, self.api_sub_type, self.unique_id)
        if type == 'WEB':
            return self.tc_requests.victim_web_assets(self.api_type, self.api_sub_type, self.unique_id)

        return None

    def get_asset(self, asset_id, type):
        return self.asset(asset_id, type=type)

    def delete_asset(self, asset_id, type):
        return self.asset(asset_id, type=type, action='DELETE')

    def phone_assets(self):
        return self.assets(type='HANDLER')

    def email_assets(self):
        return self.assets(type='PHONE')

    def network_assets(self):
        return self.assets(type='URL')

    def social_assets(self):
        return self.assets(type='URL')

    def web_assets(self):
        return self.assets(type='URL')

    def phone_asset(self, asset_id, action='GET'):
        return self.asset(asset_id, 'HANDLER', action=action)

    def email_asset(self, asset_id, action='GET'):
        return self.asset(asset_id, 'PHONE', action=action)

    def network_asset(self, asset_id, action='GET'):
        return self.asset(asset_id, 'URL', action=action)

    def social_asset(self, asset_id, action='GET'):
        return self.asset(asset_id, 'URL', action=action)

    def web_asset(self, asset_id, action='GET'):
        return self.asset(asset_id, 'URL', action=action)

    def get_phone_asset(self, asset_id):
        return self.get_asset(asset_id, 'HANDLER')

    def get_email_asset(self, asset_id):
        return self.get_asset(asset_id, 'PHONE')

    def get_network_asset(self, asset_id):
        return self.get_asset(asset_id, 'URL')

    def get_social_asset(self, asset_id):
        return self.get_asset(asset_id, 'URL')

    def get_web_asset(self, asset_id):
        return self.get_asset(asset_id, 'URL')

    def delete_phone_asset(self, asset_id):
        return self.delete_asset(asset_id, 'HANDLER')

    def delete_email_asset(self, asset_id):
        return self.delete_asset(asset_id, 'PHONE')

    def delete_network_asset(self, asset_id):
        return self.delete_asset(asset_id, 'URL')

    def delete_social_asset(self, asset_id):
        return self.delete_asset(asset_id, 'URL')

    def delete_web_asset(self, asset_id):
        return self.delete_asset(asset_id, 'URL')

    def add_phone_asset(self, name):
        return self.add_asset('PHONE', name, None)

    def add_email_asset(self, name, type):
        self.add_asset('EMAIL', name, type)

    def add_network_asset(self, name, type):
        self.add_asset('NETWORK', name, type)

    def add_social_asset(self, name, type):
        self.add_asset('SOCIAL', name, type)

    def add_web_asset(self, name):
        self.add_asset('WEB', name, None)

    def update_phone_asset(self, asset_id, name):
        return self.update_asset('PHONE', asset_id, name, None)

    def update_email_asset(self, asset_id, name, type):
        self.update_asset('EMAIL', asset_id, name, type)

    def update_network_asset(self, asset_id, name, type):
        self.update_asset('NETWORK', asset_id, name, type)

    def update_social_asset(self, asset_id, name, type):
        self.update_asset('SOCIAL', asset_id, name, type)

    def update_web_asset(self, asset_id, name):
        self.update_asset('WEB', asset_id, name, None)
