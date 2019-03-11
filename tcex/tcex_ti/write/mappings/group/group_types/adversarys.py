from tcex.tcex_ti.write.mappings.group.tcex_ti_group import Group


class Adversary(Group):
    """ThreatConnect Batch Adversary Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, name, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super(Adversary, self).__init__(tcex, 'adversaries', name, **kwargs)

    def asset(self, type, name, asset_id=None, action='CREATE'):
        return self.tc_requests.adversary_asset(self.api_type, self.api_sub_type, self.unique_id,
                                                type, name, asset_id=asset_id, action=action)

    def update_asset(self, type, name, id):
        return self.asset(type, name, asset_id=id, action='UPDATE')

    def delete_asset(self, type, name, id):
        return self.asset(type, name, asset_id=id, action='DELETE')

    def create_asset(self, type, name):
        return self.asset(type, name)

    def create_handler_asset(self, name):
        return self.create_asset('HANDLER', name)

    def update_handler_asset(self, name, id):
        return self.update_asset('HANDLER', name, id)

    def delete_handler_asset(self, name, id):
        return self.delete_asset('HANDLER', name, id)

    def create_phone_asset(self, name):
        self.create_asset('PHONE', name)

    def update_phone_asset(self, name, id):
        self.update_asset('PHONE', name, id)

    def delete_phone_asset(self, name, id):
        self.delete_asset('PHONE', name, id)

    def create_url_asset(self, name):
        self.create_asset('URL', name)

    def update_url_asset(self, name, id):
        self.update_asset('URL', name, id)

    def delete_url_asset(self, name, id):
        self.delete_asset('URL', name, id)
