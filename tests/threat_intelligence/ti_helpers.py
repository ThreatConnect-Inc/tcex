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
            'Address': self._rand_ip,
            'ASN': self._rand_asn,
            'Hashtag': self._rand_hashtag,
        }

        # cleanup values
        self.ti_objects = []

    @property
    def _indicator_value(self):
        """Return a proper indicator value for the current indicator type."""
        return self.im.get(self.ti_type)()

    @staticmethod
    def _rand_asn():
        """Return a random IP ASN."""
        return f'ASN{randint(1000, 9999)}'

    def _rand_hashtag(self):
        """Return a random IP hashtag."""
        return f'#{self.tcex.utils.random_string(randint(5,15))}'

    @staticmethod
    def _rand_ip():
        """Return a random IP address."""
        return f'222.{randint(0,255)}.{randint(0,255)}.{randint(0,255)}'

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
        indicator_value = kwargs.get(self.ti_type) or self._indicator_value

        # setup indicator data
        indicator_data = {
            self.ti_field.lower(): indicator_value,
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

    api_entity = None
    indicator_field = None
    indicator_type = None
    owner = None
    ti = None
    ti_helper = None

    def indicator_get_tag(self, request):
        """Get tags for an indicator."""
        tag_data = {'name': request.node.name}
        helper_ti = self.ti_helper.create_indicator(tags=tag_data)

        # retrieve the indicator
        indicator_data = {
            self.indicator_field: helper_ti.indicator,
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
            self.indicator_field: helper_ti.indicator,
            'confidence': 100,
            'indicator_type': self.indicator_type,
            'owner': self.owner,
            'rating': 5,
        }
        ti = self.ti.indicator(**indicator_data)
        r = ti.update()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(self.api_entity)

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
