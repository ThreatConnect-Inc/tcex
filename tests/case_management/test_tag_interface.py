# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestTagIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm

    def test_get_single(self):
        tag = self.test_create('tag_name', delete=False)
        self.test_create('tag_name_2', delete=False)

        tag = self.cm.tag(id=tag.id)
        tag.get()
        assert tag.name == 'tag_name'

        self.test_delete('tag_name', create=False)
        self.test_delete('tag_name_2', create=False)

    def test_tql(self):
        test_tag_1 = self.test_create('tag_name', delete=False)
        self.test_create('tag_name_2', delete=False)
        tags = self.cm.tags()

        # Test id tql filter
        tags.id_filter('=', test_tag_1.id)
        assert len(tags) == 1
        for tag in tags:
            assert tag.id == test_tag_1.id

        # Test AND functionality
        tags.name_filter('=', 'does not exist')
        assert len(tags) == 0

        # Clear Filters
        tags.tql.filters = []

        # Test Name filter
        tags.name_filter('!=', 'does not exist')
        assert len(tags) == 2
        for tag in tags:
            assert tag.name in ['tag_name', 'tag_name_2']

        tags.name_filter('=', 'tag_name')
        assert len(tags) == 1
        for tag in tags:
            assert tag.name == test_tag_1.name

        # Clear Filters
        tags.tql.filters = []

        tags.owner_name_filter('=', tcex.args.tc_owner)
        # assert len(tags) == 2

        self.test_delete('tag_name', create=False)
        self.test_delete('tag_name_2', create=False)

    def test_delete(self, name='tag_name', create=True):
        if create:
            self.test_create(name, delete=False)
        tags = self.cm.tags()
        tags.name_filter('=', name)
        for tag in tags:
            tag.delete()

    def test_create(self, name='tag_name', description='Tag Description', delete=True):
        tag = self.cm.tag(name=name, description=description)
        tag.submit()

        assert tag.name == name
        assert tag.description == description

        if delete:
            self.test_delete(name, create=False)

        return tag
