# -*- coding: utf-8 -*-
"""ThreatConnect TI Victim"""

from .mappings import Mappings

# import local modules for dynamic reference
module = __import__(__name__)


class Victim(Mappings):
    """Unique API calls for Victim API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties."""
        super().__init__(
            tcex,
            main_type='Victim',
            api_type='victims',
            sub_type=None,
            api_entity='victim',
            api_branch=None,
            **kwargs
        )

    def add_asset(self, asset_type, asset_value, **kwargs):
        """Add an asset to the Victim

        Valid asset_type and optional identifier:
        + email - address_type
        + network - network
        + phone - N/A
        + social - network
        + web - N/A

        Args:
            asset_type: (str) Either phone, handle, or urL
            asset_value: (str) the value for the asset

        Returns:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        asset_methods = {
            'email': self.tc_requests.add_email_asset,
            'network': self.tc_requests.add_victim_network_asset,
            'phone': self.tc_requests.add_victim_phone_asset,
            'social': self.tc_requests.add_victim_social_asset,
            'web': self.tc_requests.add_victim_web_asset,
        }

        # handle invalid input
        if asset_methods.get(asset_type.lower()) is None:
            self._tcex.handle_error(
                925, ['asset_type', 'assets', 'asset_type', 'asset_type', asset_type]
            )

        return asset_methods.get(asset_type.lower())(self.unique_id, asset_value, **kwargs)

    def add_key_value(self, key, value):
        """Convert the value and adds it as a data field.

        Args:
            key ([type]): [description]
            value ([type]): [description]
        """
        if key == 'unique_id':
            self._unique_id = str(value)
        else:
            self._data[key] = value

    def add_email_asset(self, value, address_type):
        """Add a email asset to the Victim.

        Args:
            value: The value of the asset
            address_type: The address type (e.g., personal, business)

        Returns:
            requests.Response: The response from the API call.
        """
        self.add_asset('email', value, address_type=address_type)

    def add_phone_asset(self, value):
        """Add a phone asset to the Victim.

        Args:
            value: The value of the asset

        Returns:
            requests.Response: The response from the API call.
        """
        return self.add_asset('phone', value)

    def add_network_asset(self, value, network):
        """Add a network asset to the Victim.

        Args:
            value: The value of the asset
            network: The network the asset is attached.

        Returns:
            requests.Response: The response from the API call.
        """
        self.add_asset('network', value, network=network)

    def add_social_asset(self, value, network):
        """Add a social asset to the Victim.

        Args:
            value: The value of the asset
            network: The network the asset is attached.

        Returns:
            requests.Response: The response from the API call.
        """
        self.add_asset('social', value, network=network)

    def add_web_asset(self, name):
        """Add a web asset to the Victim.

        Args:
            value: The value of the asset

        Returns:
            requests.Response: The response from the API call.
        """
        self.add_asset('web', name)

    def asset(self, asset_id, asset_type, action='GET'):
        """Return an asset of a Victim

        Valid asset_type and optional identifier:
        + email - address_type
        + network - network
        + phone - N/A
        + social - network
        + web - N/A

        Returns:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        asset_methods = {
            'email': self.tc_requests.victim_email_asset,
            'network': self.tc_requests.victim_network_asset,
            'phone': self.tc_requests.victim_phone_asset,
            'social': self.tc_requests.victim_social_asset,
            'web': self.tc_requests.victim_web_asset,
        }

        # handle invalid input
        if asset_methods.get(asset_type.lower()) is None:
            self._tcex.handle_error(
                925, ['asset_type', 'assets', 'asset_type', 'asset_type', asset_type]
            )

        return asset_methods.get(asset_type.lower())(self.unique_id, asset_id, action=action)

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
            yield from self.tc_requests.victim_assets(
                self.api_type, self.api_branch, self.unique_id
            )
        if asset_type == 'PHONE':
            yield from self.tc_requests.victim_phone_assets(
                self.api_type, self.api_branch, self.unique_id
            )
        if asset_type == 'EMAIL':
            yield from self.tc_requests.victim_email_assets(
                self.api_type, self.api_branch, self.unique_id
            )
        if asset_type == 'NETWORK':
            yield from self.tc_requests.victim_network_assets(
                self.api_type, self.api_branch, self.unique_id
            )
        if asset_type == 'SOCIAL':
            yield from self.tc_requests.victim_social_assets(
                self.api_type, self.api_branch, self.unique_id
            )
        if asset_type == 'WEB':
            yield from self.tc_requests.victim_web_assets(
                self.api_type, self.api_branch, self.unique_id
            )

        self._tcex.handle_error(
            925, ['asset_type', 'assets', 'asset_type', 'asset_type', asset_type]
        )

    def can_create(self):
        """Return True if victim can be create."""
        return self.data.get('name') is not None

    def delete_asset(self, asset_id, asset_type):
        """
        Deletes a asset

        Args:
            asset_id:
            asset_type:
        """
        return self.asset(asset_id, asset_type=asset_type, action='DELETE')

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

    def get_asset(self, asset_id, asset_type):
        """
        Gets a asset
        Args:
            asset_id:
            asset_type:

        Returns:

        """
        return self.asset(asset_id, asset_type=asset_type)

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

    @staticmethod
    def is_victim():
        """Return True if object is a victim."""
        return True

    @property
    def name(self):
        """Return Victim name."""
        return self._data.get('name')

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

    def phone_assets(self):
        """ Gets Phone assets """
        yield from self.assets(asset_type='PHONE')

    def email_assets(self):
        """ Gets Phone assets """
        yield from self.assets(asset_type='EMAIL')

    def network_assets(self):
        """ Gets Network assets """
        yield from self.assets(asset_type='NETWORK')

    def social_assets(self):
        """ Gets Social assets """
        yield from self.assets(asset_type='SOCIAL')

    def web_assets(self):
        """ Gets a Web assets """
        yield from self.assets(asset_type='WEB')

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
