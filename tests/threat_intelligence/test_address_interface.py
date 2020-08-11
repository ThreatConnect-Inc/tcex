"""Test the TcEx Threat Intel Module."""
# standard library
import os
from datetime import datetime, timedelta
from random import randint

from .ti_helpers import TestThreatIntelligence, TIHelper


class TestAddressIndicators(TestThreatIntelligence):
    """Test TcEx Address Indicators."""

    indicator_field = 'ip'
    indicator_field_arg = indicator_field.replace(' ', '_').lower()
    indicator_field_custom = 'ip'
    indicator_type = 'Address'
    owner = os.getenv('TC_OWNER')
    ti = None
    ti_helper = None
    tcex = None

    def setup_class(self):
        """Configure setup before all tests."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.indicator_type, self.indicator_field_arg)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.ti_helper.cleanup()

    def tests_ti_association_example_1(self):
        """Testing TI module"""
        rand_ip = self.ti_helper.rand_ip()
        indicator_kwargs = {'ip': rand_ip, 'rating': randint(0, 5), 'confidence': randint(0, 100)}
        group_kwargs = {
            'fileName': self.ti_helper.rand_filename(),
            'name': self.ti_helper.rand_name(),
        }
        indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
        indicator.create()
        group = self.ti.group('document', self.owner, **group_kwargs)
        group.create()

        indicator.add_association(group)

        indicator = self.ti.indicator('address', self.owner, ip=rand_ip)
        empty = True
        for association in indicator.group_associations():
            assert association.get('id') == group.unique_id
            empty = False
        if empty:
            assert False, 'No group association was created'
        empty = True
        for association in group.indicator_associations():
            assert association.get('summary') == indicator.unique_id
            empty = False
        if empty:
            assert False, 'No indicator association was created'

    def tests_ti_association_example_2(self):
        """Testing TI module"""
        rand_ip = self.ti_helper.rand_ip()
        indicator_kwargs = {'ip': rand_ip, 'rating': randint(0, 5), 'confidence': randint(0, 100)}
        group_kwargs = {
            'fileName': self.ti_helper.rand_filename(),
            'name': self.ti_helper.rand_name(),
        }
        indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
        indicator.create()
        group = self.ti.group('document', self.owner, **group_kwargs)
        group.create()

        indicator = self.ti.indicator('address', self.owner, ip=rand_ip)
        group = self.ti.group('document', self.owner, id=group.unique_id)

        indicator.add_association(group)

        indicator = self.ti.indicator('address', self.owner, ip=rand_ip)
        empty = True
        for association in indicator.group_associations():
            assert str(association.get('id')) == group.unique_id
            empty = False
        if empty:
            assert False, 'No group association was created'
        empty = True
        for association in group.indicator_associations():
            assert association.get('summary') == indicator.unique_id
            empty = False
        if empty:
            assert False, 'No indicator association was created'

    def tests_ti_indicators_owners(self):
        """Testing TI module"""
        rand_ip = self.ti_helper.rand_ip()
        indicator_kwargs = {'ip': rand_ip, 'rating': randint(0, 5), 'confidence': randint(0, 100)}
        indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
        indicator.create()
        owner = indicator.owners()
        assert len(owner.json().get('data', {}).get('owner', [])) == 1, 'Owners were not retrieved.'

    def tests_ti_indicators_date_filter(self):
        """Testing TI module"""
        rand_ip = self.ti_helper.rand_ip()
        indicator_kwargs = {'ip': rand_ip, 'rating': randint(0, 5), 'confidence': randint(0, 100)}
        indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
        indicator.create()
        today = datetime.strftime(datetime.now(), '%Y-%m-%d')
        tomorrow = datetime.strftime(datetime.now() + timedelta(1), '%Y-%m-%d')
        filters = self.tcex.ti.filters()
        filters.add_filter('dateAdded', '>', today)
        filters.add_filter('dateAdded', '<', tomorrow)
        indicators = self.tcex.ti.indicator()
        found = False
        for indicator in indicators.many(filters=filters):
            if indicator.get('summary') == rand_ip:
                found = True

        assert found, 'Expected Indicator not returned on dateAdded filter.'

    def tests_ti_indicators_active_and_inactive_filter(self):
        """Testing TI module"""
        rand_ip_1 = self.ti_helper.rand_ip()
        rand_ip_2 = self.ti_helper.rand_ip()
        indicator_kwargs = {
            'ip': rand_ip_1,
            'rating': randint(0, 5),
            'confidence': randint(0, 100),
            'active': True,
        }
        indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
        indicator.create()
        indicator_kwargs['ip'] = rand_ip_2
        indicator_kwargs['active'] = False
        indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
        indicator.create()
        filters = self.ti.filters()
        filters.add_filter('active', '=', 'true')
        filters.add_filter('active', '=', 'false')
        parameters = {'orParams': 'true'}
        indicators = self.tcex.ti.indicator()
        active_found = False
        inactive_found = False
        for indicator in indicators.many(filters=filters, params=parameters):
            if indicator.get('summary') == rand_ip_1:
                active_found = True
            if indicator.get('summary') == rand_ip_2:
                inactive_found = True
            if active_found and inactive_found:
                break

        assert active_found, 'Expected Indicator not returned on active filter.'
        assert inactive_found, 'Expected Indicator not returned on inactive filter.'

    def tests_ti_indicators_inactive_filter(self):
        """Testing TI module"""
        rand_ip = self.ti_helper.rand_ip()
        indicator_kwargs = {
            'ip': rand_ip,
            'rating': randint(0, 5),
            'confidence': randint(0, 100),
            'active': False,
        }
        indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
        indicator.create()
        filters = self.ti.filters()
        filters.add_filter('active', '=', 'false')
        indicators = self.tcex.ti.indicator()
        active_found = False
        for indicator in indicators.many(filters=filters):
            if indicator.get('summary') == rand_ip:
                active_found = True
            if active_found:
                break

        assert active_found, 'Expected Indicator not returned on active filter.'

    def tests_ti_indicators_to_groups(self):
        """Testing TI module"""
        rand_ip = self.ti_helper.rand_ip()
        indicator_kwargs = {'ip': rand_ip, 'rating': randint(0, 5), 'confidence': randint(0, 100)}
        indicator = self.ti.indicator('address', self.owner, **indicator_kwargs)
        indicator.create()
        group_name = self.ti_helper.rand_name()
        group_data = {
            'name': group_name,
            'owner': self.owner,
        }
        ti = self.ti.adversary(**group_data)
        ti.create()
        indicator.add_association(ti)
        found = False
        for group in indicator.group_associations():
            if group.get('name') == group_name:
                found = True

        assert found, 'Failed to retrieve group associations from indicator.'

    def tests_ti_address_create(self):
        """Create an address indicator using specific interface."""
        indicator_data = {
            'confidence': randint(0, 100),
            self.indicator_field_custom: self.ti_helper.rand_ip(),
            'owner': self.owner,
            'rating': randint(0, 5),
        }
        ti = self.ti.address(**indicator_data)
        r = ti.create()
        assert ti.as_entity

        # assert response
        assert r.status_code == 201

        # retrieve indicator for asserts
        ti = self.ti.address(**indicator_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('confidence') == indicator_data.get('confidence')
        assert ti_data.get(ti.api_entity) == indicator_data.get(ti.api_entity)
        assert ti_data.get('rating') == indicator_data.get('rating')

        # cleanup indicator
        r = ti.delete()
        assert r.status_code == 200

    def tests_ti_address_add_attribute(self, request):
        """Test indicator add attribute."""
        super().indicator_add_attribute(request)

    def tests_ti_address_add_label(self):
        """Test indicator add label."""
        super().indicator_add_label()

    def tests_ti_address_add_tag(self, request):
        """Test indicator add tag."""
        super().indicator_add_tag(request)

    def tests_ti_address_delete(self):
        """Test indicator delete."""
        super().indicator_delete()

    def tests_ti_address_get(self):
        """Test indicator get with generic indicator method."""
        super().indicator_get()

    def tests_ti_address_get_includes(self, request):
        """Test indicator get with includes."""
        super().indicator_get_includes(request)

    def tests_ti_address_get_attribute(self, request):
        """Test indicator get attribute."""
        super().indicator_get_attribute(request)

    def tests_ti_address_get_label(self):
        """Test indicator get label."""
        super().indicator_get_label()

    def tests_ti_address_get_tag(self, request):
        """Test indicator get tag."""
        super().indicator_get_tag(request)

    def tests_ti_address_update(self):
        """Test updating indicator metadata."""
        super().indicator_update()
