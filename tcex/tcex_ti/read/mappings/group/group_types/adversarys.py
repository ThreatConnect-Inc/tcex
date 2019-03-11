from tcex.tcex_ti.write.mappings.group.tcex_ti_group import Group

class Adversary(Group):
    """ThreatConnect Batch Adversary Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, unique_id=None):
        super(Adversary, self).__init__(tcex, 'adversaries', unique_id=unique_id)

    def adversary_assets(self, asset_type=None, **kwargs):
        if not self._data.get('unique_id', None):
            return

        return self._tc_requests.adversary_assets(self.api_type, self.api_sub_type, self.unique_id, asset_type, kwargs)

    def adversary_phone_assets(self, **kwargs):
        return self.adversary_assets(asset_type='PHONE', **kwargs)

    def adversary_handles_assets(self, **kwargs):
        return self.adversary_assets(asset_type='HANDLER', **kwargs)

    def adversary_url_assets(self, **kwargs):
        return self.adversary_assets(asset_type='URL', **kwargs)
