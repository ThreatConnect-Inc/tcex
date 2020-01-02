# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from tcex.case_management.tql import TQL

from ..tcex_init import tcex


# pylint: disable=W0201
class TestNoteIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm

    # def test_get_single(self):

    # def test_get_many(self):

    # def test_tql(self):

    def test_delete(self, name='tag_name', create=True):
        """[summary]

        Args:
            name (str, optional): [description]. Defaults to 'tag_name'.
            create (bool, optional): [description]. Defaults to True.
        """
        if create:
            self.test_create(name, delete=False)
        tags = self.cm.tags()
        tags.name_filter(TQL.Operator.EQ, name)
        for tag in tags:
            tag.delete()

    def test_create(self, name='tag_name', description='Tag Description', delete=True):
        """[summary]

        Args:
            name (str, optional): [description]. Defaults to 'tag_name'.
            description (str, optional): [description]. Defaults to 'Tag Description'.
            delete (bool, optional): [description]. Defaults to True.

        Returns:
            [type]: [description]
        """
        tag = self.cm.tag(name=name, description=description)
        tag.submit()

        assert tag.name == name
        assert tag.description == description

        if delete:
            self.test_delete(name, create=False)

        return tag
