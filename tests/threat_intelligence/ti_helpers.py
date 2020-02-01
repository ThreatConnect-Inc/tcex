# -*- coding: utf-8 -*-
"""Case Management PyTest Helper Method"""
import os
from random import randint

from ..mock_app import MockApp


class TIHelper:
    """Case Management Helper Module

    Args:
        cm_object (str): The name of the object (e.g., artifact) being tested.
    """

    def __init__(self, ti_type, ti_field):
        """Initialize Class Properties"""
        self.ti_type = ti_type
        self.ti_field = ti_field

        # properties
        self.app = MockApp(runtime_level='Playbook')
        self.tcex = self.app.tcex
        self.ti = self.tcex.ti

        # indicator_type_value_map
        self.im = {
            'Address': self.rand_ip,
            'ASN': self.rand_asn,
            'CIDR': self.rand_cidr,
            'Email Subject': self.rand_email_subject,
            'Hashtag': self.rand_hashtag,
            'Mutex': self.rand_mutex,
        }

        # cleanup values
        self.ti_objects = []

    @property
    def indicator_value(self):
        """Return a proper indicator value for the current indicator type."""
        return self.im.get(self.ti_type)()

    @staticmethod
    def rand_asn():
        """Return a random ASN."""
        return f'ASN{randint(1000, 9999)}'

    @staticmethod
    def rand_cidr():
        """Return a random CIDR block."""
        return f'{randint(0,255)}.{randint(0,255)}.{randint(0,255)}.0/{randint(16,24)}'

    def rand_email_subject(self):
        """Return a random email subject."""
        return (
            f'{self.tcex.utils.random_string(randint(5,15))} '
            f'{self.tcex.utils.random_string(randint(5,15))} '
            f'{self.tcex.utils.random_string(randint(5,15))}'
        )

    def rand_hashtag(self):
        """Return a random hashtag."""
        return f'#{self.tcex.utils.random_string(randint(5,15))}'.lower()

    @staticmethod
    def rand_ip():
        """Return a random IP address."""
        return f'222.{randint(0,255)}.{randint(0,255)}.{randint(0,255)}'

    def rand_mutex(self):
        """Return a random Mutex."""
        return f'Global\\{self.tcex.utils.random_string(randint(5,10))}'

    @staticmethod
    def rand_user_agent():
        """Return a random Mutex."""
        return (
            f'Mozilla/{randint(1,5)}.0 (Macintosh; Intel Mac OS X 10.8; rv:36.0) '
            f'Gecko/20100101 Firefox/{randint(1,36)}.0'
        )

    def create_indicator(self, indicator_type=None, **kwargs):
        """Create an case.

        If a case_name is not provide a dynamic case name will be used.

        Args:
            indicator_type (str, optional): The indicator type.
            asn_number (str, kwargs): [ASN] The value for this Indicator.
            attributes (dict|list, kwargs): An attribute or attributes to add to indicator.
            ip (str, kwargs): [address] The value for this Indicator.
            hashtag (str, kwargs): [hashtag] The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            owner (str, kwargs): The TC owner to using when adding TI.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            security_labels (dict|list, kwargs): A label or labels to add to indicator.
            tags (dict|list, kwargs): A tag or tags to add to indicator.

        Returns:
            TI: A TI object.
        """
        # use passed indicator type or global value
        it = indicator_type or self.ti_type
        indicator_value = kwargs.get(self.ti_type) or self.indicator_value

        # setup indicator data
        indicator_data = {
            self.ti_field: indicator_value,
            'confidence': kwargs.get('confidence') or randint(0, 100),
            'indicator_type': it,
            'owner': kwargs.get('owner') or os.getenv('TC_OWNER'),
            'rating': kwargs.get('rating') or randint(0, 5),
        }
        ti = self.ti.indicator(**indicator_data)

        # add the indicator data to the ti object to be accessed in test case
        setattr(ti, 'confidence', indicator_data.get('confidence'))
        setattr(ti, 'indicator', indicator_value)
        setattr(ti, 'rating', indicator_data.get('rating'))

        # store case id for cleanup
        self.ti_objects.append(ti)

        # create indicator
        r = ti.create()
        if not r.ok:
            raise RuntimeError(f'Failed to create indicator ({indicator_value}). Error: ({r.text})')

        # handle attribute inputs
        attributes = kwargs.pop('attributes', [])
        if isinstance(attributes, dict):
            attributes = [attributes]
        for attribute in attributes:
            ra = ti.add_attribute(**attribute)
            if not ra.ok:
                raise RuntimeError(f'Failed to add attribute ({attribute}). Error: ({ra.text})')

        # handle label inputs
        labels = kwargs.pop('labels', [])
        if isinstance(labels, dict):
            labels = [labels]
        for label in labels:
            rl = ti.add_label(**label)
            if not rl.ok:
                raise RuntimeError(f'Failed to add label ({label}). Error: ({rl.text})')

        # handle tag inputs
        tags = kwargs.pop('tags', [])
        if isinstance(tags, dict):
            tags = [tags]
        tags.append({'name': 'PyTest'})
        for tag in tags:
            rt = ti.add_tag(**tag)
            if not rt.ok:
                raise RuntimeError(f'Failed to add tag ({tag}). Error: ({rt.text})')

        return ti

    def cleanup(self):
        """Remove all cases and child data."""
        for obj in self.ti_objects:
            obj.delete()


