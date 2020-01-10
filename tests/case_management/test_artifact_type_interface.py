# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os
from tcex.case_management.tql import TQL

from ..tcex_init import tcex
from .cm_helpers import CMHelper


class TestArtifactType:
    """Test TcEx CM Artifact Type Interface."""

    cm = None
    cm_helper = None
    test_obj = None
    test_obj_collection = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm
        self.test_obj = self.cm.artifact_type()
        self.test_obj_collection = self.cm.artifact_types()

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper(self.cm)

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_artifact_type_properties(self):
        """Test Artifacts properties."""
        r = tcex.session.options(self.test_obj.api_endpoint, params={'show': 'readOnly'})
        for prop_string, prop_data in r.json().items():
            prop_read_only = prop_data.get('read-only', False)
            prop_string = self.cm_helper.camel_to_snake(prop_string)

            # ensure class has property
            assert hasattr(
                self.test_obj, prop_string
            ), f'Missing {prop_string} property. read-only: {prop_read_only}'

    def test_artifact_types_filter_methods(self):
        """Test Artifacts filter methods."""
        r = tcex.session.options(f'{self.test_obj.api_endpoint}/tql', params={})

        for data in r.json().get('data'):
            keyword = data.get('keyword')

            if keyword not in self.test_obj_collection.filter.keywords:
                assert False, f'Missing TQL keyword {keyword}.'

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
        assert artifact_type.name == 'E-mail Address'
        assert artifact_type.description.startswith('A name that identifies')
        assert artifact_type.data_type == 'String'
        assert artifact_type.intel_type == 'indicator-EmailAddress'

    def test_artifact_type_get_by_tql_filter_active(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.active(TQL.Operator.EQ, True)

        for artifact_type in artifact_types:
            if artifact_type.id == 1:
                assert artifact_type.name == 'E-mail Address'
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
                assert artifact_type.name == 'E-mail Address'
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
            assert artifact_type.name == 'E-mail Address'
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
            assert artifact_type.name == 'E-mail Address'
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
            assert artifact_type.name == 'E-mail Address'
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
                assert artifact_type.name == 'E-mail Address'
                assert artifact_type.description.startswith('A name that identifies')
                assert artifact_type.data_type == 'String'
                assert artifact_type.intel_type == 'indicator-EmailAddress'
                break
        else:
            assert False, 'No artifact type returned for TQL'

    def test_artifact_type_get_by_tql_filter_name(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.name(TQL.Operator.EQ, 'E-mail Address')

        for artifact_type in artifact_types:
            assert artifact_type.name == 'E-mail Address'
            assert artifact_type.description.startswith('A name that identifies')
            assert artifact_type.data_type == 'String'
            assert artifact_type.intel_type == 'indicator-EmailAddress'
            break
        else:
            assert False, 'No artifact type returned for TQL'

    def test_artifact_type_get_by_tql_filter_tql(self):
        """Test Artifact Type Get by TQL"""
        artifact_types = self.cm.artifact_types()
        artifact_types.filter.tql('name EQ "E-mail Address"')

        for artifact_type in artifact_types:
            assert artifact_type.name == 'E-mail Address'
            assert artifact_type.description.startswith('A name that identifies')
            assert artifact_type.data_type == 'String'
            assert artifact_type.intel_type == 'indicator-EmailAddress'
            break
        else:
            assert False, 'No artifact type returned for TQL'

    # TODO: MJ is checking if this can be removed
    def test_artifact_type_get_by_tql_filter_ui_element(self, request):
        """Test Artifact Type Get by TQL"""
