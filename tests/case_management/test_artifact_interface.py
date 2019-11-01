# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestArtifactIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm
        self.intel_type = 'ArtifactType intelType'

    def test_get_single(self, summary='Artifact Summary'):
        """Tests adding, fetching, updating, and deleting host attributes"""
        tags = self.cm.tags()
        tags.owner_name_filter('=', 'System')
        for tag in tags:
            print(tag)
        # create
        # case = self.cm.case(name='Case Name', status='Open', severity='Low')
        # case.add_tag(name='tag1', description='tags_description')
        # case.add_note(text='text', summary='summary')
        # case.add_task(name='name', description='description')
        # case.submit()
        # artifact = self.artifact_create(
        #     summary=summary, intel_type=self.intel_type, type='Date artifact type', case_id=case.id
        # )

    # def artifact_create(self):
    #     artifact
    # def case_create(self, **kwargs):
    #     self.
