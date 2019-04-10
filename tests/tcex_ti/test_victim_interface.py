# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestVictim:
    """Test TcEx Victim."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_victim_get(self, victim_id=None, name='victim-name-42353'):
        """Test victim get."""
        # create
        if not victim_id:
            victim_id = self.victim_create(name)

        # get
        ti = self.ti.victim(name, owner=tcex.args.tc_owner, unique_id=victim_id)
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('name') == name

        # delete
        self.victim_delete()

    def test_victim_get_attributes(self, victim_id=None, name='victim-name-12453'):
        """Test victim get."""
        # create
        if not victim_id:
            victim_id = self.victim_create(name)

        self.test_victim_add_attribute(
            victim_id=victim_id, attribute_type='Description', attribute_value='test1'
        )
        self.test_victim_add_attribute(
            victim_id=victim_id, attribute_type='Description', attribute_value='test2'
        )
        self.test_victim_add_attribute(
            victim_id=victim_id, attribute_type='Description', attribute_value='test3'
        )

        # get attributes
        ti = self.ti.victim(name, owner=tcex.args.tc_owner, unique_id=victim_id)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.victim_delete()

    def test_victim_get_tags(self, victim_id=None, name='victim-name-64235'):
        """Test victim get."""
        # create
        if not victim_id:
            victim_id = self.victim_create(name)

        self.test_victim_add_tag(victim_id=victim_id, tag='One')
        self.test_victim_add_tag(victim_id=victim_id, tag='Two')

        # get tags
        ti = self.ti.victim(name, owner=tcex.args.tc_owner, unique_id=victim_id)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.victim_delete()

    def test_victim_get_include(self, victim_id=None, name='victim-name-78159'):
        """Test victim get."""
        if not victim_id:
            victim_id = self.victim_create(name)

        self.test_victim_add_attribute(
            victim_id=victim_id, attribute_type='Description', attribute_value='test123'
        )
        self.test_victim_add_label(victim_id=victim_id, label='TLP:RED')
        self.test_victim_add_tag(victim_id=victim_id, tag='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.victim(name, owner=tcex.args.tc_owner, unique_id=victim_id)
        r = ti.single(params=parameters)

        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('victim').get('name') == name
        assert ti_data.get('data').get('victim').get('attribute')[0].get('value') == 'test123'
        # assert ti_data.get('data').get('victim').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('victim').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.victim_delete()

    def victim_create(self, name='victim-name-65341'):
        """Test victim create."""
        ti = self.ti.victim(name, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('victim').get('name') == name
        return ti.unique_id

    def test_victim_add_attribute(
        self,
        victim_id=None,
        name='victim-name-nkjvb',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test victim attribute add."""
        should_delete = False
        if not victim_id:
            should_delete = True
            victim_id = self.victim_create(name)

        ti = self.ti.victim(name, owner=tcex.args.tc_owner, unique_id=victim_id)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value

        if should_delete:
            self.victim_delete()

    def test_victim_add_label(self, victim_id=None, name='victim-name-ds4vb', label='TLP:GREEN'):
        """Test victim attribute add."""
        should_delete = False
        if not victim_id:
            should_delete = True
            victim_id = self.victim_create(name)

        ti = self.ti.victim(name, owner=tcex.args.tc_owner, unique_id=victim_id)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'

        if should_delete:
            self.victim_delete()

    def test_victim_add_tag(self, victim_id=None, name='victim-name-fdsv23', tag='Crimeware'):
        """Test victim attribute add."""
        should_delete = False
        if not victim_id:
            should_delete = True
            victim_id = self.victim_create(name)

        ti = self.ti.victim(name, owner=tcex.args.tc_owner, unique_id=victim_id)
        r = ti.add_tag(tag)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

        if should_delete:
            self.victim_delete()

    def victim_delete(self, victim_id=None, name='victim-name-bdsfd'):
        """Test victim delete."""
        # create indicator
        if not victim_id:
            victim_id = self.victim_create(name)

        # delete indicator
        ti = self.ti.victim(name, owner=tcex.args.tc_owner, unique_id=victim_id)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_victim_update(self, victim_id=None, name='victim-name-b3da3'):
        """Test victim update."""
        # create indicator
        if not victim_id:
            victim_id = self.victim_create(name)

        name = 'victim-new-name-fdasb3'

        # update indicator
        ti = self.ti.victim(name, owner=tcex.args.tc_owner, unique_id=victim_id)
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('victim').get('name') == name

        # delete indicator
        self.victim_delete()
