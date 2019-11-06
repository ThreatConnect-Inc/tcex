# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestWorkflowTemplateIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm

    def test_get_single(self):
        ...

    def test_get_many(self):
        ...

    def test_tql(self):
        ...

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


