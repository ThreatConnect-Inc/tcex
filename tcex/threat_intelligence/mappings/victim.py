# -*- coding: utf-8 -*-
"""ThreatConnect TI Victim"""

from .mappings import Mappings

# import local modules for dynamic reference
module = __import__(__name__)


class Victim(Mappings):
    """Unique API calls for Victim API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            owner (str, kwargs): The owner for this Victim. Default to default Org when not provided
            name (str, kwargs): [Required for Create] The name for this Victim.
        """
        super().__init__(tcex, 'Victim', 'victims', None, 'victim', None, kwargs.pop('owner', None))
        self.name = None
        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    def _set_unique_id(self, json_response):
        """Set the unique id of the Group."""
        self.unique_id = json_response.get('id', '')

    def add_asset(self, asset_type, body):
        """Add an asset to the Victim

        Valid asset_type and optional identifier:
        + email
        + network
        + phone
        + social
        + web

        Args:
            asset_type: (str) Either email, network, phone, social, or web.
            body: (dict) the body of the asset being added.

        Return:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if body is None:
            body = {}

        if asset_type is None:
            self._tcex.handle_error(
                925, ['asset_type', 'update_asset', 'asset_type', 'asset_type', asset_type]
            )

        return self.tc_requests.victim_add_asset(self.unique_id, asset_type, body)

    def add_email_asset(self, address, address_type):
        """Add a email asset to the Victim

        Args:
            address: (str) The asset address.
            address_type: (str) The asset address_type

        Return:
            requests.Response: The response from the API call.
        """
        asset_data = {'address': address, 'addressType': address_type}
        return self.add_asset('EMAIL', asset_data)

    def add_key_value(self, key, value):
        """Add the key-value to the Victim. """
        key = self._metadata_map.get(key, key)
        if key in ['unique_id', 'id']:
            self._unique_id = str(value)
        else:
            self._data[key] = value

    @property
    def _metadata_map(self):
        """Return metadata map for Group objects."""
        return {'work_location': 'workLocation'}

    def add_network_asset(self, account, network):
        """Add a network asset to the Victim

        Args:
            account: (str) The asset account.
            network: (str) The asset network

        Return:
            requests.Response: The response from the API call.
        """
        asset_data = {'account': account, 'network': network}
        return self.add_asset('NETWORK', asset_data)

    def add_phone_asset(self, phone_type):
        """Add a phone asset to the Victim

        Args:
            phone_type: (str) The asset phone type.

        Return:
            requests.Response: The response from the API call.
        """
        asset_data = {'phoneType': phone_type}
        return self.add_asset('PHONE', asset_data)

    def add_social_asset(self, account, network):
        """Add a social asset to the Victim

        Args:
            account: (str) The asset account.
            network: (str) The asset network

        Return:
            requests.Response: The response from the API call.
        """
        asset_data = {'account': account, 'network': network}
        return self.add_asset('SOCIAL', asset_data)

    def add_web_asset(self, web_site):
        """Add a web asset to the Victim

        Args:
            web_site: (str) The asset account.

        Return:
            requests.Response: The response from the API call.
        """
        asset_data = {'webSite': web_site}
        return self.add_asset('WEB', asset_data)

    @property
    def as_entity(self):
        """Return the entity representation of the Victim."""
        return {
            'type': 'Victim',
            'value': self.name,
            'id': int(self.unique_id) if self.unique_id else None,
        }

    def assets(self, asset_type=None):
        """
        Gets the assets of a Victim

        Valid asset_type and optional identifier:
        + email
        + network
        + phone
        + social
        + web

        Args:
            asset_type: (str) The type of asset to be retrieved. Defaults to all of them.

        Yield:
            Json: The asset being retrieved.

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.victim_assets(
            self.api_type, self.api_branch, self.unique_id, asset_type
        )

    def can_create(self):
        """Return True if victim can be create."""
        return self.data.get('name') is not None

    def delete_asset(self, asset_id, asset_type):
        """Delete an asset of the Victim

        Valid asset_type and optional identifier:
        + email
        + network
        + phone
        + social
        + web

        Args:
            asset_id: (int) the id of the asset being deleted.
            asset_type: (str) Either email, network, phone, social, or web.

        Return:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if asset_type is None:
            self._tcex.handle_error(
                925, ['asset_type', 'update_asset', 'asset_type', 'asset_type', asset_type]
            )

        return self.tc_requests.victim_delete_asset(self.unique_id, asset_type, asset_id)

    def delete_email_asset(self, asset_id):
        """Delete an email asset of the Victim

        Args:
            asset_id: (int) the id of the asset being deleted.

        Return:
            requests.Response: The response from the API call.
        """
        return self.delete_asset(asset_id, 'EMAIL')

    def delete_network_asset(self, asset_id):
        """Delete an network asset of the Victim

        Args:
            asset_id: (int) the id of the asset being deleted.

        Return:
            requests.Response: The response from the API call.
        """
        return self.delete_asset(asset_id, 'NETWORK')

    def delete_phone_asset(self, asset_id):
        """Delete an phone asset of the Victim

        Args:
            asset_id: (int) the id of the asset being deleted.

        Return:
            requests.Response: The response from the API call.
        """
        return self.delete_asset(asset_id, 'PHONE')

    def delete_social_asset(self, asset_id):
        """Delete an social asset of the Victim

        Args:
            asset_id: (int) the id of the asset being deleted.

        Return:
            requests.Response: The response from the API call.
        """
        return self.delete_asset(asset_id, 'SOCIAL')

    def delete_web_asset(self, asset_id):
        """Delete an web asset of the Victim

        Args:
            asset_id: (int) the id of the asset being deleted.

        Return:
            requests.Response: The response from the API call.
        """
        return self.delete_asset(asset_id, 'WEB')

    def email_assets(self):
        """
        Gets the email assets of a Victim

        Yield:
            Json: The asset being retrieved.
        """
        return self.assets(asset_type='EMAIL')

    def get_asset(self, asset_id, asset_type):
        """
        Gets the assets of a Victim

        Valid asset_type and optional identifier:
        + email
        + network
        + phone
        + social
        + web

        Args:
            asset_id: (int) the id of the asset being deleted.
            asset_type: (str) The type of asset to be retrieved.

        Return:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if asset_type is None:
            self._tcex.handle_error(
                925, ['asset_type', 'update_asset', 'asset_type', 'asset_type', asset_type]
            )

        return self.tc_requests.victim_get_asset(self.unique_id, asset_type, asset_id)

    def get_email_asset(self, asset_id):
        """Retrieve an email asset of the Victim

        Args:
            asset_id: (int) the id of the asset being retrieved.

        Return:
            requests.Response: The response from the API call.
        """
        return self.get_asset(asset_id, 'EMAIL')

    def get_network_asset(self, asset_id):
        """Retrieve an network asset of the Victim

        Args:
            asset_id: (int) the id of the asset being retrieved.

        Return:
            requests.Response: The response from the API call.
        """
        return self.get_asset(asset_id, 'NETWORK')

    def get_phone_asset(self, asset_id):
        """Retrieve an phone asset of the Victim

        Args:
            asset_id: (int) the id of the asset being retrieved.

        Return:
            requests.Response: The response from the API call.
        """
        return self.get_asset(asset_id, 'PHONE')

    def get_social_asset(self, asset_id):
        """Retrieve an social asset of the Victim

        Args:
            asset_id: (int) the id of the asset being retrieved.

        Return:
            requests.Response: The response from the API call.
        """
        return self.get_asset(asset_id, 'SOCIAL')

    def get_web_asset(self, asset_id):
        """Retrieve an web asset of the Victim

        Args:
            asset_id: (int) the id of the asset being retrieved.

        Return:
            requests.Response: The response from the API call.
        """
        return self.get_asset(asset_id, 'WEB')

    @staticmethod
    def is_victim():
        """Return True if object is a victim."""
        return True

    @property
    def name(self):
        """Return the Victim name."""
        return self._data.get('name')

    @name.setter
    def name(self, name):
        """Set the Victim name."""
        self._data['name'] = name

    def network_assets(self):
        """
        Gets the network assets of a Victim

        Yield:
            Json: The asset being retrieved.
        """
        return self.assets(asset_type='NETWORK')

    def social_assets(self):
        """
        Gets the social assets of a Victim

        Yield:
            Json: The asset being retrieved.
        """
        return self.assets(asset_type='SOCIAL')

    def phone_assets(self):
        """
        Gets the phone assets of a Victim

        Yield:
            Json: The asset being retrieved.
        """
        return self.assets(asset_type='PHONE')

    def update_asset(self, asset_type, asset_id, body=None):
        """
        Updates a asset of a Victim

        Valid asset_type and optional identifier:
        + email
        + network
        + phone
        + social
        + web

        Args:
            asset_id: (int) the id of the asset being deleted.
            asset_type: (str) The type of asset to be retrieved.
            body: (dict) the body of the asset being updated.

        Return:
            requests.Response: The response from the API call.
        """
        if body is None:
            body = {}

        if asset_type is None:
            self._tcex.handle_error(
                925, ['asset_type', 'update_asset', 'asset_type', 'asset_type', asset_type]
            )

        return self.tc_requests.victim_update_asset(self.unique_id, asset_type, asset_id, body)

    def update_email_asset(self, asset_id, address=None, address_type=None):
        """Update a email asset of the Victim

        Args:
            asset_id: (int) the id of the asset being updated.
            address: (str) The asset address.
            address_type: (str) The asset address type

        Return:
            requests.Response: The response from the API call.
        """
        asset_data = {}
        if address:
            asset_data['address'] = address
        if address_type:
            asset_data['addressType'] = address_type
        return self.update_asset('EMAIL', asset_id, asset_data)

    def update_network_asset(self, asset_id, account=None, network=None):
        """Update a network asset of the Victim

        Args:
            asset_id: (int) the id of the asset being updated.
            account: (str) The asset account.
            network: (str) The asset network

        Return:
            requests.Response: The response from the API call.
        """
        asset_data = {}
        if account:
            asset_data['account'] = account
        if network:
            asset_data['network'] = network
        return self.update_asset('NETWORK', asset_id, asset_data)

    def update_phone_asset(self, asset_id, phone_type=None):
        """Update a phone asset of the Victim

        Args:
            asset_id: (int) the id of the asset being updated.
            phone_type: (str) The phone type account.

        Return:
            requests.Response: The response from the API call.
        """
        asset_data = {}
        if phone_type:
            asset_data['phoneType'] = phone_type
        return self.update_asset('PHONE', asset_id, asset_data)

    def update_social_asset(self, asset_id, account=None, network=None):
        """Update a social asset of the Victim

        Args:
            asset_id: (int) the id of the asset being updated.
            account: (str) The asset account.
            network: (str) The asset network

        Return:
            requests.Response: The response from the API call.
        """
        asset_data = {}
        if account:
            asset_data['account'] = account
        if network:
            asset_data['network'] = network
        return self.update_asset('SOCIAL', asset_id, asset_data)

    def update_web_asset(self, asset_id, web_site=None):
        """Update a web asset of the Victim

        Args:
            asset_id: (int) the id of the asset being updated.
            web_site: (str) The asset web_site.

        Return:
            requests.Response: The response from the API call.
        """
        asset_data = {}
        if web_site:
            asset_data['webSite'] = web_site
        return self.update_asset('WEB', asset_id, asset_data)

    def web_assets(self):
        """
        Gets the web assets of a Victim

        Yield:
            Json: The asset being retrieved.
        """
        return self.assets(asset_type='WEB')
