# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestEventGroups:
    """Test TcEx Host Groups."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_event_get(self, name='event-name-42353'):
        """Test event get."""
        # create
        event_id = self.event_create(name)

        # get
        ti = self.ti.event(name, owner=tcex.args.tc_owner, unique_id=event_id)
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('name') == name

        # delete
        self.event_delete(event_id)

    def test_event_get_attributes(self, name='event-name-12453'):
        """Test event get."""
        # create
        event_id = self.event_create(name)
        self.test_event_add_attribute(
            event_id=event_id, attribute_type='Description', attribute_value='test1'
        )
        self.test_event_add_attribute(
            event_id=event_id, attribute_type='Description', attribute_value='test2'
        )
        self.test_event_add_attribute(
            event_id=event_id, attribute_type='Description', attribute_value='test3'
        )

        # get attributes
        ti = self.ti.event(name, owner=tcex.args.tc_owner, unique_id=event_id)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.event_delete(event_id)

    def test_event_get_tags(self, name='event-name-64235'):
        """Test event get."""
        # create
        event_id = self.event_create(name)
        self.test_event_add_tag(event_id=event_id, tag='One')
        self.test_event_add_tag(event_id=event_id, tag='Two')

        # get tags
        ti = self.ti.event(name, owner=tcex.args.tc_owner, unique_id=event_id)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.event_delete(event_id)

    def test_event_get_include(self, name='event-name-78159'):
        """Test event get."""
        event_id = self.event_create(name)
        self.test_event_add_attribute(
            event_id=event_id, attribute_type='Description', attribute_value='test123'
        )
        self.test_event_add_label(event_id=event_id, label='TLP:RED')
        self.test_event_add_tag(event_id=event_id, tag='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.event(name, owner=tcex.args.tc_owner, unique_id=event_id)
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('event').get('name') == name
        assert ti_data.get('data').get('event').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('event').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('event').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.event_delete(event_id)

    def event_create(self, name='event-name-65341'):
        """Test event create."""
        ti = self.ti.event(name, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('event').get('name') == name
        return ti.unique_id

    def test_event_add_attribute(
        self,
        event_id=None,
        name='event-name-nkjvb',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test event attribute add."""
        should_delete = False
        if not event_id:
            should_delete = True
            event_id = self.event_create(name)

        ti = self.ti.event(name, owner=tcex.args.tc_owner, unique_id=event_id)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value

        if should_delete:
            self.event_delete(event_id)

    def test_event_add_label(self, event_id=None, name='event-name-ds4vb', label='TLP:GREEN'):
        """Test event attribute add."""
        should_delete = False
        if not event_id:
            should_delete = True
            event_id = self.event_create(name)

        ti = self.ti.event(name, owner=tcex.args.tc_owner, unique_id=event_id)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'

        if should_delete:
            self.event_delete(event_id)

    def test_event_add_tag(self, event_id=None, name='event-name-fdsv23', tag='Crimeware'):
        """Test event attribute add."""
        should_delete = False
        if not event_id:
            should_delete = True
            event_id = self.event_create(name)

        ti = self.ti.event(name, owner=tcex.args.tc_owner, unique_id=event_id)
        r = ti.add_tag(tag)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

        if should_delete:
            self.event_delete(event_id)

    def event_delete(self, event_id=None, name='event-name-bdsfd'):
        """Test event delete."""
        # create indicator
        if not event_id:
            event_id = self.event_create(name)

        # delete indicator
        ti = self.ti.event(name, owner=tcex.args.tc_owner, unique_id=event_id)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_event_update(self, name='event-name-b3da3'):
        """Test event update."""
        # create indicator
        event_id = self.event_create(name)

        name = 'event-new-name-fdasb3'

        # update indicator
        ti = self.ti.event(
            name, status='No Further Action', owner=tcex.args.tc_owner, unique_id=event_id
        )
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('event').get('name') == name
        assert ti_data.get('data').get('event').get('status') == 'No Further Action'

        # delete indicator
        self.event_delete(event_id)
