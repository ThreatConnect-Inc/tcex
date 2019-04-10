# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestAdversaryGroups:
    """Test TcEx Host Groups."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_incident_get(self, name='incident-name-42353'):
        """Test incident get."""
        # create
        incident_id = self.incident_create(name)

        # get
        ti = self.ti.incident(name, owner=tcex.args.tc_owner, unique_id=incident_id)
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('name') == name

        # delete
        self.incident_delete(incident_id)

    def test_incident_get_attributes(self, name='incident-name-12453'):
        """Test incident get."""
        # create
        incident_id = self.incident_create(name)
        self.test_incident_add_attribute(
            incident_id=incident_id, attribute_type='Description', attribute_value='test1'
        )
        self.test_incident_add_attribute(
            incident_id=incident_id, attribute_type='Description', attribute_value='test2'
        )
        self.test_incident_add_attribute(
            incident_id=incident_id, attribute_type='Description', attribute_value='test3'
        )

        # get attributes
        ti = self.ti.incident(name, owner=tcex.args.tc_owner, unique_id=incident_id)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.incident_delete(incident_id)

    def test_incident_get_tags(self, name='incident-name-64235'):
        """Test incident get."""
        # create
        incident_id = self.incident_create(name)
        self.test_incident_add_tag(incident_id=incident_id, tag='One')
        self.test_incident_add_tag(incident_id=incident_id, tag='Two')

        # get tags
        ti = self.ti.incident(name, owner=tcex.args.tc_owner, unique_id=incident_id)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.incident_delete(incident_id)

    def test_incident_get_include(self, name='incident-name-78159'):
        """Test incident get."""
        incident_id = self.incident_create(name)
        self.test_incident_add_attribute(
            incident_id=incident_id, attribute_type='Description', attribute_value='test123'
        )
        self.test_incident_add_label(incident_id=incident_id, label='TLP:RED')
        self.test_incident_add_tag(incident_id=incident_id, tag='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.incident(name, owner=tcex.args.tc_owner, unique_id=incident_id)
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('incident').get('name') == name
        assert ti_data.get('data').get('incident').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('incident').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('incident').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.incident_delete(incident_id)

    def incident_create(self, name='incident-name-65341'):
        """Test incident create."""
        ti = self.ti.incident(name, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('incident').get('name') == name
        return ti.unique_id

    def test_incident_add_attribute(
        self,
        incident_id=None,
        name='incident-name-nkjvb',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test incident attribute add."""
        should_delete = False
        if not incident_id:
            should_delete = True
            incident_id = self.incident_create(name)

        ti = self.ti.incident(name, owner=tcex.args.tc_owner, unique_id=incident_id)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value

        if should_delete:
            self.incident_delete(incident_id)

    def test_incident_add_label(
        self, incident_id=None, name='incident-name-ds4vb', label='TLP:GREEN'
    ):
        """Test incident attribute add."""
        should_delete = False
        if not incident_id:
            should_delete = True
            incident_id = self.incident_create(name)

        ti = self.ti.incident(name, owner=tcex.args.tc_owner, unique_id=incident_id)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'

        if should_delete:
            self.incident_delete(incident_id)

    def test_incident_add_tag(self, incident_id=None, name='incident-name-fdsv23', tag='Crimeware'):
        """Test incident attribute add."""
        should_delete = False
        if not incident_id:
            should_delete = True
            incident_id = self.incident_create(name)

        ti = self.ti.incident(name, owner=tcex.args.tc_owner, unique_id=incident_id)
        r = ti.add_tag(tag)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

        if should_delete:
            self.incident_delete(incident_id)

    def incident_delete(self, incident_id=None, name='incident-name-bdsfd'):
        """Test incident delete."""
        # create indicator
        if not incident_id:
            incident_id = self.incident_create(name)

        # delete indicator
        ti = self.ti.incident(name, owner=tcex.args.tc_owner, unique_id=incident_id)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_incident_update(self, name='incident-name-b3da3'):
        """Test incident update."""
        # create indicator
        incident_id = self.incident_create(name)

        name = 'incident-new-name-fdasb3'

        # update indicator
        ti = self.ti.incident(name, owner=tcex.args.tc_owner, unique_id=incident_id)
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('incident').get('name') == name
        r = ti.status('Rejected')
        assert r.status_code == 200
        r = ti.event_date('2019-03-29')
        assert r.status_code == 200

        # delete indicator
        self.incident_delete(incident_id)
