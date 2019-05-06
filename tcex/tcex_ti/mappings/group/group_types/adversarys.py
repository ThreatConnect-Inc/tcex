# -*- coding: utf-8 -*-
"""ThreatConnect TI Adversary """
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Adversary(Group):
    """Unique API calls for Adversary API Endpoints"""

    def __init__(self, tcex, name, owner=None, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
        """
        super(Adversary, self).__init__(
            tcex, 'Adversary', 'adversary', 'adversaries', name, owner, **kwargs
        )

    def add_asset(self, asset_type, asset_name):
        """
        Add an asset to the adversary
        Args:
            asset_type: (str) Either PHONE, HANDLER, or URL
            asset_name: (str) the value for the asset

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if asset_type == 'PHONE':
            return self.tc_requests.add_adversary_phone_asset(
                self.api_type, self.api_branch, self.unique_id, asset_name
            )
        if asset_type == 'HANDLER':
            return self.tc_requests.add_adversary_handler_asset(
                self.api_type, self.api_branch, self.unique_id, asset_name
            )
        if asset_type == 'URL':
            return self.tc_requests.add_adversary_url_asset(
                self.api_type, self.api_branch, self.unique_id, asset_name
            )
        self._tcex.handle_error(
            925, ['asset_type', 'assets', 'asset_type', 'asset_type', asset_type]
        )
        return None

    def asset(self, asset_id, asset_type, action='GET'):
        """
        Gets the asset with the provided id
        Args:
            asset_id: The id of the asset to be retrieved
            asset_type: (str) Either PHONE, HANDLER, or URL
            action:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if asset_type == 'PHONE':
            return self.tc_requests.adversary_phone_asset(
                self.api_type, self.api_branch, self.unique_id, asset_id, action=action
            )
        if asset_type == 'HANDLER':
            return self.tc_requests.adversary_handle_asset(
                self.api_type, self.api_branch, self.unique_id, asset_id, action=action
            )
        if asset_type == 'URL':
            return self.tc_requests.adversary_url_asset(
                self.api_type, self.api_branch, self.unique_id, asset_id, action=action
            )
        self._tcex.handle_error(
            925, ['asset_type', 'assets', 'asset_type', 'asset_type', asset_type]
        )
        return None

    def assets(self, asset_type=None):
        """
        Retrieves all of the assets of a given asset_type

        Args:
            asset_type: (str) Either None, PHONE, HANDLER, or URL

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        if not asset_type:
            return self.tc_requests.adversary_assets(self.api_type, self.api_branch, self.unique_id)
        if asset_type == 'PHONE':
            return self.tc_requests.adversary_phone_assets(
                self.api_type, self.api_branch, self.unique_id
            )
        if asset_type == 'HANDLER':
            return self.tc_requests.adversary_handle_assets(
                self.api_type, self.api_branch, self.unique_id
            )
        if asset_type == 'URL':
            return self.tc_requests.adversary_url_assets(
                self.api_type, self.api_branch, self.unique_id
            )

        self._tcex.handle_error(
            925, ['asset_type', 'assets', 'asset_type', 'asset_type', asset_type]
        )
        return None

    def get_asset(self, asset_id, asset_type):
        """
        Gets the asset with the provided asset_id & asset_type.

        Args:
            asset_id: The id of the asset.
            asset_type: The asset type.

        Returns:

        """
        return self.asset(asset_id, asset_type=asset_type)

    def delete_asset(self, asset_id, asset_type):
        """
        Delete the asset with the provided asset_id.

        Args:
            asset_id: The id of the asset.
            asset_type: The asset type.

        Returns:

        """
        return self.asset(asset_id, asset_type=asset_type, action='DELETE')

    def handle_assets(self):
        """

        Returns: all of the handle assets

        """
        return self.assets(asset_type='HANDLER')

    def phone_assets(self):
        """

        Returns: all of the phone assets

        """
        return self.assets(asset_type='PHONE')

    def url_assets(self):
        """

        Returns: all of the url assets

        """
        return self.assets(asset_type='URL')

    def handle_asset(self, asset_id, action='GET'):
        """
        Gets the phone asset with the passed in id.

        Args:
            asset_id: The id  of the asset to be retrieved
            action:

        Returns:

        """
        return self.asset(asset_id, 'HANDLER', action=action)

    def phone_asset(self, asset_id, action='GET'):
        """
        Gets the phone asset with the passed in id.

        Args:
            asset_id: The id  of the asset to be retrieved
            action:

        Returns:

        """
        return self.asset(asset_id, 'PHONE', action=action)

    def url_asset(self, asset_id, action='GET'):
        """
        Gets the url asset with the passed in id.

        Args:
            asset_id: The id  of the asset to be retrieved
            action:

        Returns:

        """
        return self.asset(asset_id, 'URL', action=action)

    def get_handle_asset(self, asset_id):
        """
        Gets the handle asset with the passed in id

        Args:
            asset_id: The id  of the asset to be retrieved

        Returns:

        """
        return self.get_asset(asset_id, 'HANDLER')

    def get_phone_asset(self, asset_id):
        """
        Gets the phone asset with the passed in id

        Args:
            asset_id: The id  of the asset to be retrieved

        Returns:

        """
        return self.get_asset(asset_id, 'PHONE')

    def get_url_asset(self, asset_id):
        """
        Gets the url asset with the passed in id

        Args:
            asset_id: The id  of the asset to be retrieved

        Returns:

        """
        return self.get_asset(asset_id, 'URL')

    def delete_phone_asset(self, asset_id):
        """
        Delete the phone asset with the passed in id

        Args:
            asset_id: The id of the asset to be deleted

        Returns:

        """
        return self.delete_asset(asset_id, 'PHONE')

    def delete_url_asset(self, asset_id):
        """
        Delete the url asset with the passed in id

        Args:
            asset_id: The id of the asset to be deleted

        Returns:

        """
        return self.delete_asset(asset_id, 'URL')

    def delete_handler_asset(self, asset_id):
        """
        Delete the handler asset with the passed in id

        Args:
            asset_id: The id of the asset to be deleted

        Returns:

        """
        return self.delete_asset(asset_id, 'HANDLER')

    def add_handler_asset(self, name):
        """
        Add a Handler asset to the adversary.

        Args:
            name: The name of the Handler asset

        Returns:

        """
        return self.add_asset('HANDLER', name)

    def add_phone_asset(self, name):
        """
        Add a phone asset to the adversary.

        Args:
            name: The name of the phone asset

        Returns:

        """
        self.add_asset('PHONE', name)

    def add_url_asset(self, name):
        """
        Add a URL asset to the adversary.

        Args:
            name: The name of the URL asset

        Returns:

        """
        self.add_asset('URL', name)
