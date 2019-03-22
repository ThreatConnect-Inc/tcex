# -*- coding: utf-8 -*-
"""ThreatConnect TI Adversary """
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Adversary(Group):
    """Unique API calls for Adversary API Endpoints"""

    def __init__(self, tcex, name, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
        """
        super(Adversary, self).__init__(tcex, 'adversaries', name, **kwargs)
        self.api_entity = 'adversary'

    # def add_asset(self, asset_type: object, asset_name: object) -> object:
    def add_asset(self, asset_type: str, asset_name: str) -> object:
        """
        :param asset_type:
        :param asset_name:
        :return:
        """
        if asset_type == 'PHONE':
            return self.tc_requests.add_adversary_phone_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_name
            )
        if asset_type == 'HANDLER':
            return self.tc_requests.add_adversary_handler_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_name
            )
        if asset_type == 'URL':
            return self.tc_requests.add_adversary_url_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_name
            )
        return None

    def asset(self, asset_id, asset_type, action='GET'):
        """

        :param asset_id:
        :param asset_type:
        :param action:
        :return:
        """
        if asset_type == 'PHONE':
            return self.tc_requests.adversary_phone_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_id, action=action
            )
        if asset_type == 'HANDLER':
            return self.tc_requests.adversary_handle_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_id, action=action
            )
        if asset_type == 'URL':
            return self.tc_requests.adversary_url_asset(
                self.api_type, self.api_sub_type, self.unique_id, asset_id, action=action
            )
        return None

    def assets(self, asset_type=None):
        """

        :param asset_type:
        :return:
        """
        if not asset_type:
            return self.tc_requests.adversary_assets(
                self.api_type, self.api_sub_type, self.unique_id
            )
        if asset_type == 'PHONE':
            return self.tc_requests.adversary_phone_assets(
                self.api_type, self.api_sub_type, self.unique_id
            )
        if asset_type == 'HANDLER':
            return self.tc_requests.adversary_handle_assets(
                self.api_type, self.api_sub_type, self.unique_id
            )
        if asset_type == 'URL':
            return self.tc_requests.adversary_url_assets(
                self.api_type, self.api_sub_type, self.unique_id
            )

        return None

    def get_asset(self, asset_id, asset_type):
        """

        :param asset_id:
        :param asset_type:
        :return:
        """
        return self.asset(asset_id, asset_type=asset_type)

    def delete_asset(self, asset_id, asset_type):
        """

        :param asset_id:
        :param asset_type:
        :return:
        """
        return self.asset(asset_id, asset_type=asset_type, action='DELETE')

    def handle_assets(self):
        """

        :return:
        """
        return self.assets(asset_type='HANDLER')

    def phone_assets(self):
        """

        :return:
        """
        return self.assets(asset_type='PHONE')

    def url_assets(self):
        """

        :return:
        """
        return self.assets(asset_type='URL')

    def handle_asset(self, asset_id, action='GET'):
        """

        :return:
        """
        return self.asset(asset_id, 'HANDLER', action=action)

    def phone_asset(self, asset_id, action='GET'):
        """

        :return:
        """
        return self.asset(asset_id, 'PHONE', action=action)

    def url_asset(self, asset_id, action='GET'):
        """

        :return:
        """
        return self.asset(asset_id, 'URL', action=action)

    def get_handle_asset(self, asset_id):
        """

        :return:
        """
        return self.get_asset(asset_id, 'HANDLER')

    def get_phone_asset(self, asset_id):
        """

        :return:
        """
        return self.get_asset(asset_id, 'PHONE')

    def get_url_asset(self, asset_id):
        """

        :return:
        """
        return self.get_asset(asset_id, 'URL')

    def delete_phone_asset(self, asset_id):
        """

        :return:
        """
        return self.delete_asset(asset_id, 'PHONE')

    def delete_url_asset(self, asset_id):
        """

        :return:
        """
        return self.delete_asset(asset_id, 'URL')

    def delete_handler_asset(self, asset_id):
        """

        :return:
        """
        return self.delete_asset(asset_id, 'HANDLER')

    def add_handler_asset(self, name):
        """

        :return:
        """
        return self.add_asset('HANDLER', name)

    def add_phone_asset(self, name):
        """

        :return:
        """
        self.add_asset('PHONE', name)

    def add_url_asset(self, name):
        """

        :return:
        """
        self.add_asset('URL', name)
