# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestIntrustionSetGroups:
    """Test TcEx IntrustionSet Groups."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_intrusion_sets_get(self, name='intrusion_sets-name-42353'):
        """Test intrusion_sets get."""
        # create
        intrusion_sets_id = self.intrusion_sets_create(name)

        # get
        ti = self.ti.intrusion_sets(name, owner=tcex.args.tc_owner, unique_id=intrusion_sets_id)
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('name') == name

        # delete
        self.intrusion_sets_delete(intrusion_sets_id)

    def test_intrusion_sets_get_attributes(self, name='intrusion_sets-name-12453'):
        """Test intrusion_sets get."""
        # create
        intrusion_sets_id = self.intrusion_sets_create(name)
        self.test_intrusion_sets_add_attribute(
            intrusion_sets_id=intrusion_sets_id,
            attribute_type='Description',
            attribute_value='test1',
        )
        self.test_intrusion_sets_add_attribute(
            intrusion_sets_id=intrusion_sets_id,
            attribute_type='Description',
            attribute_value='test2',
        )
        self.test_intrusion_sets_add_attribute(
            intrusion_sets_id=intrusion_sets_id,
            attribute_type='Description',
            attribute_value='test3',
        )

        # get attributes
        ti = self.ti.intrusion_sets(name, owner=tcex.args.tc_owner, unique_id=intrusion_sets_id)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.intrusion_sets_delete(intrusion_sets_id)

    def test_intrusion_sets_get_tags(self, name='intrusion_sets-name-64235'):
        """Test intrusion_sets get."""
        # create
        intrusion_sets_id = self.intrusion_sets_create(name)
        self.test_intrusion_sets_add_tag(intrusion_sets_id=intrusion_sets_id, tag='One')
        self.test_intrusion_sets_add_tag(intrusion_sets_id=intrusion_sets_id, tag='Two')

        # get tags
        ti = self.ti.intrusion_sets(name, owner=tcex.args.tc_owner, unique_id=intrusion_sets_id)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.intrusion_sets_delete(intrusion_sets_id)

    def test_intrusion_sets_get_include(self, name='intrusion_sets-name-78159'):
        """Test intrusion_sets get."""
        intrusion_sets_id = self.intrusion_sets_create(name)
        self.test_intrusion_sets_add_attribute(
            intrusion_sets_id=intrusion_sets_id,
            attribute_type='Description',
            attribute_value='test123',
        )
        self.test_intrusion_sets_add_label(intrusion_sets_id=intrusion_sets_id, label='TLP:RED')
        self.test_intrusion_sets_add_tag(intrusion_sets_id=intrusion_sets_id, tag='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.intrusion_sets(name, owner=tcex.args.tc_owner, unique_id=intrusion_sets_id)
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('intrusionSet').get('name') == name
        assert ti_data.get('data').get('intrusionSet').get('attribute')[0].get('value') == 'test123'
        assert (
            ti_data.get('data').get('intrusionSet').get('securityLabel')[0].get('name') == 'TLP:RED'
        )
        assert ti_data.get('data').get('intrusionSet').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.intrusion_sets_delete(intrusion_sets_id)

    def intrusion_sets_create(self, name='intrusion_sets-name-65341'):
        """Test intrusion_sets create."""
        ti = self.ti.intrusion_sets(name, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('intrusionSet').get('name') == name
        return ti.unique_id

    def test_intrusion_sets_add_attribute(
        self,
        intrusion_sets_id=None,
        name='intrusion_sets-name-nkjvb',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test intrusion_sets attribute add."""
        should_delete = False
        if not intrusion_sets_id:
            should_delete = True
            intrusion_sets_id = self.intrusion_sets_create(name)

        ti = self.ti.intrusion_sets(name, owner=tcex.args.tc_owner, unique_id=intrusion_sets_id)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value

        if should_delete:
            self.intrusion_sets_delete(intrusion_sets_id)

    def test_intrusion_sets_add_label(
        self, intrusion_sets_id=None, name='intrusion_sets-name-ds4vb', label='TLP:GREEN'
    ):
        """Test intrusion_sets attribute add."""
        should_delete = False
        if not intrusion_sets_id:
            should_delete = True
            intrusion_sets_id = self.intrusion_sets_create(name)

        ti = self.ti.intrusion_sets(name, owner=tcex.args.tc_owner, unique_id=intrusion_sets_id)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'

        if should_delete:
            self.intrusion_sets_delete(intrusion_sets_id)

    def test_intrusion_sets_add_tag(
        self, intrusion_sets_id=None, name='intrusion_sets-name-fdsv23', tag='Crimeware'
    ):
        """Test intrusion_sets attribute add."""
        should_delete = False
        if not intrusion_sets_id:
            should_delete = True
            intrusion_sets_id = self.intrusion_sets_create(name)

        ti = self.ti.intrusion_sets(name, owner=tcex.args.tc_owner, unique_id=intrusion_sets_id)
        r = ti.add_tag(tag)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

        if should_delete:
            self.intrusion_sets_delete(intrusion_sets_id)

    def intrusion_sets_delete(self, intrusion_sets_id=None, name='intrusion_sets-name-bdsfd'):
        """Test intrusion_sets delete."""
        # create indicator
        if not intrusion_sets_id:
            intrusion_sets_id = self.intrusion_sets_create(name)

        # delete indicator
        ti = self.ti.intrusion_sets(name, owner=tcex.args.tc_owner, unique_id=intrusion_sets_id)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_intrusion_sets_update(self, name='intrusion_sets-name-b3da3'):
        """Test intrusion_sets update."""
        # create indicator
        intrusion_sets_id = self.intrusion_sets_create(name)

        name = 'intrusion_sets-new-name-fdasb3'

        # update indicator
        ti = self.ti.intrusion_sets(name, unique_id=intrusion_sets_id)
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('intrusionSet').get('name') == name

        # delete indicator
        self.intrusion_sets_delete(intrusion_sets_id)
