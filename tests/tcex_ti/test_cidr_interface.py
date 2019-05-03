# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
from ..tcex_init import tcex


# pylint: disable=W0201
# pylint: disable=E1101
class TestCIDRIndicators:
    """Test TcEx CIDR Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti
        blocks = [
            '1.1.1.1/8',
            '1.1.1.2/8',
            '1.1.1.3/8',
            '1.1.1.4/8',
            '1.1.1.5/8',
            '1.1.1.6/8',
            '1.1.1.7/8',
        ]
        for block in blocks:
            ti = self.ti.indicator(indicator_type='CIDR', owner=tcex.args.tc_owner, Block=block)
            ti.delete()

    def test_cidr_get(self, block='1.1.1.1/8'):
        """Test cidr get."""
        # create
        self.cidr_create(block)

        # get
        ti = self.ti.cidr(block, owner=tcex.args.tc_owner)
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('Block') == block

    def test_cidr_get_attributes(self, block='1.1.1.2/8'):
        """Test cidr get."""
        # create
        self.cidr_create(block)
        self.test_cidr_add_attribute(False, block, 'Description', 'test1')
        self.test_cidr_add_attribute(False, block, 'Description', 'test2')
        self.test_cidr_add_attribute(False, block, 'Description', 'test3')

        # get attributes
        ti = self.ti.cidr(block, owner=tcex.args.tc_owner)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

    def test_cidr_get_tags(self, block='1.1.1.3/8'):
        """Test cidr get."""
        # create
        self.cidr_create(block)
        self.test_cidr_add_tag(False, block, 'One')
        self.test_cidr_add_tag(False, block, 'Two')

        # get tags
        ti = self.ti.cidr(block, owner=tcex.args.tc_owner)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

    def test_cidr_get_include(self, block='1.1.1.8/8'):
        """Test cidr get."""
        self.cidr_create(block)

        self.test_cidr_add_attribute(False, block, 'Description', 'test123')
        self.test_cidr_add_label(False, block, 'TLP:RED')
        self.test_cidr_add_tag(False, block, 'PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.cidr(block, owner=tcex.args.tc_owner)
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('Block') == block
        assert ti_data.get('data').get(ti.api_entity).get('attribute')[0].get('value') == 'test123'
        assert (
            ti_data.get('data').get(ti.api_entity).get('securityLabel')[0].get('name') == 'TLP:RED'
        )
        assert ti_data.get('data').get(ti.api_entity).get('tag')[0].get('name') == 'PyTest'

    def cidr_create(self, block='1.1.1.7/8'):
        """Test cidr create."""
        ti = self.ti.indicator(indicator_type='CIDR', owner=tcex.args.tc_owner, Block=block)
        r = ti.create()
        print(r.text)
        print(r.url)
        print(block)
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('Block') == block

    def test_cidr_add_attribute(
        self,
        should_create=True,
        block='1.1.1.1/8',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test cidr attribute add."""
        if should_create:
            self.cidr_create(block)

        ti = self.ti.cidr(block, owner=tcex.args.tc_owner)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value

    def test_cidr_add_label(self, should_create=True, block='1.1.1.6/8', label='TLP:GREEN'):
        """Test cidr attribute add."""
        if should_create:
            self.cidr_create(block)

        ti = self.ti.cidr(block, owner=tcex.args.tc_owner)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'

    def test_cidr_add_tag(self, should_create=True, block='1.1.1.5/8', name='Crimeware'):
        """Test cidr attribute add."""
        if should_create:
            self.cidr_create(block)

        ti = self.ti.cidr(block, owner=tcex.args.tc_owner)
        r = ti.add_tag(name=name)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

    def cidr_delete(self, block):
        """Test cidr delete."""
        # create indicator
        self.cidr_create(block)

        # delete indicator
        ti = self.ti.indicator(indicator_type='CIDR', owner=tcex.args.tc_owner, block=block)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_cidr_update(self, block='1.1.1.4/8'):
        """Test cidr update."""
        # create indicator
        self.cidr_create(block)

        # update indicator
        ti = self.ti.indicator(
            indicator_type='CIDR', owner=tcex.args.tc_owner, Block=block, rating=5, confidence=10
        )
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('rating') == 5.0
        assert ti_data.get('data').get(ti.api_entity).get('confidence') == 10
