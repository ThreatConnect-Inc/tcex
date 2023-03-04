"""Test the TcEx API Module."""
# third-party
import pytest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestArtifactTypes(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('artifact_types')

    def test_artifact_type_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_artifact_type_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_artifact_type_object_properties(self):
        """Test properties."""
        super().obj_properties()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_artifact_type_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_artifact_type_get_many(self):
        """Test Artifact Get Many"""
        # [Retrieve Testing] iterate over all object looking for needle
        artifact_types = self.v3.artifact_types()
        for artifact_type in artifact_types:
            if artifact_type.model.name == 'Protocol Number':
                assert artifact_type._api_endpoint == '/v3/artifactTypes'
                assert artifact_type.model.data_type == 'String'
                assert artifact_type.model.description is not None, 'description can not be none'
                assert artifact_type.model.description.startswith('In the Internet Protocol')
                break
        else:
            assert False, 'Artifact type of "Protocol Number" was not returned.'

    def test_artifact_type_get_single_by_id_properties(self):
        """Test Artifact get single attached to task by id"""

        # [Create Testing] Instantiate a instance of the Artifact Type
        artifact_type = self.v3.artifact_type()

        # [Create Testing] testing setters on model
        artifact_type.model.id = 1

        # [Retrieve Testing] get the object from the API
        artifact_type.get()

        # [Retrieve Testing] run assertions on returned data
        assert artifact_type.model.id == 1
        assert artifact_type.model.name == 'Email Address'
        assert artifact_type.model.description and artifact_type.model.description.startswith(
            'A name that identifies'
        )
        assert artifact_type.model.data_type == 'String'
        assert artifact_type.model.intel_type == 'indicator-EmailAddress'

        assert artifact_type.as_entity == {
            'type': 'Artifact Type',
            'id': 1,
            'value': 'Email Address',
        }

    def test_artifact_type_get_by_tql_filter_fail_tql(self):
        """Test Artifact Get by TQL"""
        # retrieve object using TQL
        artifact_types = self.v3.artifact_types()
        artifact_types.filter.tql = 'Invalid TQL'

        # [Fail Testing] validate the object is removed
        with pytest.raises(RuntimeError) as exc_info:
            for _ in artifact_types:
                pass

        # [Fail Testing] assert error message contains the correct code
        # error -> "(950, 'Error during pagination. API status code: 400, ..."
        assert '950' in str(exc_info.value)
        assert artifact_types.request.status_code == 400

    def test_artifact_type_all_filters(self):
        """Test TQL Filters for artifact on a Case"""

        artifact_types = self.v3.artifact_types()

        # [Filter Testing] active
        artifact_types.filter.active(TqlOperator.EQ, True)

        # [Filter Testing] data type
        artifact_types.filter.data_type(TqlOperator.EQ, 'String')

        # [Filter Testing] description
        artifact_types.filter.description(
            TqlOperator.EQ,
            'A name that identifies an electronic post office box on '
            'a network where Electronic-Mail (e-mail) can be sent.',
        )

        # [Filter Testing] id
        artifact_types.filter.id(TqlOperator.EQ, 1)

        # [Filter Testing] intel type
        artifact_types.filter.intel_type(TqlOperator.EQ, 'indicator-EmailAddress')

        # !!! Core Issue !!!
        # [Filter Testing] managed
        # artifact_types.filter.managed(TqlOperator.EQ, True)

        # [Filter Testing] name
        artifact_types.filter.name(TqlOperator.EQ, 'Email Address')

        for artifact_type in artifact_types:
            assert artifact_type.model.id == 1
            assert artifact_type.model.name == 'Email Address'
            assert artifact_type.model.description is not None, 'description can not be none'
            assert artifact_type.model.description.startswith('A name that identifies')
            assert artifact_type.model.data_type == 'String'
            assert artifact_type.model.intel_type == 'indicator-EmailAddress'
            break
        else:
            assert False, f'No artifact found for tql -> {artifact_types.tql.as_str}'
        assert len(artifact_types) == 1, (
            'More than 1 artifact type retrieved for tql ' f'{artifact_types.tql.as_str}.'
        )
