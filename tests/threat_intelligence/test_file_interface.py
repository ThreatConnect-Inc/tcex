# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os
from random import randint
import uuid
from datetime import datetime, timedelta

from .ti_helpers import TIHelper, TestThreatIntelligence


class TestFileIndicators(TestThreatIntelligence):
    """Test TcEx URL Indicators."""

    indicator_field = 'md5'
    indicator_field_arg = indicator_field.replace(' ', '_').lower()
    indicator_field_custom = 'md5'
    indicator_type = 'File'
    owner = os.getenv('TC_OWNER')
    ti = None
    ti_helper = None
    tcex = None

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.indicator_type, self.indicator_field_arg)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.ti_helper.cleanup()

    def tests_ti_file_create(self):
        """Create an indicator using specific interface."""
        indicator_data = {
            'md5': uuid.uuid4().hex.upper(),
            'owner': self.owner,
            'rating': randint(0, 5),
        }
        ti = self.ti.file(**indicator_data)
        r = ti.create()

        # assert response
        assert r.status_code == 201

        # retrieve indicator for asserts
        ti = self.ti.file(**indicator_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get('confidence') == indicator_data.get('confidence')
        assert ti_data.get(ti.api_entity) == indicator_data.get(ti.api_entity)
        assert ti_data.get('rating') == indicator_data.get('rating')

        # cleanup indicator
        r = ti.delete()
        assert r.status_code == 200

    def tests_ti_file_add_attribute(self, request):
        """Test indicator add attribute."""
        super().indicator_add_attribute(request)

    def tests_ti_file_add_label(self):
        """Test indicator add label."""
        super().indicator_add_label()

    def tests_ti_file_add_tag(self, request):
        """Test indicator add tag."""
        super().indicator_add_tag(request)

    def tests_ti_file_delete(self):
        """Test indicator delete."""
        super().indicator_delete()

    def tests_ti_file_get(self):
        """Test indicator get with generic indicator method."""
        super().indicator_get()

    def tests_ti_file_get_includes(self, request):
        """Test indicator get with includes."""
        super().indicator_get_includes(request)

    def tests_ti_file_get_attribute(self, request):
        """Test indicator get attribute."""
        super().indicator_get_attribute(request)

    def tests_ti_file_get_label(self):
        """Test indicator get label."""
        super().indicator_get_label()

    def tests_ti_file_get_tag(self, request):
        """Test indicator get tag."""
        super().indicator_get_tag(request)

    def tests_ti_file_update(self):
        """Test updating indicator metadata."""
        super().indicator_update()

    def tests_ti_file_add_occurrence(self):
        """Test updating indicator metadata."""
        file = self.ti_helper.create_indicator()
        response = file.add_occurrence(
            'pytest_occurrence', (datetime.now() - timedelta(days=2)).isoformat(), '.'
        )
        assert response.ok
        data = response.json().get('data').get('fileOccurrence')
        assert data.get('fileName') == 'pytest_occurrence'

    def tests_ti_file_get_occurrence(self):
        """Test retrieving file occurrence."""
        file = self.ti_helper.create_indicator()
        response = file.add_occurrence(
            'pytest_occurrence', (datetime.now() - timedelta(days=2)).isoformat(), '.'
        )
        assert response.ok
        occurrence_id = response.json().get('data').get('fileOccurrence').get('id')
        response = file.occurrence(occurrence_id)
        assert response.ok
        data = response.json().get('data').get('fileOccurrence')
        assert data.get('fileName') == 'pytest_occurrence'
        assert data.get('id') == occurrence_id

    def tests_ti_file_get_occurrences(self):
        """Test retrieving multiple file occurrences."""
        file = self.ti_helper.create_indicator()
        occurrence_names = ['pytest_occurrence_1', 'pytest_occurence_2']
        file.add_occurrence(
            occurrence_names[0], (datetime.now() - timedelta(days=2)).isoformat(), '.'
        )
        file.add_occurrence(
            occurrence_names[1], (datetime.now() - timedelta(days=2)).isoformat(), '.'
        )
        length = 0
        for occurrence in file.occurrences():
            length += 1
            assert occurrence.get('fileName') in occurrence_names
            occurrence_names.remove(occurrence.get('fileName'))
        assert length == 2

    def tests_ti_file_delete_occurrence(self):
        """Test deleting file occurrence."""
        file = self.ti_helper.create_indicator()
        response = file.add_occurrence(
            'pytest_occurrence', (datetime.now() - timedelta(days=2)).isoformat(), '.'
        )
        occurrence_id = response.json().get('data').get('fileOccurrence').get('id')
        response = file.occurrence(occurrence_id)
        assert response.ok

    def tests_ti_file_add_action(self):
        """Test adding file action."""
        file = self.ti_helper.create_indicator()
        indicator_data = {
            'confidence': randint(0, 100),
            'ip': self.ti_helper.rand_ip(),
            'owner': self.owner,
            'rating': randint(0, 5),
        }
        target = self.ti.address(**indicator_data)
        target.create()
        response = file.add_action('traffic', target)
        assert response.ok
        target.delete()

    def tests_ti_file_get_actions(self):
        """Test retrieving file actions."""
        file = self.ti_helper.create_indicator()
        action_targets = []
        ips = [self.ti_helper.rand_ip(), self.ti_helper.rand_ip()]
        indicator_data = {
            'confidence': randint(0, 100),
            'ip': ips[0],
            'owner': self.owner,
            'rating': randint(0, 5),
        }
        action_targets.append(self.ti.address(**indicator_data))
        indicator_data = {
            'confidence': randint(0, 100),
            'ip': ips[1],
            'owner': self.owner,
            'rating': randint(0, 5),
        }
        action_targets.append(self.ti.address(**indicator_data))
        for target in action_targets:
            target.create()
        action = 'traffic'
        file.add_action(action, action_targets[0])
        file.add_action(action, action_targets[1])
        length = 0
        for action in file.actions(action, self.ti.indicator()):
            length += 1
            assert action.get('summary') in ips
            ips.remove(action.get('summary'))
        assert length == 2
        for target in action_targets:
            target.delete()

    def tests_ti_file_delete_action(self):
        """Test deleting file action."""
        file = self.ti_helper.create_indicator()
        action = 'traffic'
        indicator_data = {
            'confidence': randint(0, 100),
            'ip': self.ti_helper.rand_ip(),
            'owner': self.owner,
            'rating': randint(0, 5),
        }
        target = self.ti.address(**indicator_data)
        target.create()
        file.add_action(action, target)
        response = file.delete_action(action, target)
        assert response.ok
        target.delete()
