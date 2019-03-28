# -*- coding: utf-8 -*-
"""ThreatConnect TI Victim"""

from tcex.tcex_ti.mappings.tcex_ti_mappings import TIMappings

# import local modules for dynamic reference
module = __import__(__name__)


class Victim(TIMappings):
    """Unique API calls for Victim API Endpoints"""

    def __init__(self, tcex, name, **kwargs):
        super(Victim, self).__init__(tcex, 'Victim', 'victims', None, 'victim')
        self._data['name'] = name

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    @staticmethod
    def is_victim():
        return True

    def can_create(self):
        """

        :return:
        """
        if self._data.get('name'):
            return True
        return False

    def add_key_value(self, key, value):
        """

        :param key:
        :param value:
        """
        self._data[key] = value

    def _set_unique_id(self, json_response):
        """

        :param json_response:
        """
        self.unique_id = json_response.get('id', '')

    @property
    def name(self):
        """Return Indicator summary."""
        return self._data.get('name')

    def add_asset(self, asset, asset_name, asset_type):
        """

        :param asset:
        :param asset_name:
        :param asset_type:
        :return:
        """
        if asset == 'PHONE':
            return self.tc_requests.add_victim_phone_asset(self.unique_id, asset_name)
        if asset == 'EMAIL':
            return self.tc_requests.add_victim_email_asset(self.unique_id, asset_name, asset_type)
        if asset == 'NETWORK':
            return self.tc_requests.add_victim_network_asset(self.unique_id, asset_name, asset_type)
        if asset == 'SOCIAL':
            return self.tc_requests.add_victim_social_asset(self.unique_id, asset_name, asset_type)
        if asset == 'WEB':
            return self.tc_requests.add_victim_web_asset(self.unique_id, asset_name)
        return None

    def update_asset(self, asset, asset_id, asset_name, asset_type):
        """

        :param asset:
        :param asset_id:
        :param asset_name:
        :param asset_type:
        :return:
        """
        if asset == 'PHONE':
            return self.tc_requests.update_victim_phone_asset(self.unique_id, asset_id, asset_name)
        if asset == 'EMAIL':
            return self.tc_requests.update_victim_email_asset(
                self.unique_id, asset_id, asset_name, asset_type
            )
        if asset == 'NETWORK':
            return self.tc_requests.update_victim_network_asset(
                self.unique_id, asset_id, asset_name, asset_type
            )
        if asset == 'SOCIAL':
            return self.tc_requests.update_victim_social_asset(
                self.unique_id, asset_id, asset_name, asset_type
            )
        if asset == 'WEB':
            return self.tc_requests.update_victim_web_asset(self.unique_id, asset_id, asset_name)
        return None

    def asset(self, asset_id, asset, action='GET'):
        """

        :param asset_id:
        :param asset:
        :param action:
        :return:
        """
        if asset == 'PHONE':
            return self.tc_requests.victim_phone_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_id, action=action
            )
        if asset == 'EMAIL':
            return self.tc_requests.victim_email_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_id, action=action
            )
        if asset == 'NETWORK':
            return self.tc_requests.victim_network_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_id, action=action
            )
        if asset == 'SOCIAL':
            return self.tc_requests.victim_social_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_id, action=action
            )
        if asset == 'WEB':
            return self.tc_requests.victim_web_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_id, action=action
            )
        return None

    def assets(self, asset=None):
        """

        :param asset:
        :return:
        """

        request = None
        if not asset:
            request = self.tc_requests.victim_assets(
                self.api_type, self.api_sub_type, self.unique_id
            )
        if asset == 'PHONE':
            request = self.tc_requests.victim_phone_assets(
                self.api_type, self.api_sub_type, self.unique_id
            )
        if asset == 'EMAIL':
            request = self.tc_requests.victim_email_assets(
                self.api_type, self.api_sub_type, self.unique_id
            )
        if asset == 'NETWORK':
            request = self.tc_requests.victim_network_assets(
                self.api_type, self.api_sub_type, self.unique_id
            )
        if asset == 'SOCIAL':
            request = self.tc_requests.victim_social_assets(
                self.api_type, self.api_sub_type, self.unique_id
            )
        if asset == 'WEB':
            request = self.tc_requests.victim_web_assets(
                self.api_type, self.api_sub_type, self.unique_id
            )

        return request

    def get_asset(self, asset_id, asset):
        """

        :param asset_id:
        :param asset:
        :return:
        """
        return self.asset(asset_id, asset=asset)

    def delete_asset(self, asset_id, asset):
        """

        :param asset_id:
        :param asset:
        :return:
        """
        return self.asset(asset_id, asset=asset, action='DELETE')

    def phone_assets(self):
        """

        :return:
        """
        return self.assets(asset='HANDLER')

    def email_assets(self):
        """

        :return:
        """
        return self.assets(asset='PHONE')

    def network_assets(self):
        """

        :return:
        """
        return self.assets(asset='URL')

    def social_assets(self):
        """

        :return:
        """
        return self.assets(asset='URL')

    def web_assets(self):
        """

        :return:
        """
        return self.assets(asset='URL')

    def phone_asset(self, asset_id, action='GET'):
        """

        :param asset_id:
        :param action:
        :return:
        """
        return self.asset(asset_id, 'HANDLER', action=action)

    def email_asset(self, asset_id, action='GET'):
        """

        :param asset_id:
        :param action:
        :return:
        """
        return self.asset(asset_id, 'PHONE', action=action)

    def network_asset(self, asset_id, action='GET'):
        """

        :param asset_id:
        :param action:
        :return:
        """
        return self.asset(asset_id, 'URL', action=action)

    def social_asset(self, asset_id, action='GET'):
        """

        :param asset_id:
        :param action:
        :return:
        """
        return self.asset(asset_id, 'URL', action=action)

    def web_asset(self, asset_id, action='GET'):
        """

        :param asset_id:
        :param action:
        :return:
        """
        return self.asset(asset_id, 'URL', action=action)

    def get_phone_asset(self, asset_id):
        """

        :param asset_id:
        :return:
        """
        return self.get_asset(asset_id, 'HANDLER')

    def get_email_asset(self, asset_id):
        """

        :param asset_id:
        :return:
        """
        return self.get_asset(asset_id, 'PHONE')

    def get_network_asset(self, asset_id):
        """

        :param asset_id:
        :return:
        """
        return self.get_asset(asset_id, 'URL')

    def get_social_asset(self, asset_id):
        """

        :param asset_id:
        :return:
        """
        return self.get_asset(asset_id, 'URL')

    def get_web_asset(self, asset_id):
        """

        :param asset_id:
        :return:
        """
        return self.get_asset(asset_id, 'URL')

    def delete_phone_asset(self, asset_id):
        """

        :param asset_id:
        :return:
        """
        return self.delete_asset(asset_id, 'HANDLER')

    def delete_email_asset(self, asset_id):
        """

        :param asset_id:
        :return:
        """
        return self.delete_asset(asset_id, 'PHONE')

    def delete_network_asset(self, asset_id):
        """

        :param asset_id:
        :return:
        """
        return self.delete_asset(asset_id, 'URL')

    def delete_social_asset(self, asset_id):
        """

        :param asset_id:
        :return:
        """
        return self.delete_asset(asset_id, 'URL')

    def delete_web_asset(self, asset_id):
        """

        :param asset_id:
        :return:
        """
        return self.delete_asset(asset_id, 'URL')

    def add_phone_asset(self, name):
        """

        :param name:
        :return:
        """
        return self.add_asset('PHONE', name, None)

    def add_email_asset(self, name, asset_type):
        """

        :param name:
        :param asset_type:
        """
        self.add_asset('EMAIL', name, asset_type)

    def add_network_asset(self, name, asset_type):
        """

        :param name:
        :param asset_type:
        """
        self.add_asset('NETWORK', name, asset_type)

    def add_social_asset(self, name, asset_type):
        """

        :param name:
        :param asset_type:
        """
        self.add_asset('SOCIAL', name, asset_type)

    def add_web_asset(self, name):
        """

        :param name:
        """
        self.add_asset('WEB', name, None)

    def update_phone_asset(self, asset_id, name):
        """

        :param asset_id:
        :param name:
        :return:
        """
        return self.update_asset('PHONE', asset_id, name, None)

    def update_email_asset(self, asset_id, name, asset_type):
        """

        :param asset_id:
        :param name:
        :param asset_type:
        """
        self.update_asset('EMAIL', asset_id, name, asset_type)

    def update_network_asset(self, asset_id, name, asset_type):
        """

        :param asset_id:
        :param name:
        :param asset_type:
        """
        self.update_asset('NETWORK', asset_id, name, asset_type)

    def update_social_asset(self, asset_id, name, asset_type):
        """

        :param asset_id:
        :param name:
        :param asset_type:
        """
        self.update_asset('SOCIAL', asset_id, name, asset_type)

    def update_web_asset(self, asset_id, name):
        """

        :param asset_id:
        :param name:
        """
        self.update_asset('WEB', asset_id, name, None)
