# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
# standard library
import os

# first-party
from tcex.case_management.tql import TQL

from .cm_helpers import CMHelper, TestCaseManagement


class TestArtifactType(TestCaseManagement):
    """Test TcEx CM Artifact Type Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper('artifact_type')
        self.cm = self.cm_helper.cm
        self.tcex = self.cm_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_artifact_type_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_artifact_type_code_gen(self):
        """Generate code and docstring from Options methods.

        This is not truly a test case, but best place to store it for now.
        """
        doc_string, filter_map, filter_class = super().obj_code_gen()
        assert doc_string
        assert filter_map
        assert filter_class

    def test_artifact_type_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_artifact_type_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_artifact_type_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_artifact_type_get_many(self):
        """Tests getting all artifact types"""
        artifact_types = self.cm.artifact_types()
        for artifact_type in artifact_types:
            if artifact_type.name == 'Protocol Number':
                assert artifact_type.api_endpoint == '/v3/artifactTypes'
                assert artifact_type.data_type == 'String'
                assert artifact_type.description.startswith('In the Internet Protocol')
                break
        else:
            assert False, 'Artifact type of "Protocol Number" was not returned.'

    def test_artifact_type_get_single(self):
        """Tests Artifact Type Get by Id"""
        artifact_type = self.cm.artifact_type(id=1)
        artifact_type.get()

        assert artifact_type.id == 1
        assert artifact_type.name == 'Email Address'
        assert artifact_type.description.startswith('A name that identifies')
        assert artifact_type.data_type == 'String'
        assert artifact_type.intel_type == 'indicator-EmailAddress'

    def test_artifact_type_get_by_tql_filter_active(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.active(TQL.Operator.EQ, True)

        for artifact_type in artifact_types:
            if artifact_type.id == 1:
                assert artifact_type.name == 'Email Address'
                assert artifact_type.description.startswith('A name that identifies')
                assert artifact_type.data_type == 'String'
                assert artifact_type.intel_type == 'indicator-EmailAddress'
                break
        else:
            assert False, 'No artifact type returned for TQL'

    def test_artifact_type_get_by_tql_filter_data_type(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.data_type(TQL.Operator.EQ, 'String')

        for artifact_type in artifact_types:
            if artifact_type.id == 1:
                assert artifact_type.name == 'Email Address'
                assert artifact_type.description.startswith('A name that identifies')
                assert artifact_type.data_type == 'String'
                assert artifact_type.intel_type == 'indicator-EmailAddress'
                break
        else:
            assert False, 'No artifact type returned for TQL'

    def test_artifact_type_get_by_tql_filter_description(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.description(
            TQL.Operator.EQ,
            'A name that identifies an electronic post office box on '
            'a network where Electronic-Mail (e-mail) can be sent.',
        )

        for artifact_type in artifact_types:
            assert artifact_type.name == 'Email Address'
            assert artifact_type.description.startswith('A name that identifies')
            assert artifact_type.data_type == 'String'
            assert artifact_type.intel_type == 'indicator-EmailAddress'
            break
        else:
            assert False, 'No artifact type returned for TQL'

    def test_artifact_type_get_by_tql_filter_id(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.id(TQL.Operator.EQ, 1)

        for artifact_type in artifact_types:
            assert artifact_type.name == 'Email Address'
            assert artifact_type.description.startswith('A name that identifies')
            assert artifact_type.data_type == 'String'
            assert artifact_type.intel_type == 'indicator-EmailAddress'
            break
        else:
            assert False, 'No artifact type returned for TQL'

    def test_artifact_type_get_by_tql_filter_intel_type(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.intel_type(TQL.Operator.EQ, 'indicator-EmailAddress')

        for artifact_type in artifact_types:
            assert artifact_type.name == 'Email Address'
            assert artifact_type.description.startswith('A name that identifies')
            assert artifact_type.data_type == 'String'
            assert artifact_type.intel_type == 'indicator-EmailAddress'
            break
        else:
            assert False, 'No artifact type returned for TQL'

    def test_artifact_type_get_by_tql_filter_managed(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.managed(TQL.Operator.EQ, True)

        for artifact_type in artifact_types:
            if artifact_type.id == 1:
                assert artifact_type.name == 'Email Address'
                assert artifact_type.description.startswith('A name that identifies')
                assert artifact_type.data_type == 'String'
                assert artifact_type.intel_type == 'indicator-EmailAddress'
                break
        else:
            assert False, 'No artifact type returned for TQL'

    def test_artifact_type_get_by_tql_filter_name(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.name(TQL.Operator.EQ, 'Email Address')

        for artifact_type in artifact_types:
            assert artifact_type.name == 'Email Address'
            assert artifact_type.description.startswith('A name that identifies')
            assert artifact_type.data_type == 'String'
            assert artifact_type.intel_type == 'indicator-EmailAddress'
            break
        else:
            assert False, 'No artifact type returned for TQL'

    def test_artifact_type_get_by_tql_filter_tql(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.tql('name EQ "Email Address"')

        for artifact_type in artifact_types:
            assert artifact_type.name == 'Email Address'
            assert artifact_type.description.startswith('A name that identifies')
            assert artifact_type.data_type == 'String'
            assert artifact_type.intel_type == 'indicator-EmailAddress'
            assert artifact_type.as_entity.get('value') == 'Email Address'
            break
        else:
            assert False, 'No artifact type returned for TQL'

    # TODO: MJ is checking if this can be removed
    def test_artifact_type_get_by_tql_filter_ui_element(self, request):
        """Test Artifact Type Get by TQL"""
