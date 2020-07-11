# -*- coding: utf-8 -*-
"""Test the TcEx Case Management Module."""
import os
from datetime import datetime, timedelta
from tcex.case_management.tql import TQL

from .cm_helpers import CMHelper, TestCaseManagement


class TestTag(TestCaseManagement):
    """Test TcEx CM Tag Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper('tag')
        self.cm = self.cm_helper.cm
        self.tcex = self.cm_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_tag_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_tag_code_gen(self):
        """Generate code and docstring from Options methods.

        This is not truly a test case, but best place to store it for now.
        """
        doc_string, filter_map, filter_class = super().obj_code_gen()
        assert doc_string
        assert filter_map
        assert filter_class

    def test_tag_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_tag_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_tag_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_tag_create(self, request):
        """Test Tag Creation"""
        # tag data
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # get tag from API to use in asserts
        tag = self.cm.tag(id=tag.id)
        tag.get()

        # run assertions on returned data
        assert tag.name == tag_data.get('name')
        assert tag.description == tag_data.get('description')

        # delete tag
        tag.delete()

    def test_tag_get_single(self, request):
        """Test Tag Creation"""
        # tag data
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # get tag from API to use in asserts
        tag = self.cm.tag(id=tag.id)
        tag.get()

        # run assertions on returned data
        assert tag.name == tag_data.get('name')
        assert tag.description == tag_data.get('description')

        # delete tag
        tag.delete()

    def test_tag_get_single_properties(self, request):
        """Test Tag Creation"""
        # tag data
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag()
        tag.description = tag_data.get('description')
        tag.name = tag_data.get('name')
        tag.submit()

        # create case with tag
        case = self.cm_helper.create_case(tags=tag_data)
        case_id = case.id

        # get tag from API to use in asserts
        tag = self.cm.tag(id=tag.id)
        tag.get(all_available_fields=True)

        # run assertions on returned data
        assert tag.description == tag_data.get('description')
        assert tag.name == tag_data.get('name')

        # read-only properties
        for case in tag.cases:
            if case.id == case_id:
                break
        else:
            assert False, 'Case id not found.'
        assert tag.last_used
        assert tag.owner

        # test as_entity
        assert tag.as_entity.get('value') == tag_data.get('name')

        # delete tag
        tag.delete()

    def test_tag_get_many(self, request):
        """Test Tag Creation"""
        # tag data
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # iterate over all tag looking for needle
        for t in self.cm.tags():
            if t.name == tag_data.get('name'):
                assert t.name == tag_data.get('name')
                assert t.description == tag_data.get('description')
                break
        else:
            assert False

        # delete tag
        tag.delete()

    def test_tag_get_by_tql_filter_case_id(self, request):
        """Test Tag Get by TQL"""
        tag_data = {
            'name': request.node.name,
        }

        # create case
        case = self.cm_helper.create_case(tags=tag_data)

        # retrieve tags using TQL
        tags = self.cm.tags()
        tags.filter.case_id(TQL.Operator.EQ, case.id)

        for t in tags:
            if t.name.lower() == 'pytest':
                continue

            assert t.name == tag_data.get('name')
            break
        else:
            assert False, 'No tag returned for TQL'

    def test_tag_get_by_tql_filter_description(self, request):
        """Test Tag Get by TQL"""
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # retrieve tags using TQL
        tags = self.cm.tags()
        tags.filter.description(TQL.Operator.EQ, tag_data.get('description'))

        for t in tags:
            if t.name.lower() == 'pytest':
                continue

            assert t.name == tag_data.get('name')
            break
        else:
            assert False, 'No tag returned for TQL'

    def test_tag_get_by_tql_filter_has_case(self, request):
        """Test Tag Get by TQL"""
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # create case
        case = self.cm_helper.create_case(tags=tag_data)

        # retrieve tags using TQL
        tags = self.cm.tags()
        tags.filter.has_case.id(TQL.Operator.EQ, case.id)

        for t in tags:
            if t.name.lower() == 'pytest':
                continue

            assert t.name == tag_data.get('name')
            break
        else:
            assert False, 'No tag returned for TQL'

    def test_tag_get_by_tql_filter_id(self, request):
        """Test Tag Get by TQL"""
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # retrieve tags using TQL
        tags = self.cm.tags()
        tags.filter.id(TQL.Operator.EQ, tag.id)

        for tag in tags:
            assert tag.name == tag_data.get('name')
            assert tag.description == tag_data.get('description')
            break
        else:
            assert False, 'No tag returned for TQL'

        # delete tag
        tag.delete()

    def test_tag_get_by_tql_filter_last_used(self, request):
        """Test Tag Get by TQL"""
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # create case
        self.cm_helper.create_case(tags=tag_data)

        # retrieve tags using TQL
        tags = self.cm.tags()
        tags.filter.id(TQL.Operator.EQ, tag.id)
        tags.filter.last_used(
            TQL.Operator.GT, (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        )

        for t in tags:
            if t.name.lower() == 'pytest':
                continue

            assert t.name == tag_data.get('name')
            break
        else:
            assert False, 'No tag returned for TQL'

    def test_tag_get_by_tql_filter_name(self, request):
        """Test Tag Get by TQL"""
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # retrieve tags using TQL
        tags = self.cm.tags()
        tags.filter.name(TQL.Operator.EQ, tag_data.get('name'))

        for tag in tags:
            assert tag.name == tag_data.get('name')
            assert tag.description == tag_data.get('description')
            break
        else:
            assert False, 'No tag returned for TQL'

        # delete tag
        tag.delete()

    def test_tag_get_by_tql_filter_owner(self, request):
        """Test Tag Get by TQL"""
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # retrieve tags using TQL
        tags = self.cm.tags()
        tags.filter.id(TQL.Operator.EQ, tag.id)
        tags.filter.owner(TQL.Operator.EQ, 2)

        for tag in tags:
            assert tag.name == tag_data.get('name')
            assert tag.description == tag_data.get('description')
            break
        else:
            assert False, 'No tag returned for TQL'

        # delete tag
        tag.delete()

    def test_tag_get_by_tql_filter_owner_name(self, request):
        """Test Tag Get by TQL"""
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # retrieve tags using TQL
        tags = self.cm.tags()
        tags.filter.id(TQL.Operator.EQ, tag.id)
        tags.filter.owner_name(TQL.Operator.EQ, 'TCI')

        for tag in tags:
            assert tag.name == tag_data.get('name')
            assert tag.description == tag_data.get('description')
            break
        else:
            assert False, 'No tag returned for TQL'

        # delete tag
        tag.delete()

    def test_tag_get_by_tql_filter_tql(self, request):
        """Test Tag Get by TQL"""
        tag_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
        }

        # create tag
        tag = self.cm.tag(**tag_data)
        tag.submit()

        # retrieve tags using TQL
        tags = self.cm.tags()
        tags.filter.tql(f'id EQ {tag.id}')

        for tag in tags:
            assert tag.name == tag_data.get('name')
            assert tag.description == tag_data.get('description')
            break
        else:
            assert False, 'No tag returned for TQL'

        # delete tag
        tag.delete()
