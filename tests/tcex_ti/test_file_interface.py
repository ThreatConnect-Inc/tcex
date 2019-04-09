# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestFileIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_file_get(
        self,
        file_uuid=None,
        md5='58E58325FE5C06927EFE133BEDF3A3E1',
        sha1='1A619D8B2CDBE8C8DB25CEB2FD6B0048F7EFFFFB',
        sha256='07D4FB51C8E6A98BE2B3A4C3F3BD86C6C5C1E131D9E88D068844C9D91346F3CD',
    ):
        """Test file get."""
        # create
        if not file_uuid:
            file_uuid = self.file_create(md5=md5, sha1=sha1, sha256=sha256)

        # get
        ti = self.ti.file(unique_id=file_uuid)
        r = ti.single(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('file').get('md5', None) == md5
        assert ti_data.get('data').get('file').get('sha1', None) == sha1
        assert ti_data.get('data').get('file').get('sha256', None) == sha256

        # delete
        self.test_file_delete(file_uuid)

    def test_file_get_attributes(
        self,
        file_uuid=None,
        md5='11EAC23484821C361CB164604BB319C7',
        sha1='1865FB32B2942026FA6819AECC7E3B9768B61894',
        sha256='FAAEFA54AEA4F8BF081C5CE549CDE0F84616FAAD778FBD2D046EAAE80F26EC46',
    ):
        """Test file get."""
        # create
        if not file_uuid:
            file_uuid = self.file_create(md5, sha1, sha256)

        self.test_file_add_attribute(file_uuid, 'Description', 'test1')
        self.test_file_add_attribute(file_uuid, 'Description', 'test2')
        self.test_file_add_attribute(file_uuid, 'Description', 'test3')

        # get attributes
        ti = self.ti.file(unique_id=file_uuid)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.test_file_delete(file_uuid)

    def test_file_get_tags(
        self,
        file_uuid=None,
        md5='824B644C325BD186EBD3E9D7C2B5A5A4',
        sha1='F6951AD421E06EE0C2728C70F1ABC422BEEE84F4',
        sha256='61981BEF62B21AE9BF62952D9D09AC1799CF760571DA5368A06905003E66139A',
    ):
        """Test file get."""
        # create
        if not file_uuid:
            file_uuid = self.file_create(md5=md5, sha1=sha1, sha256=sha256)

        self.test_file_add_tag(file_uuid, 'One')
        self.test_file_add_tag(file_uuid, 'Two')

        # get tags
        ti = self.ti.file(unique_id=file_uuid)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.test_file_delete(file_uuid)

    def test_file_get_include(
        self,
        file_uuid=None,
        md5='4F9E206DBCEBD815AFF963D95207E09C',
        sha1='FB4952B1B0A2FBE439FB02F772B241A64983E501',
        sha256='4ED4293A63E793F40DD5CAACCA11CDD8F218DDCAE236A1B6ABBBD' '2FDD9AA5834',
    ):
        """Test file get."""
        if not file_uuid:
            file_uuid = self.file_create(md5=md5, sha1=sha1, sha256=sha256)

        self.test_file_add_attribute(
            file_uuid, attribute_type='Description', attribute_value='test123'
        )
        self.test_file_add_label(file_uuid, label='TLP:RED')
        self.test_file_add_tag(file_uuid, name='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.file(unique_id=file_uuid)
        r = ti.single(owner='TCI', params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('file').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('file').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('file').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.test_file_delete(file_uuid)

    def file_create(
        self,
        md5='D72E521FACF661631D47E751AF495715',
        sha1='CFADB8C73F414B1F7437E2999537B9C9C6FA257B',
        sha256='5626FE054EDCB0624BC164A0665CE55944F51EDD1FFD02E6BBA5958488895CA8',
    ):
        """Test file create."""
        ti = self.ti.file(md5=md5, sha1=sha1, sha256=sha256)
        r = ti.create('TCI')
        print(r)
        assert r.status_code == 201
        ti_data = r.json()
        print(ti_data)
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
        md5='F9478E2D303B09EB2875051CDAAB7704',
        sha1='E4893529FB7BD3D3995A58E81D3B8999B7B5D348',
        sha256='F725694888A3923C2092A0C4AC966235B52EAE8824ADCC2C4391409A7CE8382B',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test file attribute add."""
        should_delete = False
        if not file_uuid:
            should_delete = True
            file_uuid = self.file_create(md5, sha1, sha256)
        ti = self.ti.file(unique_id=file_uuid)
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value
        if should_delete:
            self.test_file_delete(file_uuid)

    def test_file_add_label(
        self,
        file_uuid=None,
        md5='07E2A5E97375C954C6F7A6AF76EAA81B',
        sha1='930FAC851C05B9571F2438A646D4C9A56903E4FE',
        sha256='8B612EEF234E51294D6F7F56E9EED00FEFD1E3A892D48CB7B34FBBA349A0295C',
        label='TLP:GREEN',
    ):
        """Test file attribute add."""
        should_delete = False
        if not file_uuid:
            should_delete = True
            file_uuid = self.file_create(md5, sha1, sha256)
        ti = self.ti.file(unique_id=file_uuid)
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'
        if should_delete:
            self.test_file_delete(file_uuid)

    def test_file_add_tag(
        self,
        file_uuid=None,
        md5='DDF6269CBE9958374D1833189BFF8CFA',
        sha1='9BCAC58BE766E5D5C6EDE97012D4FC761766B565',
        sha256='B18A65AE2B5967E06B823E8E7924000EE1578690B9CE1D93D4E2FC2E857FDE77',
        name='Crimeware',
    ):
        """Test file attribute add."""
        should_delete = False
        if not file_uuid:
            should_delete = True
            file_uuid = self.file_create(md5, sha1, sha256)
        ti = self.ti.file(unique_id=file_uuid)
        r = ti.add_tag(name=name)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

        if should_delete:
            self.test_file_delete(file_uuid)

    def test_file_delete(
        self,
        file_uuid=None,
        md5='4B51B1DFEA078D0014B997EDE0507EE7',
        sha1='367710D27B8B53A791A5687AC5EE5250740FEB86',
        sha256='7668A99D8233CD0A4D92021CF795430ABBE7AF29BCBB96754F278DC3B8686025',
    ):
        """Test file delete."""
        # create indicator
        if not file_uuid:
            file_uuid = self.file_create(md5, sha1, sha256)
        ti = self.ti.file(unique_id=file_uuid)
        r = ti.delete(owner='TCI')
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_file_update(
        self,
        file_uuid=None,
        md5='CDEF40E7795255D42184DCFC10E93A3A',
        sha1='41883B481AADA48BFAF8B61EB87C737FDE68B404',
        sha256='72C16007D15D3D3B01D50DFA54FBCD233F704193C1837075AB5E596CC1E2FFEC',
    ):
        """Test file update."""
        # create indicator
        if not file_uuid:
            file_uuid = self.file_create(md5, sha1, sha256)
        ti = self.ti.file(unique_id=file_uuid)
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
