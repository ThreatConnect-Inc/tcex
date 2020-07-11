# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os
from .ti_helpers import TIHelper, TestThreatIntelligence


class TestVictim(TestThreatIntelligence):
    """Test TcEx Threat Groups."""

    owner = os.getenv('TC_OWNER')
    ti = None
    ti_helper = None
    tcex = None

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper('Victim')
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.ti_helper.cleanup()

    def tests_ti_victim_create(self):
        """Create a victim using specific interface."""
        victim_data = {
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.victim(**victim_data)
        ti.name = victim_data.get('name')
        r = ti.create()
        assert ti.as_entity

        # assert response
        assert r.status_code == 201

        # retrieve victim for asserts
        victim_data['unique_id'] = ti.unique_id
        ti = self.ti.victim(**victim_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'
        assert ti.name == ti_data.get('name')

        # validate ti data
        assert ti_data.get(ti.api_entity) == victim_data.get(ti.api_entity)

        # cleanup victim
        r = ti.delete()
        assert r.status_code == 200

    def tests_ti_victim_add_email_asset(self):
        """Test victim add email asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_email_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        assert r.status_code == 201

    def tests_ti_victim_add_network_asset(self):
        """Test victim add network asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_network_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        assert r.status_code == 201

    def tests_ti_victim_add_phone_asset(self):
        """Test victim add phone asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_phone_asset(self.ti_helper.rand_phone_number())
        assert r.status_code == 201

    def tests_ti_victim_add_social_asset(self):
        """Test victim add social asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_social_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        assert r.status_code == 201

    def tests_ti_victim_add_web_asset(self):
        """Test victim add web asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_web_asset(self.ti_helper.rand_name())
        assert r.status_code == 201

    def tests_ti_victim_delete_email_asset(self):
        """Test victim delete email asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_email_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimEmailAddress', {}).get('id')
        r = helper_ti.delete_email_asset(asset_id)
        assert r.status_code == 200

    def tests_ti_victim_delete_network_asset(self):
        """Test victim delete network asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_network_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimNetworkAccount', {}).get('id')
        r = helper_ti.delete_network_asset(asset_id)
        assert r.status_code == 200

    def tests_ti_victim_delete_phone_asset(self):
        """Test victim delete phone asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_phone_asset(self.ti_helper.rand_phone_number())
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimPhone', {}).get('id')
        r = helper_ti.delete_phone_asset(asset_id)
        assert r.status_code == 200

    def tests_ti_victim_delete_social_asset(self):
        """Test victim delete social asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_social_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimSocialNetwork', {}).get('id')
        r = helper_ti.delete_social_asset(asset_id)
        assert r.status_code == 200

    def tests_ti_victim_delete_web_asset(self):
        """Test victim delete web asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_web_asset(self.ti_helper.rand_name())
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimWebSite', {}).get('id')
        r = helper_ti.delete_web_asset(asset_id)
        assert r.status_code == 200

    def tests_ti_victim_get_email_asset(self):
        """Test victim get email asset."""
        helper_ti = self.ti_helper.create_victim()

        address = self.ti_helper.rand_name()
        address_type = self.ti_helper.rand_name()
        r = helper_ti.add_email_asset(address, address_type)
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimEmailAddress', {}).get('id')
        r = helper_ti.get_email_asset(asset_id)
        assert r.status_code == 200
        asset_json = r.json().get('data', {}).get('victimEmailAddress', {})
        assert asset_json.get('address') == address
        assert asset_json.get('addressType') == address_type

    def tests_ti_victim_get_network_asset(self):
        """Test victim get network asset."""
        helper_ti = self.ti_helper.create_victim()

        account = self.ti_helper.rand_name()
        network = self.ti_helper.rand_name()
        r = helper_ti.add_network_asset(account, network)
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimNetworkAccount', {}).get('id')
        r = helper_ti.get_network_asset(asset_id)
        assert r.status_code == 200
        asset_json = r.json().get('data', {}).get('victimNetworkAccount', {})
        assert asset_json.get('account') == account
        assert asset_json.get('network') == network

    def tests_ti_victim_get_phone_asset(self):
        """Test victim get phone asset."""
        helper_ti = self.ti_helper.create_victim()

        phone_number = self.ti_helper.rand_phone_number()
        r = helper_ti.add_phone_asset(phone_number)
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimPhone', {}).get('id')
        r = helper_ti.get_phone_asset(asset_id)
        assert r.status_code == 200
        asset_json = r.json().get('data', {}).get('victimPhone', {})
        assert asset_json.get('phoneType') == phone_number

    def tests_ti_victim_get_social_asset(self):
        """Test victim get social asset."""
        helper_ti = self.ti_helper.create_victim()

        account = self.ti_helper.rand_name()
        network = self.ti_helper.rand_name()
        r = helper_ti.add_social_asset(account, network)
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimSocialNetwork', {}).get('id')
        r = helper_ti.get_social_asset(asset_id)
        assert r.status_code == 200
        asset_json = r.json().get('data', {}).get('victimSocialNetwork', {})
        assert asset_json.get('account') == account
        assert asset_json.get('network') == network

    def tests_ti_victim_get_web_asset(self):
        """Test victim get web asset."""
        helper_ti = self.ti_helper.create_victim()

        web_site = self.ti_helper.rand_name()
        r = helper_ti.add_web_asset(web_site)
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimWebSite', {}).get('id')
        r = helper_ti.get_web_asset(asset_id)
        assert r.status_code == 200
        asset_json = r.json().get('data', {}).get('victimWebSite', {})
        assert asset_json.get('webSite') == web_site

    def tests_ti_victim_update_email_asset(self):
        """Test victim update email asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_email_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimEmailAddress', {}).get('id')
        address = self.ti_helper.rand_name()
        address_type = self.ti_helper.rand_name()
        r = helper_ti.update_email_asset(asset_id, address, address_type)
        assert r.status_code == 200
        asset_json = r.json().get('data', {}).get('victimEmailAddress', {})
        assert asset_json.get('address') == address
        assert asset_json.get('addressType') == address_type

    def tests_ti_victim_update_network_asset(self):
        """Test victim update network asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_network_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimNetworkAccount', {}).get('id')
        account = self.ti_helper.rand_name()
        network = self.ti_helper.rand_name()
        r = helper_ti.update_network_asset(asset_id, account, network)
        assert r.status_code == 200
        asset_json = r.json().get('data', {}).get('victimNetworkAccount', {})
        assert asset_json.get('account') == account
        assert asset_json.get('network') == network

    def tests_ti_victim_update_phone_asset(self):
        """Test victim update phone asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_phone_asset(self.ti_helper.rand_phone_number())
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimPhone', {}).get('id')
        phone_type = self.ti_helper.rand_phone_number()
        r = helper_ti.update_phone_asset(asset_id, phone_type)
        assert r.status_code == 200
        asset_json = r.json().get('data', {}).get('victimPhone', {})
        assert asset_json.get('phoneType') == phone_type

    def tests_ti_victim_update_social_asset(self):
        """Test victim update social asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_social_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimSocialNetwork', {}).get('id')
        account = self.ti_helper.rand_name()
        network = self.ti_helper.rand_name()
        r = helper_ti.update_social_asset(asset_id, account, network)
        assert r.status_code == 200
        asset_json = r.json().get('data', {}).get('victimSocialNetwork', {})
        assert asset_json.get('account') == account
        assert asset_json.get('network') == network

    def tests_ti_victim_update_web_asset(self):
        """Test victim update web asset."""
        helper_ti = self.ti_helper.create_victim()

        r = helper_ti.add_web_asset(self.ti_helper.rand_name())
        assert r.status_code == 201

        asset_id = r.json().get('data', {}).get('victimWebSite', {}).get('id')
        web_site = self.ti_helper.rand_name()
        r = helper_ti.update_web_asset(asset_id, web_site)
        assert r.status_code == 200
        asset_json = r.json().get('data', {}).get('victimWebSite', {})
        assert asset_json.get('webSite') == web_site

    def tests_ti_victim_get_web_assets(self):
        """Test victim get web assets."""
        helper_ti = self.ti_helper.create_victim()
        web_asset_names = [self.ti_helper.rand_name(), self.ti_helper.rand_name()]
        helper_ti.add_web_asset(web_asset_names[0])
        helper_ti.add_web_asset(web_asset_names[1])

        counter = 0
        for asset in helper_ti.web_assets():
            assert asset.get('name') in web_asset_names
            web_asset_names.remove(asset.get('name'))
            counter += 1
        assert counter == 2

    def tests_ti_victim_get_phone_assets(self):
        """Test victim get phone assets."""
        helper_ti = self.ti_helper.create_victim()
        phone_types = [self.ti_helper.rand_name(), self.ti_helper.rand_name()]
        helper_ti.add_phone_asset(phone_types[0])
        helper_ti.add_phone_asset(phone_types[1])

        counter = 0
        for asset in helper_ti.phone_assets():
            assert asset.get('name') in phone_types
            phone_types.remove(asset.get('name'))
            counter += 1
        assert counter == 2

    def tests_ti_victim_get_email_assets(self):
        """Test victim get email assets."""
        helper_ti = self.ti_helper.create_victim()
        addresses = [self.ti_helper.rand_name(), self.ti_helper.rand_name()]
        helper_ti.add_email_asset(addresses[0], self.ti_helper.rand_name())
        helper_ti.add_email_asset(addresses[1], self.ti_helper.rand_name())

        counter = 0
        for asset in helper_ti.email_assets():
            assert asset.get('name') in addresses
            addresses.remove(asset.get('name'))
            counter += 1
        assert counter == 2

    def tests_ti_victim_get_network_assets(self):
        """Test victim get network assets."""
        helper_ti = self.ti_helper.create_victim()
        accounts = [self.ti_helper.rand_name(), self.ti_helper.rand_name()]
        helper_ti.add_network_asset(accounts[0], self.ti_helper.rand_name())
        helper_ti.add_network_asset(accounts[1], self.ti_helper.rand_name())

        counter = 0
        for asset in helper_ti.network_assets():
            assert asset.get('name') in accounts
            accounts.remove(asset.get('name'))
            counter += 1
        assert counter == 2

    def tests_ti_victim_get_social_assets(self):
        """Test victim get social assets."""
        helper_ti = self.ti_helper.create_victim()
        accounts = [self.ti_helper.rand_name(), self.ti_helper.rand_name()]
        helper_ti.add_social_asset(accounts[0], self.ti_helper.rand_name())
        helper_ti.add_social_asset(accounts[1], self.ti_helper.rand_name())

        counter = 0
        for asset in helper_ti.social_assets():
            assert asset.get('name') in accounts
            accounts.remove(asset.get('name'))
            counter += 1
        assert counter == 2

    def tests_ti_victim_get_assets(self):
        """Test victim get all assets."""
        helper_ti = self.ti_helper.create_victim()
        helper_ti.add_web_asset(self.ti_helper.rand_name())
        helper_ti.add_web_asset(self.ti_helper.rand_name())

        helper_ti.add_social_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        helper_ti.add_social_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())

        helper_ti.add_network_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        helper_ti.add_network_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())

        helper_ti.add_email_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())
        helper_ti.add_email_asset(self.ti_helper.rand_name(), self.ti_helper.rand_name())

        helper_ti.add_phone_asset(self.ti_helper.rand_name())
        helper_ti.add_phone_asset(self.ti_helper.rand_name())

        counter = 0
        for asset in helper_ti.assets():
            assert str(helper_ti.unique_id) in asset.get('webLink')
            counter += 1
        assert counter == 10

    def tests_ti_victim_add_asset_invalid(self):
        """Test victim fail on add asset with before victim has been created."""
        helper_ti = self.ti.victim(name=self.ti_helper.rand_name())
        try:
            helper_ti.add_phone_asset(self.ti_helper.rand_name())
            assert False, 'failed to catch add asset on an victim with no id.'
        except RuntimeError:
            assert True, 'caught add asset on an victim with no id.'

    def tests_ti_victim_delete_asset_invalid(self):
        """Test victim fail on delete asset with before victim has been created."""
        helper_ti = self.ti.victim(name=self.ti_helper.rand_name())
        try:
            helper_ti.delete_phone_asset(1)
            assert False, 'failed to catch delete asset on an victim with no id.'
        except RuntimeError:
            assert True, 'caught add asset on an victim with no id.'

    def tests_ti_victim_add_asset_no_body(self):
        """Test victim return error on add asset with no body."""
        helper_ti = self.ti_helper.create_victim()
        r = helper_ti.add_asset('phone', None)
        assert r.status_code == 400

    def tests_ti_victim_add_asset_no_type_invalid(self):
        """Test victim fail on add asset with no asset type."""
        helper_ti = self.ti_helper.create_victim()
        try:
            helper_ti.add_asset(
                None,
                {'address': self.ti_helper.rand_name(), 'addressType': self.ti_helper.rand_name()},
            )
            assert False, 'failed to catch add asset on an victim with no type.'
        except RuntimeError:
            assert True, 'caught add asset on an victim with no type.'

    def tests_ti_victim_delete_asset_no_type_invalid(self):
        """Test victim fail on delete asset with no asset type."""
        helper_ti = self.ti_helper.create_victim()
        try:
            helper_ti.delete_asset(1, None)
            assert False, 'failed to catch delete asset on an victim with no type.'
        except RuntimeError:
            assert True, 'caught delete asset on an victim with no type.'

    def tests_ti_victim_get_assets_invalid(self):
        """Test victim fail on get assets when no victim id is present."""
        helper_ti = self.ti.victim(name=self.ti_helper.rand_name())
        try:
            helper_ti.assets()
            assert False, 'failed to catch get assets on an victim with no id.'
        except RuntimeError:
            assert True, 'caught get assets on an victim with no id.'

    def tests_ti_victim_get_asset_invalid(self):
        """Test victim fail on get asset when no victim id is present."""
        helper_ti = self.ti.victim(name=self.ti_helper.rand_name())
        try:
            helper_ti.get_phone_asset(1)
            assert False, 'failed to catch get asset on an victim with no id.'
        except RuntimeError:
            assert True, 'caught get asset on an victim with no id.'

    def tests_ti_victim_get_asset_no_type_invalid(self):
        """Test victim fail on get asset with no asset type."""
        helper_ti = self.ti_helper.create_victim()
        try:
            helper_ti.get_asset(1, None)
            assert False, 'failed to catch get asset on an victim with no id.'
        except RuntimeError:
            assert True, 'caught get asset on an victim with no id.'

    def tests_ti_victim_update_asset_no_body(self):
        """Test victim error on update asset with no body."""
        helper_ti = self.ti_helper.create_victim()
        r = helper_ti.add_phone_asset(self.ti_helper.rand_name())
        asset_id = r.json().get('data', {}).get('victimPhone', {}).get('id')
        r = helper_ti.update_asset('phone', asset_id)
        assert r.status_code == 400

    def tests_ti_victim_update_asset_no_type_invalid(self):
        """Test victim fail on update asset with no asset type."""
        helper_ti = self.ti_helper.create_victim()
        try:
            helper_ti.update_asset(None, None)
            assert False, 'failed to catch update asset on an victim with no type.'
        except RuntimeError:
            assert True, 'caught update asset on an victim with no type.'
