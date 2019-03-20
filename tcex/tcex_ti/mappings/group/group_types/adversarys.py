from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Adversary(Group):
    """ThreatConnect Batch Adversary Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, name, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was addd.
            xid (str, kwargs): The external id for this Group.
        """
        super(Adversary, self).__init__(tcex, 'adversaries', name, **kwargs)
        self.api_entity = 'adversary'

    def add_asset(self, type, asset_name):
        if type == 'PHONE':
            return self.tc_requests.add_adversary_phone_asset(self.api_type, self.api_sub_type, self.unique_id, asset_name)
        if type == 'HANDLER':
            return self.tc_requests.add_adversary_handler_asset(self.api_type, self.api_sub_type, self.unique_id, asset_name)
        if type == 'URL':
            return self.tc_requests.add_adversary_url_asset(self.api_type, self.api_sub_type, self.unique_id, asset_name)

    def asset(self, asset_id, type, action='GET'):
        if type == 'PHONE':
            return self.tc_requests.adversary_phone_asset(self.api_type, self.api_sub_type, self.unique_id,
                                                          asset_id, action=action)
        if type == 'HANDLER':
            return self.tc_requests.adversary_handle_asset(self.api_type, self.api_sub_type, self.unique_id,
                                                          asset_id, action=action)
        if type == 'URL':
            return self.tc_requests.adversary_url_asset(self.api_type, self.api_sub_type, self.unique_id,
                                                           asset_id, action=action)

    def assets(self, type=None):
        if not type:
            return self.tc_requests.adversary_assets(self.api_type, self.api_sub_type, self.unique_id)
        if type == 'PHONE':
            return self.tc_requests.adversary_phone_assets(self.api_type, self.api_sub_type, self.unique_id)
        if type == 'HANDLER':
            return self.tc_requests.adversary_handle_assets(self.api_type, self.api_sub_type, self.unique_id)
        if type == 'URL':
            return self.tc_requests.adversary_url_assets(self.api_type, self.api_sub_type, self.unique_id)

        return None

    def get_asset(self, asset_id, type):
        return self.asset(asset_id, type=type)

    def delete_asset(self, asset_id, type):
        return self.asset(asset_id, type=type, action='DELETE')

    def handle_assets(self):
        return self.assets(type='HANDLER')

    def phone_assets(self):
        return self.assets(type='PHONE')

    def url_assets(self):
        return self.assets(type='URL')

    def handle_asset(self, asset_id, action='GET'):
        return self.asset(asset_id, 'HANDLER', action=action)

    def phone_asset(self, asset_id, action='GET'):
        return self.asset(asset_id, 'PHONE', action=action)

    def url_asset(self, asset_id, action='GET'):
        return self.asset(asset_id, 'URL', action=action)

    def get_handle_asset(self, asset_id):
        return self.get_asset(asset_id, 'HANDLER')

    def get_phone_asset(self, asset_id):
        return self.get_asset(asset_id, 'PHONE')

    def get_url_asset(self, asset_id):
        return self.get_asset(asset_id, 'URL')

    def delete_phone_asset(self, asset_id):
        return self.delete_asset(asset_id, 'PHONE')

    def delete_url_asset(self, asset_id):
        return self.delete_asset(asset_id, 'URL')

    def delete_handler_asset(self, asset_id):
        return self.delete_asset(asset_id, 'HANDLER')

    def add_handler_asset(self, name):
        return self.add_asset('HANDLER', name)

    def add_phone_asset(self, name):
        self.add_asset('PHONE', name)

    def add_url_asset(self, name):
        self.add_asset('URL', name)

