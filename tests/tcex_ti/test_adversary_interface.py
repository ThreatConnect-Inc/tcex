# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestAdversaryGroups:
    """Test TcEx Host Groups."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_adversary_get(self, name='adversary-name-42353'):
        """Test adversary get."""
        # create
        adversary_id = self.adversary_create(name)

        # get
        ti = self.ti.adversary(name, owner=tcex.args.tc_owner, unique_id=adversary_id)
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('name') == name

        # delete
        self.adversary_delete(adversary_id)

    def test_adversary_get_attributes(self, name='adversary-name-12453'):
        """Test adversary get."""
        # create
        adversary_id = self.adversary_create(name)
        self.test_adversary_add_attribute(
            adversary_id=adversary_id, attribute_type='Description', attribute_value='test1'
        )
        self.test_adversary_add_attribute(
            adversary_id=adversary_id, attribute_type='Description', attribute_value='test2'
        )
        self.test_adversary_add_attribute(
            adversary_id=adversary_id, attribute_type='Description', attribute_value='test3'
        )

        # get attributes
        ti = self.ti.adversary(name, owner=tcex.args.tc_owner, unique_id=adversary_id)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.adversary_delete(adversary_id)

    def test_adversary_get_tags(self, name='adversary-name-64235'):
        """Test adversary get."""
        # create
        adversary_id = self.adversary_create(name)
        self.test_adversary_add_tag(adversary_id=adversary_id, tag='One')
        self.test_adversary_add_tag(adversary_id=adversary_id, tag='Two')

        # get tags
        ti = self.ti.adversary(name, owner=tcex.args.tc_owner, unique_id=adversary_id)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.adversary_delete(adversary_id)

    def test_adversary_get_include(self, name='adversary-name-78159'):
        """Test adversary get."""
        adversary_id = self.adversary_create(name)
        self.test_adversary_add_attribute(
            adversary_id=adversary_id, attribute_type='Description', attribute_value='test123'
        )
        self.test_adversary_add_label(adversary_id=adversary_id, label='TLP:RED')
        self.test_adversary_add_tag(adversary_id=adversary_id, tag='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.adversary(name, owner=tcex.args.tc_owner, unique_id=adversary_id)
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('adversary').get('name') == name
        assert ti_data.get('data').get('adversary').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('adversary').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('adversary').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.adversary_delete(adversary_id)

    def adversary_create(self, name='adversary-name-65341'):
        """Test adversary create."""
        ti = self.ti.adversary(name, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('adversary').get('name') == name
        return ti.unique_id

    def test_adversary_add_attribute(
        self,
        adversary_id=None,
        name='adversary-name-nkjvb',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test adversary attribute add."""

        should_delete = False
        if not adversary_id:
            should_delete = True
            adversary_id = self.adversary_create(name)

        ti = self.ti.adversary(name, owner=tcex.args.tc_owner, unique_id=adversary_id)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value
        if should_delete:
            self.adversary_delete(adversary_id)

    def test_adversary_add_label(
        self, adversary_id=None, name='adversary-name-ds4vb', label='TLP:GREEN'
    ):
        """Test adversary attribute add."""
        should_delete = False
        if not adversary_id:
            should_delete = True
            adversary_id = self.adversary_create(name)

        ti = self.ti.adversary(name, owner=tcex.args.tc_owner, unique_id=adversary_id)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'
        if should_delete:
            self.adversary_delete(adversary_id)

    def test_adversary_add_tag(
        self, adversary_id=None, name='adversary-name-fdsv23', tag='Crimeware'
    ):
        """Test adversary attribute add."""
        should_delete = False
        if not adversary_id:
            should_delete = True
            adversary_id = self.adversary_create(name)

        ti = self.ti.adversary(name, owner=tcex.args.tc_owner, unique_id=adversary_id)
        r = ti.add_tag(tag)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'
        if should_delete:
            self.adversary_delete(adversary_id)

    def adversary_delete(self, adversary_id=None, name='adversary-name-bdsfd'):
        """Test adversary delete."""
        # create indicator
        if not adversary_id:
            adversary_id = self.adversary_create(name)

        # delete indicator
        ti = self.ti.adversary(name, owner=tcex.args.tc_owner, unique_id=adversary_id)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_adversary_update(self, name='adversary-name-b3da3'):
        """Test adversary update."""
        # create indicator
        adversary_id = self.adversary_create(name)

        name = 'adversary-new-name-fdasb3'

        # update indicator
        ti = self.ti.adversary(name, owner=tcex.args.tc_owner, unique_id=adversary_id)
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('adversary').get('name') == name

        # delete indicator
        self.adversary_delete(adversary_id)
