# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestFileIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def teardown_class(self):
        """Configure setup before all tests."""
        hash_prefixes = ['A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'B4', 'B5', 'B6', 'B7']
        for hp in hash_prefixes:
            unique_id = hp * 16
            ti = self.ti.file(owner=tcex.args.tc_owner, unique_id=unique_id)
            ti.delete()

    def test_file_get(self, file_uuid=None, md5='A4', sha1='A4', sha256='A4'):
        """Test file get."""
        # create
        if not file_uuid:
            file_uuid = self.file_create(md5=md5 * 16, sha1=sha1 * 20, sha256=sha256 * 32)

        # get
        ti = self.ti.file(owner=tcex.args.tc_owner, unique_id=file_uuid)
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('file').get('md5', None) == md5 * 16
        assert ti_data.get('data').get('file').get('sha1', None) == sha1 * 20
        assert ti_data.get('data').get('file').get('sha256', None) == sha256 * 32

        # delete
        self.test_file_delete(file_uuid)

    def test_file_get_attributes(self, file_uuid=None, md5='A5', sha1='A5', sha256='A5'):
        """Test file get."""
        # create
        if not file_uuid:
            file_uuid = self.file_create(md5 * 16, sha1 * 20, sha256 * 32)

        self.test_file_add_attribute(file_uuid, 'Description', 'test1')
        self.test_file_add_attribute(file_uuid, 'Description', 'test2')
        self.test_file_add_attribute(file_uuid, 'Description', 'test3')

        # get attributes
        ti = self.ti.file(owner=tcex.args.tc_owner, unique_id=file_uuid)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.test_file_delete(file_uuid)

    def test_file_get_tags(self, file_uuid=None, md5='A6', sha1='A6', sha256='A6'):
        """Test file get."""
        # create
        if not file_uuid:
            file_uuid = self.file_create(md5=md5 * 16, sha1=sha1 * 20, sha256=sha256 * 32)

        self.test_file_add_tag(file_uuid, 'One')
        self.test_file_add_tag(file_uuid, 'Two')

        # get tags
        ti = self.ti.file(owner=tcex.args.tc_owner, unique_id=file_uuid)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.test_file_delete(file_uuid)

    def test_file_get_include(self, file_uuid=None, md5='A7', sha1='A7', sha256='A7'):
        """Test file get."""
        if not file_uuid:
            file_uuid = self.file_create(md5=md5 * 16, sha1=sha1 * 20, sha256=sha256 * 32)

        self.test_file_add_attribute(
            file_uuid, attribute_type='Description', attribute_value='test123'
        )
        self.test_file_add_label(file_uuid, label='TLP:RED')
        self.test_file_add_tag(file_uuid, name='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.file(owner=tcex.args.tc_owner, unique_id=file_uuid)
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('file').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('file').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('file').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.test_file_delete(file_uuid)

    def file_create(self, md5, sha1, sha256):
        """Test file create."""
        ti = self.ti.file(owner=tcex.args.tc_owner, md5=md5, sha1=sha1, sha256=sha256)
        r = ti.create()
        assert r.status_code == 201
        ti_data = r.json()
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('file').get('md5', None) == md5
        assert ti_data.get('data').get('file').get('sha1', None) == sha1
        assert ti_data.get('data').get('file').get('sha256', None) == sha256

        if md5:
            return md5
        if sha1:
            return sha1
        if sha256:
            return sha256
        return None

    def test_file_add_attribute(
        self,
        file_uuid=None,
        md5='A9',
        sha1='A9',
        sha256='A9',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test file attribute add."""
        should_delete = False
        if not file_uuid:
            should_delete = True
            file_uuid = self.file_create(md5=md5 * 16, sha1=sha1 * 20, sha256=sha256 * 32)
        ti = self.ti.file(owner=tcex.args.tc_owner, unique_id=file_uuid)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value
        if should_delete:
            self.test_file_delete(file_uuid)

    def test_file_add_label(
        self, file_uuid=None, md5='B4', sha1='B4', sha256='B4', label='TLP:GREEN'
    ):
        """Test file attribute add."""
        should_delete = False
        if not file_uuid:
            should_delete = True
            file_uuid = self.file_create(md5=md5 * 16, sha1=sha1 * 20, sha256=sha256 * 32)
        ti = self.ti.file(owner=tcex.args.tc_owner, unique_id=file_uuid)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'
        if should_delete:
            self.test_file_delete(file_uuid)

    def test_file_add_tag(self, file_uuid=None, md5='B5', sha1='B5', sha256='B5', name='Crimeware'):
        """Test file attribute add."""
        should_delete = False
        if not file_uuid:
            should_delete = True
            file_uuid = self.file_create(md5=md5 * 16, sha1=sha1 * 20, sha256=sha256 * 32)
        ti = self.ti.file(owner=tcex.args.tc_owner, unique_id=file_uuid)
        r = ti.add_tag(name=name)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

        if should_delete:
            self.test_file_delete(file_uuid)

    def test_file_delete(self, file_uuid=None, md5='B6', sha1='B6', sha256='B6'):
        """Test file delete."""
        # create indicator
        if not file_uuid:
            file_uuid = self.file_create(md5=md5 * 16, sha1=sha1 * 20, sha256=sha256 * 32)
        ti = self.ti.file(owner=tcex.args.tc_owner, unique_id=file_uuid)
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_file_update(self, file_uuid=None, md5='B7', sha1='B7', sha256='B7'):
        """Test file update."""
        # create indicator
        if not file_uuid:
            file_uuid = self.file_create(md5=md5 * 16, sha1=sha1 * 20, sha256=sha256 * 32)
        ti = self.ti.file(owner=tcex.args.tc_owner, unique_id=file_uuid)
        r = ti.rating(5)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('file').get('rating') == 5.0

        r = ti.confidence(10)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('file').get('confidence') == 10

        # delete indicator
        self.test_file_delete(file_uuid)
