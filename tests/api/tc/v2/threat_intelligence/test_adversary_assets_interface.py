"""Test the TcEx Threat Intel Module."""
# standard library
import os
import random

from .ti_helpers import TestThreatIntelligence, TIHelper


class TestAdversaryAssets(TestThreatIntelligence):
    """Test TcEx Adversary Assets."""

    group_type = 'Adversary'
    owner = os.getenv('TC_OWNER')
    ti = None
    ti_helper = None
    tcex = None

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.group_type)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.ti_helper.cleanup()

    def tests_ti_groups_to_indicators(self):
        """Test the TI module."""
        helper_ti = self.ti_helper.create_group()
        rand_ip = self.ti_helper.rand_ip()
        indicator_kwargs = {
            'ip': rand_ip,
            'rating': random.randint(0, 5),
            'confidence': random.randint(0, 100),
        }
        indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
        indicator.create()
        helper_ti.add_association(indicator)
        found = False
        for indicator in helper_ti.indicator_associations():
            if indicator.get('summary') == rand_ip:
                found = True
        assert found, 'Failed to retrieve indicator associations from group.'

    def tests_ti_adversary_add_asset_handle(self):
        """Add an asset to and Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        r = helper_ti.add_handle_asset(self.ti_helper.rand_email_address())

        # assert response
        assert r.status_code == 201

    def tests_ti_adversary_add_asset_phone(self):
        """Add an asset to and Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        r = helper_ti.add_phone_asset(self.ti_helper.rand_phone_number())

        # assert response
        assert r.status_code == 201

    def tests_ti_adversary_add_asset_url(self):
        """Add an asset to and Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        r = helper_ti.add_url_asset(self.ti_helper.rand_url())

        # assert response
        assert r.status_code == 201

    def tests_ti_adversary_add_asset_invalid_type(self):
        """Test passing a bad asset type."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        try:
            asset_type = 'invalid type'
            helper_ti.add_asset(asset_type, None)
            assert False, f'invalid asset type of {asset_type} not caught'
        except RuntimeError:
            assert True, 'caught invalid asset type'

    def tests_ti_adversary_add_asset_no_update(self):
        """Test passing a bad asset type."""
        ti = self.ti.adversary(name='new')

        # add asset
        try:
            ti.add_asset('phone', self.ti_helper.rand_phone_number())
            assert False, 'failed to catch update on an adversary with no id.'
        except RuntimeError:
            assert True, 'caught update call on an adversary with no id'

    def tests_ti_adversary_asset(self):
        """Add an asset to and Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        r = helper_ti.add_phone_asset(self.ti_helper.rand_phone_number())
        response_data = r.json()
        ti_data = response_data.get('data', {}).get('adversaryPhoneNumber')

        # assert response
        assert r.status_code == 201
        assert response_data.get('status') == 'Success'

        # Get asset
        r = helper_ti.asset(ti_data.get('id'), 'phone')

    def tests_ti_adversary_delete_asset_handle(self):
        """Add an asset to and Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        r = helper_ti.add_handle_asset(self.ti_helper.rand_email_address())
        response_data = r.json()
        asset_id = response_data.get('data', {}).get('adversaryHandle', {}).get('id')

        # delete asset
        r = helper_ti.delete_handle_asset(asset_id)

        # assert response
        assert r.status_code == 200

    def tests_ti_adversary_delete_asset_phone(self):
        """Add an asset to and Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        r = helper_ti.add_phone_asset(self.ti_helper.rand_phone_number())
        response_data = r.json()
        asset_id = response_data.get('data', {}).get('adversaryPhoneNumber', {}).get('id')

        # delete assets
        r = helper_ti.delete_phone_asset(asset_id)

        # assert response
        assert r.status_code == 200

    def tests_ti_adversary_delete_asset_url(self):
        """Add an asset to and Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        r = helper_ti.add_url_asset(self.ti_helper.rand_url())
        response_data = r.json()
        asset_id = response_data.get('data', {}).get('adversaryUrl', {}).get('id')

        # delete asset
        r = helper_ti.delete_url_asset(asset_id)

        # assert response
        assert r.status_code == 200

    def tests_ti_adversary_get_asset_no_update(self):
        """Add an asset to and Adversary."""
        ti = self.ti.adversary(name='new')

        # add asset
        try:
            ti.asset('phone', self.ti_helper.rand_phone_number())
            assert False, 'failed to catch get on an adversary with no id.'
        except RuntimeError:
            assert True, 'caught get call on an adversary with no id'

    def tests_ti_adversary_get_asset_invalid_type(self):
        """Add an asset to and Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        try:
            asset_type = 'invalid type'
            helper_ti.asset('123', asset_type)
            assert False, f'invalid asset type of {asset_type} not caught'
        except RuntimeError:
            assert True, 'caught invalid asset type'

    def tests_ti_adversary_get_asset_handle(self):
        """Add an asset to and Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        r = helper_ti.add_handle_asset(self.ti_helper.rand_email_address())
        response_data = r.json()
        asset_id = response_data.get('data', {}).get('adversaryHandle', {}).get('id')

        # get asset
        r = helper_ti.get_handle_asset(asset_id)

        # assert response
        assert r.status_code == 200

    def tests_ti_adversary_get_asset_phone(self):
        """Get an asset from an Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        r = helper_ti.add_phone_asset(self.ti_helper.rand_phone_number())
        response_data = r.json()
        asset_id = response_data.get('data', {}).get('adversaryPhoneNumber', {}).get('id')

        # get asset
        r = helper_ti.get_phone_asset(asset_id)

        # assert response
        assert r.status_code == 200

    def tests_ti_adversary_get_asset_url(self):
        """Get an asset from an Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        r = helper_ti.add_url_asset(self.ti_helper.rand_url())
        response_data = r.json()
        asset_id = response_data.get('data', {}).get('adversaryUrl', {}).get('id')

        # get asset
        r = helper_ti.get_url_asset(asset_id)

        # assert response
        assert r.status_code == 200

    def tests_ti_adversary_get_asset_handles(self):
        """Get an asset from an Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        asset = self.ti_helper.rand_email_address()
        helper_ti.add_handle_asset(asset)

        # get assets
        for a in helper_ti.handle_assets():
            if a.get('handle') == asset:
                break
        else:
            assert False, 'Handle asset not found.'

    def tests_ti_adversary_get_asset_phones(self):
        """Get an asset from an Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        asset = self.ti_helper.rand_phone_number()
        helper_ti.add_phone_asset(asset)

        # get assets
        for a in helper_ti.phone_assets():
            if a.get('phoneNumber') == asset:
                break
        else:
            assert False, 'Phone asset not found.'

    def tests_ti_adversary_get_asset_urls(self):
        """Get an asset from an Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        asset = self.ti_helper.rand_url()
        helper_ti.add_url_asset(asset)

        # get assets
        for a in helper_ti.url_assets():
            if a.get('url') == asset:
                break
        else:
            assert False, 'URL asset not found.'

    def tests_ti_adversary_get_assets(self):
        """Get an asset from an Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        asset = self.ti_helper.rand_url()
        helper_ti.add_url_asset(asset)

        # get assets
        for a in helper_ti.assets():
            # at the generic level the asset bucket is "bucketAsset" and field is "name"
            if a.get('name') == asset:
                break
        else:
            assert False, 'URL asset not found.'

    def tests_ti_adversary_get_assets_invalid_type(self):
        """Get an asset from an Adversary."""
        helper_ti = self.ti_helper.create_group()

        # add asset
        asset = self.ti_helper.rand_url()
        helper_ti.add_url_asset(asset)

        # get assets
        try:
            asset_type = 'invalid type'
            for a in helper_ti.assets(asset_type=asset_type):
                assert a
            assert False, f'invalid asset type of {asset_type} not caught'
        except RuntimeError:
            assert True, 'caught invalid asset type'

    def tests_ti_adversary_get_assets_no_update(self):
        """Test passing a bad asset type."""
        ti = self.ti.adversary(name='new')

        # get assets
        try:
            for a in ti.assets():
                assert a
            assert False, 'failed to catch update on an adversary with no id.'
        except RuntimeError:
            assert True, 'caught update call on an adversary with no id'