class TestThreatIntelligence:
    """Test TcEx Threat Intelligence Base Class"""

    indicator_field = None
    indicator_field_arg = None
    indicator_type = None
    owner = None
    ti = None
    ti_helper = None

    def indicator_add_attribute(self, request):
        """Create a attribute on an indicator."""
        helper_ti = self.ti_helper.create_indicator()

        attribute_data = {
            'attribute_type': 'Description',
            'attribute_value': request.node.name,
            'source': request.node.name,
            'displayed': True,
        }
        r = helper_ti.add_attribute(**attribute_data)
        response_data = r.json()
        ti_data = response_data.get('data', {}).get('attribute')

        # assert response
        assert r.status_code == 201
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('type') == attribute_data.get('attribute_type')
        assert ti_data.get('value') == attribute_data.get('attribute_value')
        assert ti_data.get('displayed') == attribute_data.get('displayed')

    def indicator_add_label(self):
        """Create a label on an indicator."""
        helper_ti = self.ti_helper.create_indicator()

        r = helper_ti.add_label(label='TLP:GREEN')
        response_data = r.json()

        # assert response
        assert r.status_code == 201
        assert response_data.get('status') == 'Success'

    def indicator_add_tag(self, request):
        """Create a tag on an indicator."""
        helper_ti = self.ti_helper.create_indicator()

        r = helper_ti.add_tag(request.node.name)
        response_data = r.json()

        # assert response
        assert r.status_code == 201
        assert response_data.get('status') == 'Success'

    def indicator_delete(self):
        """Delete indicator."""
        helper_ti = self.ti_helper.create_indicator()

        # indicator for delete
        indicator_data = {
            self.indicator_field_arg: helper_ti.indicator,
            'indicator_type': self.indicator_type,
            'owner': helper_ti.owner,
        }
        ti = self.ti.indicator(**indicator_data)
        r = ti.delete()
        response_data = r.json()

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

    def indicator_get(self):
        """Get indicator with generic indicator method."""
        helper_ti = self.ti_helper.create_indicator()

        # retrieve the indicator
        indicator_data = {
            self.indicator_field_arg: helper_ti.indicator,
            'indicator_type': self.indicator_type,
            'owner': helper_ti.owner,
        }
        ti = self.ti.indicator(**indicator_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('confidence') == helper_ti.confidence, (
            f"confidence value ({ti_data.get('confidence')}) doe not match"
            f'expected value of ({helper_ti.confidence})'
        )
        assert ti_data.get(self.indicator_field) == helper_ti.indicator, (
            f'indicator value ({ti_data.get(self.indicator_field)}) doe not match'
            f'expected value of ({helper_ti.indicator})'
        )
        assert ti_data.get('rating') == helper_ti.rating, (
            f"rating value ({ti_data.get('rating')}) doe not match"
            f'expected value of ({helper_ti.rating})'
        )

    def indicator_get_includes(self, request):
        """Get indicator with includes."""
        attribute_data = {
            'attribute_type': 'Description',
            'attribute_value': request.node.name,
        }
        label_data = {'label': 'TLP:RED'}
        tag_data = {'name': request.node.name}
        helper_ti = self.ti_helper.create_indicator(
            attributes=attribute_data, labels=label_data, tags=tag_data
        )

        # retrieve the indicator
        indicator_data = {
            self.indicator_field_arg: helper_ti.indicator,
            'indicator_type': self.indicator_type,
            'owner': helper_ti.owner,
        }
        ti = self.ti.indicator(**indicator_data)
        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        r = ti.single(params=parameters)
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('confidence') == helper_ti.confidence, (
            f"confidence value ({ti_data.get('confidence')}) doe not match"
            f'expected value of ({helper_ti.confidence})'
        )
        assert ti_data.get(self.indicator_field) == helper_ti.indicator, (
            f'indicator value ({ti_data.get(self.indicator_field)}) doe not match'
            f'expected value of ({helper_ti.indicator})'
        )
        assert ti_data.get('rating') == helper_ti.rating, (
            f"rating value ({ti_data.get('rating')}) doe not match"
            f'expected value of ({helper_ti.rating})'
        )

        # validate metadata
        assert ti_data.get('attribute')[0].get('value') == attribute_data.get('attribute_value'), (
            f"attribute value {ti_data.get('attribute')[0].get('value')} does not match"
            f"expected value {attribute_data.get('attribute_value')}"
        )
        assert ti_data.get('securityLabel')[0].get('name') == label_data.get('label'), (
            f"label value {ti_data.get('securityLabel')[0].get('name')} does not match"
            f"expected value {label_data.get('label')}"
        )
        for tag in ti_data.get('tag'):
            if tag.get('name') == tag_data.get('name'):
                break
        else:
            assert False, f"Could not find tag {tag_data.get('name')}"

    def indicator_get_attribute(self, request):
        """Get attributes for an indicator."""
        attribute_data = {
            'attribute_type': 'Description',
            'attribute_value': request.node.name,
        }
        helper_ti = self.ti_helper.create_indicator(attributes=attribute_data)

        # retrieve the indicator
        indicator_data = {
            self.indicator_field_arg: helper_ti.indicator,
            'indicator_type': self.indicator_type,
            'owner': helper_ti.owner,
        }
        ti = self.ti.indicator(**indicator_data)
        for attribute in ti.attributes():
            if attribute.get('value') == request.node.name:
                break
        else:
            assert False, f'Could not find attribute with value {request.node.name}'

    def indicator_get_label(self):
        """Get tags for an indicator."""
        label_data = {'label': 'TLP:RED'}
        helper_ti = self.ti_helper.create_indicator(labels=label_data)

        # retrieve the indicator
        indicator_data = {
            self.indicator_field_arg: helper_ti.indicator,
            'indicator_type': self.indicator_type,
            'owner': helper_ti.owner,
        }
        ti = self.ti.indicator(**indicator_data)
        for label in ti.labels():
            if label.get('name') == label_data.get('label'):
                break
        else:
            assert False, f"Could not find tag with value {label_data.get('label')}"

    def indicator_get_tag(self, request):
        """Get tags for an indicator."""
        tag_data = {'name': request.node.name}
        helper_ti = self.ti_helper.create_indicator(tags=tag_data)

        # retrieve the indicator
        indicator_data = {
            self.indicator_field_arg: helper_ti.indicator,
            'indicator_type': self.indicator_type,
            'owner': helper_ti.owner,
        }
        ti = self.ti.indicator(**indicator_data)
        for tag in ti.tags():
            if tag.get('name') == request.node.name:
                break
        else:
            assert False, f'Could not find tag with value {request.node.name}'

    def indicator_update(self):
        """Test updating indicator metadata."""
        helper_ti = self.ti_helper.create_indicator()

        # update indicator
        indicator_data = {
            self.indicator_field_arg: helper_ti.indicator,
            'confidence': 100,
            'indicator_type': self.indicator_type,
            'owner': self.owner,
            'rating': 5,
        }
        ti = self.ti.indicator(**indicator_data)
        r = ti.update()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        expected_status_code = 200
        expected_status = 'Success'
        assert r.status_code == expected_status_code, (
            f'status code ({r.status_code}) does not match '
            f'expected code of ({expected_status_code}).'
        )
        assert response_data.get('status') == expected_status, (
            f"status ({response_data.get('status')}) does not "
            f'match expected status of ({expected_status})'
        )
        print(ti_data)
        print(self.indicator_field)

        # validate ti data
        assert ti_data.get('confidence') == indicator_data.get('confidence'), (
            f"confidence value ({ti_data.get('confidence')}) doe not match"
            f"expected value of ({indicator_data.get('confidence')})"
        )
        assert ti_data.get(self.indicator_field) == helper_ti.indicator, (
            f'indicator value ({ti_data.get(self.indicator_field)}) doe not match'
            f'expected value of ({helper_ti.indicator})'
        )
        assert ti_data.get('rating') == indicator_data.get('rating'), (
            f"rating value ({ti_data.get('rating')}) doe not match"
            f"expected value of ({indicator_data.get('rating')})"
        )
