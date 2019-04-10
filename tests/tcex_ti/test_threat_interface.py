# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestThreatGroups:
    """Test TcEx Threat Groups."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_threat_get(self, threat_id=None, name='threat-name-42353'):
        """Test threat get."""
        # create
        if not threat_id:
            threat_id = self.threat_create(name)

        # get
        ti = self.ti.threat(name, owner=tcex.args.tc_owner, unique_id=threat_id)
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('name') == name

        # delete
        self.threat_delete(threat_id)

    def test_threat_get_attributes(self, threat_id=None, name='threat-name-12453'):
        """Test threat get."""
        # create
        if not threat_id:
            threat_id = self.threat_create(name)

        self.test_threat_add_attribute(
            threat_id=threat_id, attribute_type='Description', attribute_value='test1'
        )
        self.test_threat_add_attribute(
            threat_id=threat_id, attribute_type='Description', attribute_value='test2'
        )
        self.test_threat_add_attribute(
            threat_id=threat_id, attribute_type='Description', attribute_value='test3'
        )

        # get attributes
        ti = self.ti.threat(name, unique_id=threat_id)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.threat_delete(threat_id)

    def test_threat_get_tags(self, threat_id=None, name='threat-name-64235'):
        """Test threat get."""
        # create
        if not threat_id:
            threat_id = self.threat_create(name)

        self.test_threat_add_tag(threat_id=threat_id, tag='One')
        self.test_threat_add_tag(threat_id=threat_id, tag='Two')

        # get tags
        ti = self.ti.threat(name, unique_id=threat_id)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.threat_delete(threat_id)

    def test_threat_get_include(self, threat_id=None, name='threat-name-78159'):
        """Test threat get."""
        if not threat_id:
            threat_id = self.threat_create(name)

        self.test_threat_add_attribute(
            threat_id=threat_id, attribute_type='Description', attribute_value='test123'
        )
        self.test_threat_add_label(threat_id=threat_id, label='TLP:RED')
        self.test_threat_add_tag(threat_id=threat_id, tag='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.threat(name, unique_id=threat_id)
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('threat').get('name') == name
        assert ti_data.get('data').get('threat').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('threat').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('threat').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.threat_delete(threat_id)

    def threat_create(self, name='threat-name-65341'):
        """Test threat create."""
        ti = self.ti.threat(name, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('threat').get('name') == name
        return ti.unique_id

    def test_threat_add_attribute(
        self,
        threat_id=None,
        name='threat-name-nkjvb',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test threat attribute add."""

        should_delete = False
        if not threat_id:
            should_delete = True
            threat_id = self.threat_create(name)

        ti = self.ti.threat(name, unique_id=threat_id)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value

        if should_delete:
            self.threat_delete()

    def test_threat_add_label(self, threat_id=None, name='threat-name-ds4vb', label='TLP:GREEN'):
        """Test threat attribute add."""
        should_delete = False
        if not threat_id:
            should_delete = True
            threat_id = self.threat_create(name)

        ti = self.ti.threat(name, owner=tcex.args.tc_owner, unique_id=threat_id)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'
        if should_delete:
            self.threat_delete()

    def test_threat_add_tag(self, threat_id=None, name='threat-name-fdsv23', tag='Crimeware'):
        """Test threat attribute add."""
        should_delete = False
        if not threat_id:
            should_delete = True
            threat_id = self.threat_create(name)

        ti = self.ti.threat(name, owner=tcex.args.tc_owner, unique_id=threat_id)
        r = ti.add_tag(tag)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'
        if should_delete:
            self.threat_delete()

    def threat_delete(self, threat_id=None, name='threat-name-bdsfd'):
        """Test threat delete."""
        # create indicator
        if not threat_id:
            threat_id = self.threat_create(name)

        # delete indicator
        ti = self.ti.threat(name, owner=tcex.args.tc_owner, unique_id=threat_id)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_threat_update(self, threat_id=None, name='threat-name-b3da3'):
        """Test threat update."""
        # create indicator
        if not threat_id:
            threat_id = self.threat_create(name)

        name = 'threat-new-name-fdasb3'

        # update indicator
        ti = self.ti.threat(name, owner=tcex.args.tc_owner, unique_id=threat_id)
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('threat').get('name') == name

        # delete indicator
        self.threat_delete()
