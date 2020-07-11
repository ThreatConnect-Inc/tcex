# -*- coding: utf-8 -*-
"""ThreatConnect TI Adversary"""
from ..group import Group


class Adversary(Group):
    """Unique API calls for Adversary API Endpoints

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(
            tcex, sub_type='Adversary', api_entity='adversary', api_branch='adversaries', **kwargs
        )

    def add_asset(self, asset_type, asset_value):
        """Add an asset to the Adversary

        Args:
            asset_type: (str) Either phone, handle, or urL
            asset_value: (str) the value for the asset

        Returns:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        asset_methods = {
            'handle': self.tc_requests.add_adversary_handle_asset,
            'phone': self.tc_requests.add_adversary_phone_asset,
            'url': self.tc_requests.add_adversary_url_asset,
        }

        # handle invalid input
        if asset_methods.get(asset_type.lower()) is None:
            self._tcex.handle_error(
                925, ['asset_type', 'assets', 'asset_type', 'asset_type', asset_type]
            )

        return asset_methods.get(asset_type.lower())(self.unique_id, asset_value)

    def add_handle_asset(self, value):
        """Add a Handle asset to the adversary.

        Args:
            value: The value of the asset

        Returns:
            requests.Response: The response from the API call.
        """
        return self.add_asset('HANDLE', value)

    def add_phone_asset(self, value):
        """Add a phone asset to the adversary.

        Args:
            value: The value of the asset

        Returns:
            requests.Response: The response from the API call.
        """
        return self.add_asset('PHONE', value)

    def add_url_asset(self, value):
        """Add a URL asset to the adversary.

        Args:
            value: The value of the asset

        Returns:
            requests.Response: The response from the API call.
        """
        return self.add_asset('URL', value)

    def asset(self, asset_id, asset_type, action='GET'):
        """Get specific Adversary asset type from API

        Args:
            asset_id: (str) The ID of the asset.
            asset_type: (str) Either phone, handle, or url.
            action: (str): The HTTP method (e.g., DELETE or GET)

        Returns:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        asset_methods = {
            'handle': self.tc_requests.adversary_handle_asset,
            'phone': self.tc_requests.adversary_phone_asset,
            'url': self.tc_requests.adversary_url_asset,
        }

        # handle invalid input
        if asset_methods.get(asset_type.lower()) is None:
            self._tcex.handle_error(
                925, ['asset_type', 'assets', 'asset_type', 'asset_type', asset_type]
            )

        return asset_methods.get(asset_type.lower())(self.unique_id, asset_id, action=action)

    def assets(self, asset_type=None):
        """Retrieve all of the assets of a given asset_type

        Args:
            asset_type: (str) Either None, PHONE, HANDLE, or URL

        Returns:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        asset_methods = {
            'handle': self.tc_requests.adversary_handle_assets,
            'phone': self.tc_requests.adversary_phone_assets,
            'url': self.tc_requests.adversary_url_assets,
        }

        if asset_type is None:
            return self.tc_requests.adversary_assets(self.unique_id)

        # handle invalid input
        if asset_methods.get(asset_type.lower()) is None:
            self._tcex.handle_error(
                925, ['asset_type', 'assets', 'asset_type', 'asset_type', asset_type]
            )

        return asset_methods.get(asset_type.lower())(self.unique_id)

    def delete_asset(self, asset_id, asset_type):
        """Delete the asset with the provided asset_id.

        Args:
            asset_id: The id of the asset.
            asset_type: The asset type.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.asset(asset_id, asset_type=asset_type, action='DELETE')

    def delete_handle_asset(self, asset_id):
        """Delete the handle asset with the passed in id

        Args:
            asset_id: The id of the asset to be deleted

        Returns:
            requests.Response: The response from the API call.
        """
        return self.delete_asset(asset_id, 'HANDLE')

    def delete_phone_asset(self, asset_id):
        """Delete the phone asset with the passed in id

        Args:
            asset_id: The id of the asset to be deleted

        Returns:
            requests.Response: The response from the API call.
        """
        return self.delete_asset(asset_id, 'PHONE')

    def delete_url_asset(self, asset_id):
        """Delete the url asset with the passed in id

        Args:
            asset_id: The id of the asset to be deleted

        Returns:
            requests.Response: The response from the API call.
        """
        return self.delete_asset(asset_id, 'URL')

    def get_asset(self, asset_id, asset_type):
        """Get the asset with the provided asset_id & asset_type.

        Args:
            asset_id: (str) The ID of the asset.
            asset_type: (str) Either None, PHONE, HANDLE, or URL

        Returns:
            requests.Response: The response from the API call.
        """
        return self.asset(asset_id, asset_type=asset_type)

    def get_handle_asset(self, asset_id):
        """Get the handle asset with the passed in id

        Args:
            asset_id: The id of the asset.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.get_asset(asset_id, 'HANDLE')

    def get_phone_asset(self, asset_id):
        """Get the phone asset with the passed in id

        Args:
            asset_id: The id of the asset.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.get_asset(asset_id, 'PHONE')

    def get_url_asset(self, asset_id):
        """Get the url asset with the passed in id

        Args:
            asset_id: The id of the asset.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.get_asset(asset_id, 'URL')

    # def handle_asset(self, asset_id, action='GET'):
    #     """Get the handle asset with the passed in id.

    #     Args:
    #         asset_id: The id of the asset.
    #         action: (str): The HTTP method (e.g., DELETE or GET)

    #     Returns:
    #         requests.Response: The response from the API call.
    #     """
    #     return self.asset(asset_id, 'HANDLE', action=action)

    def handle_assets(self):
        """Return all of the handle assets"""
        return self.assets(asset_type='HANDLE')

    # def phone_asset(self, asset_id, action='GET'):
    #     """Get the phone asset with the passed in id.

    #     Args:
    #         asset_id: The id of the asset.
    #         action: (str): The HTTP method (e.g., DELETE or GET)

    #     Returns:
    #         requests.Response: The response from the API call.
    #     """
    #     return self.asset(asset_id, 'PHONE', action=action)

    def phone_assets(self):
        """Return all of the phone assets"""
        return self.assets(asset_type='PHONE')

    # def url_asset(self, asset_id, action='GET'):
    #     """Get the url asset with the passed in id.

    #     Args:
    #         asset_id: The id of the asset.
    #         action: (str): The HTTP method (e.g., DELETE or GET)

    #     Returns:
    #         requests.Response: The response from the API call.
    #     """
    #     return self.asset(asset_id, 'URL', action=action)

    def url_assets(self):
        """Return all of the url assets"""
        return self.assets(asset_type='URL')
