# -*- coding: utf-8 -*-
"""ThreatConnect TI Victim"""

from tcex.tcex_ti.mappings.tcex_ti_mappings import TIMappings

# import local modules for dynamic reference
module = __import__(__name__)


class Victim(TIMappings):
    """Unique API calls for Victim API Endpoints"""

    def __init__(self, tcex, name, owner=None, **kwargs):
        super(Victim, self).__init__(tcex, 'Victim', 'victims', None, 'victim', None, owner)
        self._data['name'] = name

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    @staticmethod
    def is_victim():
        return True

    def can_create(self):
        """
         If the name has been provided returns that the Victim can be created,
          otherwise returns that the Victim cannot be created.

         Returns:

         """
        if self._data.get('name'):
            return True
        return False

    def add_key_value(self, key, value):
        """
        Converts the value and adds it as a data field.

        Args:
            key:
            value:
        """
        if key == 'unique_id':
            self._unique_id = str(value)
        else:
            self._data[key] = value

    def _set_unique_id(self, json_response):
        """
        Sets the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = json_response.get('id', '')

    @property
    def name(self):
        """Return Victim name."""
        return self._data.get('name')

    def add_asset(self, asset, asset_name, asset_type):
        """
        Adds a asset to the Victim

        Valid asset_type:
        + PHONE
        + EMAIL
        + NETWORK
        + SOCIAL
        + WEB

        Args:
            asset:
            asset_name:
            asset_type: PHONE, EMAIL, NETWORK, SOCIAL, or WEB

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

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
        self._tcex.handle_error(
            925, ['asset_type', 'add_asset', 'asset_type', 'asset_type', asset_type]
        )
        return None

    def update_asset(self, asset, asset_id, asset_name, asset_type):
        """
        Update a asset of a Victim

        Valid asset_type:
        + PHONE
        + EMAIL
        + NETWORK
        + SOCIAL
        + WEB

        Args:
            asset:
            asset_name:
            asset_id:
            asset_type: PHONE, EMAIL, NETWORK, SOCIAL, or WEB

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

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

        self._tcex.handle_error(
            925, ['asset_type', 'update_asset', 'asset_type', 'asset_type', asset_type]
        )
        return None

    def asset(self, asset_id, asset_type, action='GET'):
        """
        Gets a asset of a Victim

        Valid asset_type:
        + PHONE
        + EMAIL
        + NETWORK
        + SOCIAL
        + WEB

        Args:
            asset_type:
            asset_id:
            action:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if asset_type == 'PHONE':
            return self.tc_requests.victim_phone_asset(
                self.api_type, self.api_branch, self.unique_id, asset_id, action=action
            )
        if asset_type == 'EMAIL':
            return self.tc_requests.victim_email_asset(
                self.api_type, self.api_branch, self.unique_id, asset_id, action=action
            )
        if asset_type == 'NETWORK':
            return self.tc_requests.victim_network_asset(
                self.api_type, self.api_branch, self.unique_id, asset_id, action=action
            )
        if asset_type == 'SOCIAL':
            return self.tc_requests.victim_social_asset(
                self.api_type, self.api_branch, self.unique_id, asset_id, action=action
            )
        if asset_type == 'WEB':
            return self.tc_requests.victim_web_asset(
                self.api_type, self.api_branch, self.unique_id, asset_id, action=action
            )
        self._tcex.handle_error(
            925, ['asset_type', 'asset', 'asset_type', 'asset_type', asset_type]
        )
        return None

    def assets(self, asset_type=None):
        """
        Gets the assets of a Victim

        Args:
            asset_type:

        Yields: asset json

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if not asset_type:
            for a in self.tc_requests.victim_assets(self.api_type, self.api_branch, self.unique_id):
                yield a
        if asset_type == 'PHONE':
            for a in self.tc_requests.victim_phone_assets(
                self.api_type, self.api_branch, self.unique_id
            ):
                yield a
        if asset_type == 'EMAIL':
            for a in self.tc_requests.victim_email_assets(
                self.api_type, self.api_branch, self.unique_id
            ):
                yield a
        if asset_type == 'NETWORK':
            for a in self.tc_requests.victim_network_assets(
                self.api_type, self.api_branch, self.unique_id
            ):
                yield a
        if asset_type == 'SOCIAL':
            for a in self.tc_requests.victim_social_assets(
                self.api_type, self.api_branch, self.unique_id
            ):
                yield a
        if asset_type == 'WEB':
            for a in self.tc_requests.victim_web_assets(
                self.api_type, self.api_branch, self.unique_id
            ):
                yield a

        self._tcex.handle_error(
            925, ['asset_type', 'assets', 'asset_type', 'asset_type', asset_type]
        )

    def get_asset(self, asset_id, asset_type):
        """
        Gets a asset
        Args:
            asset_id:
            asset_type:

        Returns:

        """
        return self.asset(asset_id, asset_type=asset_type)

    def delete_asset(self, asset_id, asset_type):
        """
        Deletes a asset

        Args:
            asset_id:
            asset_type:
        """
        return self.asset(asset_id, asset_type=asset_type, action='DELETE')

    def phone_assets(self):
        """ Gets Phone assets """
        for pa in self.assets(asset_type='PHONE'):
            yield pa

    def email_assets(self):
        """ Gets Phone assets """
        for ea in self.assets(asset_type='EMAIL'):
            yield ea

    def network_assets(self):
        """ Gets Network assets """
        for na in self.assets(asset_type='NETWORK'):
            yield na

    def social_assets(self):
        """ Gets Social assets """
        for sa in self.assets(asset_type='SOCIAL'):
            yield sa

    def web_assets(self):
        """ Gets a Web assets """
        for wa in self.assets(asset_type='WEB'):
            yield wa

    def phone_asset(self, asset_id, action='GET'):
        """ Gets a Phone asset """
        return self.asset(asset_id, 'PHONE', action=action)

    def email_asset(self, asset_id, action='GET'):
        """ Gets a Email asset """
        return self.asset(asset_id, 'EMAIL', action=action)

    def network_asset(self, asset_id, action='GET'):
        """
        Gets a Network Asset
        Args:
            asset_id:
            action:

        Returns:

        """
        return self.asset(asset_id, 'NETWORK', action=action)

    def social_asset(self, asset_id, action='GET'):
        """
        Gets a Social Asset
        Args:
            asset_id:
            action:

        Returns:

        """
        return self.asset(asset_id, 'SOCIAL', action=action)

    def web_asset(self, asset_id, action='GET'):
        """
        Gets a Web Asset
        Args:
            asset_id:
            action:

        Returns:

        """
        return self.asset(asset_id, 'WEB', action=action)

    def get_phone_asset(self, asset_id):
        """
        Gets a Phone Asset
        Args:
            asset_id:
            action:

        Returns:

        """
        return self.get_asset(asset_id, 'PHONE')

    def get_email_asset(self, asset_id):
        """
        Gets a Email Asset
        Args:
            asset_id:
            action:

        Returns:

        """
        return self.get_asset(asset_id, 'EMAIL')

    def get_network_asset(self, asset_id):
        """
        Gets a Network Asset
        Args:
            asset_id:

        Returns:

        """
        return self.get_asset(asset_id, 'NETWORK')

    def get_social_asset(self, asset_id):
        """
        Gets a Social Asset
        Args:
            asset_id:

        Returns:

        """
        return self.get_asset(asset_id, 'SOCIAL')

    def get_web_asset(self, asset_id):
        """
        Gets a Web Asset
        Args:
            asset_id:

        Returns:

        """
        return self.get_asset(asset_id, 'WEB')

    def delete_phone_asset(self, asset_id):
        """
        Gets a Phone Asset
        Args:
            asset_id:

        Returns:

        """
        return self.delete_asset(asset_id, 'PHONE')

    def delete_email_asset(self, asset_id):
        """
        Deletes a Email Asset
        Args:
            asset_id:

        Returns:

        """
        return self.delete_asset(asset_id, 'EMAIL')

    def delete_network_asset(self, asset_id):
        """
        Deletes a Network Asset
        Args:
            asset_id:

        Returns:

        """
        return self.delete_asset(asset_id, 'NETWORK')

    def delete_social_asset(self, asset_id):
        """
        Deletes a Social Asset
        Args:
            asset_id:

        Returns:

        """
        return self.delete_asset(asset_id, 'SOCIAL')

    def delete_web_asset(self, asset_id):
        """
        Deletes a Web Asset
        Args:
            asset_id:

        Returns:

        """
        return self.delete_asset(asset_id, 'WEB')

    def add_phone_asset(self, name):
        """
        Adds a Phone Asset
        Args:
            name: The name provided to the phone asset

        Returns:

        """
        return self.add_asset('PHONE', name, None)

    def add_email_asset(self, name, asset_type):
        """
        Adds a Email Asset
        Args:
            name: The name provided to the email asset
            asset_type: The type provided to the email asset

        Returns:

        """
        self.add_asset('EMAIL', name, asset_type)

    def add_network_asset(self, name, asset_type):
        """
        Adds a Network Asset
        Args:
            name: The name provided to the network asset
            asset_type: The type provided to the network asset

        Returns:

        """
        self.add_asset('NETWORK', name, asset_type)

    def add_social_asset(self, name, asset_type):
        """
        Adds a Social Asset
        Args:
            name: The name provided to the social asset
            asset_type: The type provided to the social asset

        Returns:

        """
        self.add_asset('SOCIAL', name, asset_type)

    def add_web_asset(self, name):
        """
        Adds a Web Asset
        Args:
            name: The name provided to the web asset

        Returns:

        """
        self.add_asset('WEB', name, None)

    def update_phone_asset(self, asset_id, name):
        """
        Updates a Phone Asset
        Args:
            name: The name provided to the phone asset
            asset_id:

        Returns:

        """
        return self.update_asset('PHONE', asset_id, name, None)

    def update_email_asset(self, asset_id, name, asset_type):
        """
        Updates a Email Asset
        Args:
            name: The name provided to the email asset
            asset_type: The type provided to the email asset
            asset_id:

        Returns:

        """
        self.update_asset('EMAIL', asset_id, name, asset_type)

    def update_network_asset(self, asset_id, name, asset_type):
        """
        Updates a Network Asset
        Args:
            name: The name provided to the network asset
            asset_type: The type provided to the network asset
            asset_id:

        Returns:

        """
        self.update_asset('NETWORK', asset_id, name, asset_type)

    def update_social_asset(self, asset_id, name, asset_type):
        """
        Updates a Social Asset
        Args:
            name: The name provided to the social asset
            asset_type: The type provided to the social asset
            asset_id:

        Returns:

        """
        self.update_asset('SOCIAL', asset_id, name, asset_type)

    def update_web_asset(self, asset_id, name):
        """
        Updates a Web Asset
        Args:
            name: The name provided to the web asset
            asset_id:

        Returns:

        """
        self.update_asset('WEB', asset_id, name, None)
