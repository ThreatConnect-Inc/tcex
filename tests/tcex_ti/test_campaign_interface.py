# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestCampaignGroups:
    """Test TcEx Host Groups."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_campaign_get(self, name='campaign-name-42353'):
        """Test campaign get."""
        # create
        campaign_id = self.campaign_create(name)

        # get
        ti = self.ti.campaign(name, owner=tcex.args.tc_owner, unique_id=campaign_id)
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('name') == name

        # delete
        self.campaign_delete(campaign_id)

    def test_campaign_get_attributes(self, name='campaign-name-12453'):
        """Test campaign get."""
        # create
        campaign_id = self.campaign_create(name)
        self.test_campaign_add_attribute(
            campaign_id=campaign_id, attribute_type='Description', attribute_value='test1'
        )
        self.test_campaign_add_attribute(
            campaign_id=campaign_id, attribute_type='Description', attribute_value='test2'
        )
        self.test_campaign_add_attribute(
            campaign_id=campaign_id, attribute_type='Description', attribute_value='test3'
        )

        # get attributes
        ti = self.ti.campaign(name, owner=tcex.args.tc_owner, unique_id=campaign_id)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.campaign_delete(campaign_id)

    def test_campaign_get_tags(self, name='campaign-name-64235'):
        """Test campaign get."""
        # create
        campaign_id = self.campaign_create(name)
        self.test_campaign_add_tag(campaign_id=campaign_id, tag='One')
        self.test_campaign_add_tag(campaign_id=campaign_id, tag='Two')

        # get tags
        ti = self.ti.campaign(name, owner=tcex.args.tc_owner, unique_id=campaign_id)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.campaign_delete(campaign_id)

    def test_campaign_get_include(self, name='campaign-name-78159'):
        """Test campaign get."""
        campaign_id = self.campaign_create(name)
        self.test_campaign_add_attribute(
            campaign_id=campaign_id, attribute_type='Description', attribute_value='test123'
        )
        self.test_campaign_add_label(campaign_id=campaign_id, label='TLP:RED')
        self.test_campaign_add_tag(campaign_id=campaign_id, tag='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.campaign(name, owner=tcex.args.tc_owner, unique_id=campaign_id)
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('campaign').get('name') == name
        assert ti_data.get('data').get('campaign').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('campaign').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('campaign').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.campaign_delete(campaign_id)

    def campaign_create(self, name='campaign-name-65341'):
        """Test campaign create."""
        ti = self.ti.campaign(name, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('campaign').get('name') == name
        return ti.unique_id

    def test_campaign_add_attribute(
        self,
        campaign_id=None,
        name='campaign-name-nkjvb',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test campaign attribute add."""
        should_delete = False
        if not campaign_id:
            should_delete = True
            campaign_id = self.campaign_create(name)

        ti = self.ti.campaign(name, owner=tcex.args.tc_owner, unique_id=campaign_id)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value

        if should_delete:
            self.campaign_delete(campaign_id)

    def test_campaign_add_label(
        self, campaign_id=None, name='campaign-name-ds4vb', label='TLP:GREEN'
    ):
        """Test campaign attribute add."""
        should_delete = False
        if not campaign_id:
            should_delete = True
            campaign_id = self.campaign_create(name)

        ti = self.ti.campaign(name, owner=tcex.args.tc_owner, unique_id=campaign_id)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'

        if should_delete:
            self.campaign_delete(campaign_id)

    def test_campaign_add_tag(self, campaign_id=None, name='campaign-name-fdsv23', tag='Crimeware'):
        """Test campaign attribute add."""
        should_delete = False
        if not campaign_id:
            should_delete = True
            campaign_id = self.campaign_create(name)

        ti = self.ti.campaign(name, owner=tcex.args.tc_owner, unique_id=campaign_id)
        r = ti.add_tag(tag)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

        if should_delete:
            self.campaign_delete(campaign_id)

    def campaign_delete(self, campaign_id=None, name='campaign-name-bdsfd'):
        """Test campaign delete."""
        # create indicator
        if not campaign_id:
            campaign_id = self.campaign_create(name)

        # delete indicator
        ti = self.ti.campaign(name, owner=tcex.args.tc_owner, unique_id=campaign_id)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_campaign_update(self, name='campaign-name-b3da3'):
        """Test campaign update."""
        # create indicator
        campaign_id = self.campaign_create(name)

        name = 'campaign-new-name-fdasb3'

        # update indicator
        ti = self.ti.campaign(name, owner=tcex.args.tc_owner, unique_id=campaign_id)
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('campaign').get('name') == name

        # delete indicator
        self.campaign_delete(campaign_id)
