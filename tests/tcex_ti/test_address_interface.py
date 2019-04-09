# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestAddressIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_address_get(self, ip='17.15.30.41'):
        """Test address get."""
        # create
        self.address_create(ip)

        # get
        ti = self.ti.address(ip)
        r = ti.single(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('address').get('ip') == ip

        # delete
        self.address_delete(ip)

    def test_address_get_attributes(self, ip='11.21.31.41'):
        """Test address get."""
        # create
        self.address_create(ip)
        self.test_address_add_attribute(False, ip, 'Description', 'test1')
        self.test_address_add_attribute(False, ip, 'Description', 'test2')
        self.test_address_add_attribute(False, ip, 'Description', 'test3')

        # get attributes
        ti = self.ti.address(ip)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.address_delete(ip)

    def test_address_get_tags(self, ip='13.23.33.43'):
        """Test address get."""
        # create
        self.address_create(ip)
        self.test_address_add_tag(False, ip, 'One')
        self.test_address_add_tag(False, ip, 'Two')

        # get tags
        ti = self.ti.address(ip)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.address_delete(ip)

    def test_address_get_include(self, ip='40.30.20.10'):
        """Test address get."""
        self.address_create(ip)

        self.test_address_add_attribute(False, ip, 'Description', 'test123')
        self.test_address_add_label(False, ip, 'TLP:RED')
        self.test_address_add_tag(False, ip, 'PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.address(ip)
        r = ti.single(owner='TCI', params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('address').get('ip') == ip
        assert ti_data.get('data').get('address').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('address').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('address').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.address_delete(ip)

    def address_create(self, ip='14.111.14.15'):
        """Test address create."""
        ti = self.ti.indicator(indicator_type='Address', ip=ip)
        r = ti.create('TCI')
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('address').get('ip') == ip

    def test_address_add_attribute(
        self,
        should_create=True,
        ip='12.13.14.15',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test address attribute add."""
        if should_create:
            self.address_create(ip)

        ti = self.ti.address(ip)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value
        if should_create:
            self.address_delete(ip)

    def test_address_add_label(self, should_create=True, ip='12.13.14.15', label='TLP:GREEN'):
        """Test address attribute add."""
        if should_create:
            self.address_create(ip)

        ti = self.ti.address(ip)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'
        if should_create:
            self.address_delete(ip)

    def test_address_add_tag(self, should_create=True, ip='12.13.14.15', name='Crimeware'):
        """Test address attribute add."""
        if should_create:
            self.address_create(ip)

        ti = self.ti.address(ip)
        r = ti.add_tag(name=name)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'
        if should_create:
            self.address_delete(ip)

    def address_delete(self, ip='12.11.12.11'):
        """Test address delete."""
        # create indicator
        self.address_create(ip)

        # delete indicator
        ti = self.ti.indicator(indicator_type='Address', ip=ip)
        r = ti.delete(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_address_update(self, ip='13.11.13.11'):
        """Test address update."""
        # create indicator
        self.address_create(ip)

        # update indicator
        ti = self.ti.indicator(indicator_type='Address', ip=ip, rating=5, confidence=10)
        r = ti.update(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('address').get('rating') == 5.0
        assert ti_data.get('data').get('address').get('confidence') == 10

        # delete indicator
        self.address_delete(ip)
