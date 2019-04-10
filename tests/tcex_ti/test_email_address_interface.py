# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestEmailAddressIndicators:
    """Test TcEx Host Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_email_address_get(self, address='email_address_42353@gmail.com'):
        """Test email_address get."""
        # create
        self.email_address_create(address)

        # get
        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('address') == address

        # delete
        self.email_address_delete(address)

    def test_email_address_get_attributes(self, address='email_address_12453@gmail.com'):
        """Test email_address get."""
        # create
        self.email_address_create(address)
        self.test_email_address_add_attribute(False, address, 'Description', 'test1')
        self.test_email_address_add_attribute(False, address, 'Description', 'test2')
        self.test_email_address_add_attribute(False, address, 'Description', 'test3')

        # get attributes
        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.email_address_delete(address)

    def test_email_address_get_tags(self, address='email_address_64235@gmail.com'):
        """Test email_address get."""
        # create
        self.email_address_create(address)
        self.test_email_address_add_tag(False, address, 'One')
        self.test_email_address_add_tag(False, address, 'Two')

        # get tags
        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.email_address_delete(address)

    def test_email_address_get_include(self, address='email_address_78159@gmail.com'):
        """Test email_address get."""
        self.email_address_create(address)
        self.test_email_address_add_attribute(False, address, 'Description', 'test123')
        self.test_email_address_add_label(False, address, 'TLP:RED')
        self.test_email_address_add_tag(False, address, 'PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('emailAddress').get('address') == address
        assert ti_data.get('data').get('emailAddress').get('attribute')[0].get('value') == 'test123'
        assert (
            ti_data.get('data').get('emailAddress').get('securityLabel')[0].get('name') == 'TLP:RED'
        )
        assert ti_data.get('data').get('emailAddress').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.email_address_delete(address)

    def email_address_create(self, address='email_address_65341@gmail.com'):
        """Test email_address create."""
        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('emailAddress').get('address') == address

    def test_email_address_add_attribute(
        self,
        should_create=True,
        address='email_address_nkjvb@gmail.com',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test email_address attribute add."""
        if should_create:
            self.email_address_create(address)

        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value
        if should_create:
            self.email_address_delete(address)

    def test_email_address_add_label(
        self, should_create=True, address='email_address_ds4vb@gmail.com', label='TLP:GREEN'
    ):
        """Test email_address attribute add."""
        if should_create:
            self.email_address_create(address)

        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'
        if should_create:
            self.email_address_delete(address)

    def test_email_address_add_tag(
        self, should_create=True, address='email_address_fdsv23@gmail.com', name='Crimeware'
    ):
        """Test email_address attribute add."""
        if should_create:
            self.email_address_create(address)

        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        r = ti.add_tag(name=name)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'
        if should_create:
            self.email_address_delete(address)

    def email_address_delete(self, address='email_address_523fa@gmail.com'):
        """Test email_address delete."""
        # create indicator
        self.email_address_create(address)

        # delete indicator
        ti = self.ti.email_address(address, owner=tcex.args.tc_owner)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_email_address_update(self, address='email_address_b3da3@gmail.com'):
        """Test email_address update."""
        # create indicator
        self.email_address_create(address)

        # update indicator
        ti = self.ti.email_address(address, rating=5, confidence=10, owner=tcex.args.tc_owner)
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('emailAddress').get('rating') == 5.0
        assert ti_data.get('data').get('emailAddress').get('confidence') == 10

        # delete indicator
        self.email_address_delete(address)
