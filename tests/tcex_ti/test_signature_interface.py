# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestAdversaryGroups:
    """Test TcEx Host Groups."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_signature_get(
        self,
        signature_id=None,
        name='signature-name-42353',
        file_name='signature-file-name-fdasr',
        file_type='Snort',
        file_content='signature-file-content-t5r32',
    ):
        """Test signature get."""
        # create
        if not signature_id:
            signature_id = self.signature_create(name, file_name, file_type, file_content)

        # get
        ti = self.ti.signature(
            name,
            file_name,
            file_type,
            file_content,
            owner=tcex.args.tc_owner,
            unique_id=signature_id,
        )
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('name') == name

        # delete
        self.signature_delete(signature_id)

    def test_signature_get_attributes(
        self,
        signature_id=None,
        name='signature-name-12453',
        file_name='signature-file-name-fdasr',
        file_type='Snort',
        file_content='signature-file-content-t5r32',
    ):
        """Test signature get."""
        # create
        if not signature_id:
            signature_id = self.signature_create(name, file_name, file_type, file_content)

        self.test_signature_add_attribute(
            signature_id=signature_id, attribute_type='Description', attribute_value='test1'
        )
        self.test_signature_add_attribute(
            signature_id=signature_id, attribute_type='Description', attribute_value='test2'
        )
        self.test_signature_add_attribute(
            signature_id=signature_id, attribute_type='Description', attribute_value='test3'
        )

        # get attributes
        ti = self.ti.signature(name, file_name, file_type, file_content, unique_id=signature_id)
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.signature_delete(signature_id)

    def test_signature_get_tags(
        self,
        signature_id=None,
        name='signature-name-64235',
        file_name='signature-file-name-fdasr',
        file_type='Snort',
        file_content='signature-file-content-t5r32',
    ):
        """Test signature get."""
        # create
        if not signature_id:
            signature_id = self.signature_create(name, file_name, file_type, file_content)

        self.test_signature_add_tag(signature_id=signature_id, tag='One')
        self.test_signature_add_tag(signature_id=signature_id, tag='Two')

        # get tags
        ti = self.ti.signature(name, file_name, file_type, file_content, unique_id=signature_id)
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.signature_delete(signature_id)

    def test_signature_get_include(
        self,
        signature_id=None,
        name='signature-name-78159',
        file_name='signature-file-name-fdasr',
        file_type='Snort',
        file_content='signature-file-content-t5r32',
    ):
        """Test signature get."""
        if not signature_id:
            signature_id = self.signature_create(name, file_name, file_type, file_content)

        self.test_signature_add_attribute(
            signature_id=signature_id, attribute_type='Description', attribute_value='test123'
        )
        self.test_signature_add_label(signature_id=signature_id, label='TLP:RED')
        self.test_signature_add_tag(signature_id=signature_id, tag='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.signature(name, file_name, file_type, file_content, unique_id=signature_id)
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('signature').get('name') == name
        assert ti_data.get('data').get('signature').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('signature').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('signature').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.signature_delete(signature_id)

    def signature_create(
        self,
        name='signature-name-65341',
        file_name='signature-file-name-fdasr',
        file_type='Snort',
        file_content='signature-file-content-t5r32',
    ):
        """Test signature create."""
        ti = self.ti.signature(name, file_name, file_type, file_content, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('signature').get('name') == name
        assert ti_data.get('data').get('signature').get('fileName') == file_name
        assert ti_data.get('data').get('signature').get('fileType') == file_type
        return ti.unique_id

    def test_signature_add_attribute(
        self,
        signature_id=None,
        name='signature-name-nkjvb',
        file_name='signature-file-name-fdasr',
        file_type='Snort',
        file_content='signature-file-content-t5r32',
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test signature attribute add."""

        should_delete = False
        if not signature_id:
            should_delete = True
            signature_id = self.signature_create(name, file_name, file_type, file_content)

        ti = self.ti.signature(
            name,
            file_name,
            file_type,
            file_content,
            owner=tcex.args.tc_owner,
            unique_id=signature_id,
        )
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value
        if should_delete:
            self.signature_delete(signature_id)

    def test_signature_add_label(
        self,
        signature_id=None,
        name='signature-name-ds4vb',
        file_name='signature-file-name-fdasr',
        file_type='Snort',
        file_content='signature-file-content-t5r32',
        label='TLP:GREEN',
    ):
        """Test signature attribute add."""
        should_delete = False
        if not signature_id:
            should_delete = True
            signature_id = self.signature_create(name, file_name, file_type, file_content)

        ti = self.ti.signature(
            name,
            file_name,
            file_type,
            file_content,
            owner=tcex.args.tc_owner,
            unique_id=signature_id,
        )
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'
        if should_delete:
            self.signature_delete(signature_id)

    def test_signature_add_tag(
        self,
        signature_id=None,
        name='signature-name-fdsv23',
        file_name='signature-file-name-fdasr',
        file_type='Snort',
        file_content='signature-file-content-t5r32',
        tag='Crimeware',
    ):
        """Test signature attribute add."""
        should_delete = False
        if not signature_id:
            should_delete = True
            signature_id = self.signature_create(name, file_name, file_type, file_content)

        ti = self.ti.signature(
            name,
            file_name,
            file_type,
            file_content,
            owner=tcex.args.tc_owner,
            unique_id=signature_id,
        )
        r = ti.add_tag(tag)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'
        if should_delete:
            self.signature_delete(signature_id)

    def signature_delete(
        self,
        signature_id=None,
        name='signature-name-bdsfd',
        file_name='signature-file-name-fdasr',
        file_type='Snort',
        file_content='signature-file-content-t5r32',
    ):
        """Test signature delete."""
        # create indicator
        if not signature_id:
            signature_id = self.signature_create(name, file_name, file_type, file_content)

        # delete indicator
        ti = self.ti.signature(
            name,
            file_name,
            file_type,
            file_content,
            owner=tcex.args.tc_owner,
            unique_id=signature_id,
        )
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_signature_update(
        self,
        signature_id=None,
        name='signature-name-b3da3',
        file_name='signature-file-name-fdasr',
        file_type='Snort',
        file_content='signature-file-content-t5r32',
    ):
        """Test signature update."""
        # create indicator
        if not signature_id:
            signature_id = self.signature_create(name, file_name, file_type, file_content)

        name = 'signature-new-name-fdasb3'

        # update indicator
        ti = self.ti.signature(
            name,
            'signature-file-name.txt',
            'Bro',
            file_content,
            owner=tcex.args.tc_owner,
            unique_id=signature_id,
        )
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('signature').get('name') == name
        assert ti_data.get('data').get('signature').get('fileName') == 'signature-file-name.txt'
        assert ti_data.get('data').get('signature').get('fileType') == 'Bro'
        r = ti.download()
        assert r.status_code == 200

        # delete indicator
        self.signature_delete(signature_id)
