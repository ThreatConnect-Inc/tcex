# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestEmailGroups:
    """Test TcEx Host Groups."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.ti = tcex.ti

    def test_email_get(
        self,
        name='email-name-42353',
        to='email-to-asdf@gmail.com',
        from_addr='email-from-fdsav@gmail.com',
        subject='email-subject-bfd21',
        body='email-body-fdsab',
        header='email-header-bfd32r',
    ):
        """Test email get."""
        # create
        email_id = self.email_create(name, to, from_addr, subject, body, header)

        # get
        ti = self.ti.email(
            name, to, from_addr, subject, body, header, owner=tcex.args.tc_owner, unique_id=email_id
        )  # pylint: disable=E1121
        r = ti.single()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get(ti.api_entity).get('name') == name

        # delete
        self.email_delete(email_id)

    def test_email_get_attributes(
        self,
        email_id=None,
        name='email-name-12453',
        to='email-to-asdf@gmail.com',
        from_addr='email-from-fdsav@gmail.com',
        subject='email-subject-bfd21',
        body='email-body-fdsab',
        header='email-header-bfd32r',
    ):
        """Test email get."""
        # create
        if not email_id:
            email_id = self.email_create(name, to, from_addr, subject, body, header)
        self.test_email_add_attribute(
            email_id=email_id, attribute_type='Description', attribute_value='test1'
        )
        self.test_email_add_attribute(
            email_id=email_id, attribute_type='Description', attribute_value='test2'
        )
        self.test_email_add_attribute(
            email_id=email_id, attribute_type='Description', attribute_value='test3'
        )

        # get attributes
        ti = self.ti.email(
            name, to, from_addr, subject, body, header, owner=tcex.args.tc_owner, unique_id=email_id
        )
        for attribute in ti.attributes():
            assert attribute
            break
        else:
            assert False

        # delete
        self.email_delete(email_id)

    def test_email_get_tags(
        self,
        email_id=None,
        name='email-name-64235',
        to='email-to-asdf@gmail.com',
        from_addr='email-from-fdsav@gmail.com',
        subject='email-subject-bfd21',
        body='email-body-fdsab',
        header='email-header-bfd32r',
    ):
        """Test email get."""
        # create
        if not email_id:
            email_id = self.email_create(name, to, from_addr, subject, body, header)
        self.test_email_add_tag(email_id=email_id, tag='One')
        self.test_email_add_tag(email_id=email_id, tag='Two')

        # get tags
        ti = self.ti.email(
            name, to, from_addr, subject, body, header, owner=tcex.args.tc_owner, unique_id=email_id
        )
        for tag in ti.tags():
            assert tag.get('name')
            break
        else:
            assert False

        # delete
        self.email_delete(email_id)

    def test_email_get_include(
        self,
        name='email-name-78159',
        to='email-to-fdsabv@gmail.com',
        from_addr='email-from-gfasa@gmail.com',
        subject='email-subject-fds32g',
        body='email-body-165few',
        header='email-header-fdy453',
    ):
        """Test email get."""
        email_id = self.email_create(name, to, from_addr, subject, body, header)
        self.test_email_add_attribute(
            email_id=email_id, attribute_type='Description', attribute_value='test123'
        )
        self.test_email_add_label(email_id=email_id, label='TLP:RED')
        self.test_email_add_tag(email_id=email_id, tag='PyTest')

        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        ti = self.ti.email(
            name, to, from_addr, subject, body, header, owner=tcex.args.tc_owner, unique_id=email_id
        )
        r = ti.single(params=parameters)
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('email').get('name') == name
        assert ti_data.get('data').get('email').get('attribute')[0].get('value') == 'test123'
        assert ti_data.get('data').get('email').get('securityLabel')[0].get('name') == 'TLP:RED'
        assert ti_data.get('data').get('email').get('tag')[0].get('name') == 'PyTest'

        # delete
        self.email_delete(email_id)

    def email_create(
        self,
        name='email-name-65341',
        to='email-to-t42gad@gmail.com',
        from_addr='email-from-bfds3@gmail.com',
        subject='email-subject-fdsab2',
        body='email-body-fd23fb',
        header='email-header-32fsa',
    ):
        """Test email create."""
        ti = self.ti.email(name, to, from_addr, subject, body, header, owner=tcex.args.tc_owner)
        r = ti.create()
        ti_data = r.json()
        assert r.status_code == 201
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('email').get('name') == name
        return ti.unique_id

    def test_email_add_attribute(
        self,
        name='email-name-fdsab5',
        to='email-to-fdsabv@gmail.com',
        from_addr='email-from-gfasa@gmail.com',
        subject='email-subject-fds32g',
        body='email-body-165few',
        header='email-header-fdy453',
        email_id=None,
        attribute_type='Description',
        attribute_value='Example Description.',
    ):
        """Test email attribute add."""
        should_delete = False
        if not email_id:
            should_delete = True
            email_id = self.email_create(name, to, from_addr, subject, body, header)

        ti = self.ti.email(
            None, None, None, None, None, None, owner=tcex.args.tc_owner, unique_id=email_id
        )
        r = ti.add_attribute(attribute_type=attribute_type, attribute_value=attribute_value)
        attribute_data = r.json()
        assert r.status_code == 201
        assert attribute_data.get('status') == 'Success'
        assert attribute_data.get('data').get('attribute').get('value') == attribute_value

        if should_delete:
            self.email_delete(email_id)

    def test_email_add_label(
        self,
        email_id=None,
        name='email-name-ds4vb',
        to='email-to-fdsabv@gmail.com',
        from_addr='email-from-gfasa@gmail.com',
        subject='email-subject-fds32g',
        body='email-body-165few',
        header='email-header-fdy453',
        label='TLP:GREEN',
    ):
        """Test email attribute add."""
        should_delete = False
        if not email_id:
            should_delete = True
            email_id = self.email_create(name, to, from_addr, subject, body, header)

        ti = self.ti.email(
            name, to, from_addr, subject, body, header, owner=tcex.args.tc_owner, unique_id=email_id
        )
        r = ti.add_label(label=label)
        label_data = r.json()
        assert r.status_code == 201
        assert label_data.get('status') == 'Success'

        if should_delete:
            self.email_delete(email_id)

    def test_email_add_tag(
        self,
        email_id=None,
        name='email-name-fdsv23',
        to='email-to-fdsabv@gmail.com',
        from_addr='email-from-gfasa@gmail.com',
        subject='email-subject-fds32g',
        body='email-body-165few',
        header='email-header-fdy453',
        tag='Crimeware',
    ):
        """Test email attribute add."""
        should_delete = False
        if not email_id:
            should_delete = True
            email_id = self.email_create(name, to, from_addr, subject, body, header)

        ti = self.ti.email(
            name, to, from_addr, subject, body, header, owner=tcex.args.tc_owner, unique_id=email_id
        )
        r = ti.add_tag(tag)
        tag_data = r.json()
        assert r.status_code == 201
        assert tag_data.get('status') == 'Success'

        if should_delete:
            self.email_delete(email_id)

    def email_delete(
        self,
        email_id=None,
        name='email-name-bdsfd',
        to='email-to-fdsabv@gmail.com',
        from_addr='email-from-gfasa@gmail.com',
        subject='email-subject-fds32g',
        body='email-body-165few',
        header='email-header-fdy453',
    ):
        """Test email delete."""
        # create indicator
        if not email_id:
            email_id = self.email_create(name, to, from_addr, subject, body, header)

        # delete indicator
        ti = self.ti.email(
            name, to, from_addr, subject, body, header, owner=tcex.args.tc_owner, unique_id=email_id
        )
        r = ti.delete()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'

    def test_email_update(
        self,
        email_id=None,
        name='email-name-b3da3',
        to='email-to-fdsabv@gmail.com',
        from_addr='email-from-gfasa@gmail.com',
        subject='email-subject-fds32g',
        body='email-body-165few',
        header='email-header-fdy453',
    ):
        """Test email update."""
        # create indicator
        if not email_id:
            email_id = self.email_create(name, to, from_addr, subject, body, header)

        # update indicator
        name = 'email-name-cj98fdsa'
        to = 'email-to-bfdsa@gmail.com'
        from_addr = 'email-from-bfdsa@gmail.com'
        subject = 'email-subject-j980as'
        body = 'email-body-fdsat3'
        header = 'email-header-jk23gf'
        ti = self.ti.email(
            name, to, from_addr, subject, body, header, owner=tcex.args.tc_owner, unique_id=email_id
        )
        r = ti.update()
        ti_data = r.json()
        assert r.status_code == 200
        assert ti_data.get('status') == 'Success'
        assert ti_data.get('data').get('email').get('name') == name
        assert ti_data.get('data').get('email').get('from') == from_addr
        assert ti_data.get('data').get('email').get('subject') == subject
        assert ti_data.get('data').get('email').get('body') == body
        assert ti_data.get('data').get('email').get('header') == header

        # delete indicator
        self.email_delete(email_id)
