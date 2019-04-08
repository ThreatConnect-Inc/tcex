# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestHostIndicators:
    """Test TcEx Host Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_host_get(self, hostname='www.hostname-title-42353.com'):
        """Test host get."""
        # create
        self.test_host_create(hostname)

        # get
        ti = self.ti.host(hostname)
        r = ti.single(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('hostName') == hostname

        # delete
        self.test_host_delete(hostname)

    def test_host_get_attributes(self, hostname='www.hostname-title-12453.com'):
        """Test host get."""
        # create
        self.test_host_create(hostname)
        self.test_host_add_attribute(hostname, 'Description', 'test1')
        self.test_host_add_attribute(hostname, 'Description', 'test2')
        self.test_host_add_attribute(hostname, 'Description', 'test3')

        # get attributes
        ti = self.ti.host(hostname)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.test_host_delete(hostname)

    def test_host_get_tags(self, hostname='www.hostname-title-64235.com'):
        """Test host get."""
        # create
        self.test_host_create(hostname)
        self.test_host_add_tag(hostname, 'One')
        self.test_host_add_tag(hostname, 'Two')

        # get tags
        ti = self.ti.host(hostname)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.test_host_delete(hostname)

    def test_host_get_include(self, hostname='www.hostname-title-78159.com'):
        """Test host get."""
        self.test_host_create(hostname)
        self.test_host_add_attribute(hostname, 'Description', 'test123')
        self.test_host_add_label(hostname, 'TLP:RED')
        self.test_host_add_tag(hostname, 'PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.host(hostname)
        r = ti.single(owner='TCI', params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('host').get('hostName') == hostname
        assert ti_data.get('data').get('host').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('host').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('host').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.test_host_delete(hostname)

    def test_host_create(self, hostname='www.hostname-title-65341.com'):
        """Test host create."""
        ti = self.ti.host(hostname)
        r = ti.create(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('host').get('hostName') == hostname

    def test_host_add_attribute(
        self,
        hostname='www.hostname-title-nkjvb.com',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test host attribute add."""
        self.test_host_create(hostname)

        ti = self.ti.host(hostname)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value

    def test_host_add_label(self, hostname='www.hostname-title-ds4vb.com', label='TLP:GREEN'):
        """Test host attribute add."""
        self.test_host_create(hostname)

        ti = self.ti.host(hostname)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'

    def test_host_add_tag(self, hostname='www.hostname-title-fdsv23.com', name='Crimeware'):
        """Test host attribute add."""
        self.test_host_create(hostname)

        ti = self.ti.host(hostname)
        r = ti.add_tag(name=name)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

    def test_host_delete(self, hostname='www.hostname-title-523fa.com'):
        """Test host delete."""
        # create indicator
        self.test_host_create(hostname)

        # delete indicator
        ti = self.ti.host(hostname)
        r = ti.delete(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_host_update(self, hostname='www.hostname-title-b3da3.com'):
        """Test host update."""
        # create indicator
        self.test_host_create(hostname)

        # update indicator
        ti = self.ti.host(hostname, rating=5, confidence=10)
        r = ti.update(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('host').get('rating') == 5.0
        assert ti_data.get('data').get('host').get('confidence') == 10

        # delete indicator
        self.test_host_delete(hostname)
