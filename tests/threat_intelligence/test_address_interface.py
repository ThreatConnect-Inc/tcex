# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os
from random import randint

from .ti_helpers import TIHelper, TestThreatIntelligence


class TestAddressIndicators(TestThreatIntelligence):
    """Test TcEx Address Indicators."""

    api_entity = 'address'
    api_branch = 'addresses'
    indicator_field = 'ip'
    indicator_type = 'Address'
    owner = os.getenv('TC_OWNER')
    ti = None
    ti_helper = None
    tcex = None

    def setup_class(self):
        """Configure setup before all tests."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.indicator_type, self.indicator_field)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.ti_helper.cleanup()

    def tests_ti_address_create_indicator_generic(self):
        """Create an address indicator using generic interface."""
        indicator_data = {
            'confidence': 100,
            'ip': f'222.{randint(0,255)}.{randint(0,255)}.{randint(0,255)}',
            'indicator_type': 'Address',
            'owner': self.owner,
            'rating': 5,
        }
        ti = self.ti.indicator(**indicator_data)
        r = ti.create()

        # assert response
        assert r.status_code == 201

        # retrieve indicator for asserts
        ti = self.ti.address(**indicator_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get('address')

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('confidence') == indicator_data.get('confidence')
        assert ti_data.get('ip') == indicator_data.get('ip')
        assert ti_data.get('rating') == indicator_data.get('rating')

        # cleanup indicator
        r = ti.delete()
        assert r.status_code == 200

    def tests_ti_address_create(self):
        """Create an address indicator using specific interface."""
        indicator_data = {
            'confidence': 100,
            'ip': f'222.{randint(0,255)}.{randint(0,255)}.{randint(0,255)}',
            'owner': self.owner,
            'rating': 5,
        }
        ti = self.ti.address(**indicator_data)
        r = ti.create()

        # assert response
        assert r.status_code == 201

        # retrieve indicator for asserts
        ti = self.ti.address(**indicator_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get('address')

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('confidence') == indicator_data.get('confidence')
        assert ti_data.get('ip') == indicator_data.get('ip')
        assert ti_data.get('rating') == indicator_data.get('rating')

        # cleanup indicator
        r = ti.delete()
        assert r.status_code == 200

    def tests_ti_address_add_attribute(self, request):
        """Create an attribute on an address indicator.

        Args:
            request (fixture): The pytest request fixture.
        """
        helper_ti = self.ti_helper.create_indicator()

        attribute_data = {
            'attribute_type': 'Description',
            'attribute_value': request.node.name,
            'source': request.node.name,
            'displayed': True,
        }
        r = helper_ti.add_attribute(**attribute_data)
        response_data = r.json()
        ti_data = response_data.get('data', {}).get('attribute')

        # assert response
        assert r.status_code == 201
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('type') == attribute_data.get('attribute_type')
        assert ti_data.get('value') == attribute_data.get('attribute_value')
        assert ti_data.get('displayed') == attribute_data.get('displayed')

    def tests_ti_address_add_security_label(self):
        """Create a tag on an address indicator.

        Args:
            request (fixture): The pytest request fixture.
        """
        helper_ti = self.ti_helper.create_indicator()

        r = helper_ti.add_label(label='TLP:GREEN')
        response_data = r.json()

        # assert response
        assert r.status_code == 201
        assert response_data.get('status') == 'Success'

    def tests_ti_address_add_tag(self, request):
        """Create a tag on an address indicator.

        Args:
            request (fixture): The pytest request fixture.
        """
        helper_ti = self.ti_helper.create_indicator()

        r = helper_ti.add_tag(request.node.name)
        response_data = r.json()

        # assert response
        assert r.status_code == 201
        assert response_data.get('status') == 'Success'

    def tests_ti_address_delete(self):
        """Create an address indicator using specific interface."""
        helper_ti = self.ti_helper.create_indicator()

        # indicator for delete
        ti = self.ti.address(ip=helper_ti.indicator, owner=helper_ti.owner)
        r = ti.delete()
        response_data = r.json()

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

    def tests_ti_address_get_address(self):
        """Get an address indicator."""
        helper_ti = self.ti_helper.create_indicator()

        # retrieve the indicator
        ti = self.ti.address(helper_ti.indicator, owner=helper_ti.owner)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get('address')

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('confidence') == helper_ti.confidence
        assert ti_data.get('ip') == helper_ti.indicator
        assert ti_data.get('rating') == helper_ti.rating

    def tests_ti_address_get_address_include(self, request):
        """Get an address indicator."""
        attribute_data = {
            'attribute_type': 'Description',
            'attribute_value': request.node.name,
        }
        label_data = {'label': 'TLP:RED'}
        tag_data = {'name': request.node.name}
        helper_ti = self.ti_helper.create_indicator(
            attributes=attribute_data, labels=label_data, tags=tag_data
        )

        # retrieve the indicator
        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.address(helper_ti.indicator, owner=helper_ti.owner)
        r = ti.single(params=parameters)
        response_data = r.json()
        ti_data = response_data.get('data', {}).get('address')

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('confidence') == helper_ti.confidence
        assert ti_data.get('ip') == helper_ti.indicator
        assert ti_data.get('rating') == helper_ti.rating

        # validate metadata
        assert ti_data.get('attribute')[0].get('value') == attribute_data.get('attribute_value')
        assert ti_data.get('securityLabel')[0].get('name') == label_data.get('label')
        for tag in ti_data.get('tag'):
            if tag.get('name') == tag_data.get('name'):
                break
        else:
            assert False, f"Could not find tag {tag_data.get('name')}"

    def tests_ti_address_get_address_attribute(self, request):
        """Get an address indicator."""
        attribute_data = {
            'attribute_type': 'Description',
            'attribute_value': request.node.name,
        }
        helper_ti = self.ti_helper.create_indicator(attributes=attribute_data)

        # retrieve the indicator
        ti = self.ti.address(helper_ti.indicator, owner=helper_ti.owner)
        for attribute in ti.attributes():
            if attribute.get('value') == request.node.name:
                break
        else:
            assert False, f'Could not find attribute with value {request.node.name}'

    def tests_ti_address_get_address_label(self, request):
        """Get an address indicator."""
        label_data = {'label': 'TLP:RED'}
        helper_ti = self.ti_helper.create_indicator(labels=label_data)

        # retrieve the indicator
        ti = self.ti.address(helper_ti.indicator, owner=helper_ti.owner)
        for label in ti.labels():
            if label.get('name') == label_data.get('label'):
                break
        else:
            assert False, f'Could not find tag with value {request.node.name}'

    def tests_ti_address_get_tag(self, request):
        """Test indicator get tag."""
        super().indicator_get_tag(request)

    def tests_ti_address_update(self):
        """Test updating indicator metadata."""
        super().indicator_update()
