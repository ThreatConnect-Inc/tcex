# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestUrlIndicators:
    """Test TcEx Host Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_url_get(self, text='https://url-title-42353.com'):
        """Test url get."""
        # create
        self.test_url_create(text)

        # get
        ti = self.ti.url(text)
        r = ti.single(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('text') == text

        # delete
        self.test_url_delete(text)

    def test_url_get_attributes(self, text='https://url-title-12453.com'):
        """Test url get."""
        # create
        self.test_url_create(text)
        self.test_url_add_attribute(text, 'Description', 'test1')
        self.test_url_add_attribute(text, 'Description', 'test2')
        self.test_url_add_attribute(text, 'Description', 'test3')

        # get attributes
        ti = self.ti.url(text)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.test_url_delete(text)

    def test_url_get_tags(self, text='https://url-title-64235.com'):
        """Test url get."""
        # create
        self.test_url_create(text)
        self.test_url_add_tag(text, 'One')
        self.test_url_add_tag(text, 'Two')

        # get tags
        ti = self.ti.url(text)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.test_url_delete(text)

    def test_url_get_include(self, text='https://url-title-78159.com'):
        """Test url get."""
        self.test_url_create(text)
        self.test_url_add_attribute(text, 'Description', 'test123')
        self.test_url_add_label(text, 'TLP:RED')
        self.test_url_add_tag(text, 'PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.url(text)
        r = ti.single(owner='TCI', params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('url').get('text') == text
        assert ti_data.get('data').get('url').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('url').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('url').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.test_url_delete(text)

    def test_url_create(self, text='https://url-title-65341.com'):
        """Test url create."""
        ti = self.ti.url(text)
        r = ti.create(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('url').get('text') == text

    def test_url_add_attribute(
        self,
        text='https://url-title-nkjvb.com',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test url attribute add."""
        self.test_url_create(text)

        ti = self.ti.url(text)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value

    def test_url_add_label(self, text='https://url-title-ds4vb.com', label='TLP:GREEN'):
        """Test url attribute add."""
        self.test_url_create(text)

        ti = self.ti.url(text)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'

    def test_url_add_tag(self, text='https://url-title-fdsv23.com', name='Crimeware'):
        """Test url attribute add."""
        self.test_url_create(text)

        ti = self.ti.url(text)
        r = ti.add_tag(name=name)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

    def test_url_delete(self, text='https://url-title-523fa.com'):
        """Test url delete."""
        # create indicator
        self.test_url_create(text)

        # delete indicator
        ti = self.ti.url(text)
        r = ti.delete(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_url_update(self, text='https://url-title-b3da3.com'):
        """Test url update."""
        # create indicator
        self.test_url_create(text)

        # update indicator
        ti = self.ti.url(text, rating=5, confidence=10)
        r = ti.update(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('url').get('rating') == 5.0
        assert ti_data.get('data').get('url').get('confidence') == 10

        # delete indicator
        self.test_url_delete(text)
