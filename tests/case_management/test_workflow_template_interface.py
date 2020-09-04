"""Test the TcEx Case Management Module."""
# standard library
import os

# first-party
from tcex.case_management.tql import TQL

from .cm_helpers import CMHelper, TestCaseManagement


class TestWorkflowTemplate(TestCaseManagement):
    """Test TcEx CM Workflow Template Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper('workflow_template')
        self.cm = self.cm_helper.cm
        self.tcex = self.cm_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_workflow_template_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_workflow_template_code_gen(self):
        """Generate code and docstring from Options methods.

        This is not truly a test case, but best place to store it for now.
        """
        doc_string, filter_map, filter_class = super().obj_code_gen()
        assert doc_string
        assert filter_map
        assert filter_class

    def test_workflow_template_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_workflow_template_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_workflow_template_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_workflow_template_create_by_case_id(self, request):
        """Test Workflow Template Creation"""
        # workflow template data
        workflow_template_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
            'version': 1,
        }

        # create workflow_template
        workflow_template = self.cm.workflow_template(**workflow_template_data)
        workflow_template.submit()

        # get workflow template from API to use in asserts
        workflow_template = self.cm.workflow_template(id=workflow_template.id)
        workflow_template.get()

        # run assertions on returned data
        assert workflow_template.description == workflow_template_data.get('description')
        assert workflow_template.name == workflow_template_data.get('name')
        assert workflow_template.version == workflow_template_data.get('version')

        # cleanup workflow template
        workflow_template.delete()

    def test_workflow_template_get_many(self, request):
        """Test Workflow Template Creation"""
        # workflow template data
        workflow_template_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
            'version': 1,
        }

        # create workflow_template
        workflow_template = self.cm.workflow_template(**workflow_template_data)
        workflow_template.submit()

        # get workflow template from API to use in asserts
        for wt in self.cm.workflow_templates():
            if wt.name == workflow_template_data.get('name'):
                assert workflow_template.description == workflow_template_data.get('description')
                assert workflow_template.version == workflow_template_data.get('version')
                break
        else:
            assert False, f"Workflow template {workflow_template_data.get('name')} was not found."

        # cleanup workflow template
        workflow_template.delete()

    def test_workflow_template_get_single_by_id(self, request):
        """Test Workflow Template Creation"""
        # workflow template data
        workflow_template_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
            'version': 1,
        }

        # create workflow_template
        workflow_template = self.cm.workflow_template(**workflow_template_data)
        workflow_template.submit()

        # get workflow template from API to use in asserts
        workflow_template = self.cm.workflow_template(id=workflow_template.id)
        workflow_template.get(all_available_fields=True)

        # run assertions on returned data
        assert workflow_template.description == workflow_template_data.get('description')
        assert workflow_template.name == workflow_template_data.get('name')
        assert workflow_template.version == workflow_template_data.get('version')
        assert workflow_template.cases

        # cleanup workflow template
        workflow_template.delete()

    def test_workflow_template_get_single_by_id_properties(self, request):
        """Test Workflow Template Creation"""
        # workflow template data
        workflow_template_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
            'version': 1,
        }

        # create workflow_template
        workflow_template = self.cm.workflow_template()
        workflow_template.description = workflow_template_data.get('description')
        workflow_template.name = workflow_template_data.get('name')
        workflow_template.version = workflow_template_data.get('version')
        workflow_template.submit()

        # get workflow template from API to use in asserts
        workflow_template = self.cm.workflow_template(id=workflow_template.id)
        workflow_template.get(all_available_fields=True)

        # run assertions on returned data
        assert workflow_template.description == workflow_template_data.get('description')
        assert workflow_template.name == workflow_template_data.get('name')
        assert workflow_template.version == workflow_template_data.get('version')
        assert workflow_template.cases

        # cleanup workflow template
        workflow_template.delete()

    def test_workflow_template_get_by_tql_filter_active(self, request):
        """Test Workflow Template Get by TQL"""
        # workflow template data
        workflow_template_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
            'version': 1,
        }

        # create workflow_template
        workflow_template = self.cm.workflow_template(**workflow_template_data)
        workflow_template.submit()

        # retrieve workflow event using TQL
        workflow_templates = self.cm.workflow_templates()
        workflow_templates.filter.active(TQL.Operator.EQ, False)
        # workflow_templates.filter.id(TQL.Operator.EQ, workflow_template.id)

        for wt in workflow_templates:
            # more than one workflow event will always be returned
            if wt.name == workflow_template_data.get('name'):
                break
        else:
            assert False, 'No workflow templates returned for TQL'

        # cleanup workflow template
        workflow_template.delete()

    def test_workflow_template_get_by_tql_filter_description(self, request):
        """Test Workflow Template Get by TQL"""
        # workflow template data
        workflow_template_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
            'version': 1,
        }

        # create workflow_template
        workflow_template = self.cm.workflow_template(**workflow_template_data)
        workflow_template.submit()

        # retrieve workflow event using TQL
        workflow_templates = self.cm.workflow_templates()
        workflow_templates.filter.description(
            TQL.Operator.EQ, workflow_template_data.get('description')
        )

        for wt in workflow_templates:
            # more than one workflow event will always be returned
            if wt.name == workflow_template_data.get('name'):
                break
        else:
            assert False, 'No workflow templates returned for TQL'

        # cleanup workflow template
        workflow_template.delete()

    def test_workflow_template_get_by_tql_filter_id(self, request):
        """Test Workflow Template Get by TQL"""
        # workflow template data
        workflow_template_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
            'version': 1,
        }

        # create workflow_template
        workflow_template = self.cm.workflow_template(**workflow_template_data)
        workflow_template.submit()

        # retrieve workflow event using TQL
        workflow_templates = self.cm.workflow_templates()
        workflow_templates.filter.id(TQL.Operator.EQ, workflow_template.id)

        for wt in workflow_templates:
            # more than one workflow event will always be returned
            if wt.name == workflow_template_data.get('name'):
                break
        else:
            assert False, 'No workflow templates returned for TQL'

        # cleanup workflow template
        workflow_template.delete()

    def test_workflow_template_get_by_tql_filter_name(self, request):
        """Test Workflow Template Get by TQL"""
        # workflow template data
        workflow_template_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
            'version': 1,
        }

        # create workflow_template
        workflow_template = self.cm.workflow_template(**workflow_template_data)
        workflow_template.submit()

        # retrieve workflow event using TQL
        workflow_templates = self.cm.workflow_templates()
        workflow_templates.filter.name(TQL.Operator.EQ, workflow_template.name)

        for wt in workflow_templates:
            # more than one workflow event will always be returned
            if wt.name == workflow_template_data.get('name'):
                break
        else:
            assert False, 'No workflow templates returned for TQL'

        # cleanup workflow template
        workflow_template.delete()

    def test_workflow_template_get_by_tql_filter_version(self, request):
        """Test Workflow Template Get by TQL"""
        # workflow template data
        workflow_template_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
            'version': 1,
        }

        # create workflow_template
        workflow_template = self.cm.workflow_template(**workflow_template_data)
        workflow_template.submit()

        # retrieve workflow event using TQL
        workflow_templates = self.cm.workflow_templates()
        workflow_templates.filter.id(TQL.Operator.EQ, workflow_template.id)
        workflow_templates.filter.version(TQL.Operator.EQ, workflow_template_data.get('version'))

        for wt in workflow_templates:
            # more than one workflow event will always be returned
            if wt.name == workflow_template_data.get('name'):
                break
        else:
            assert False, 'No workflow templates returned for TQL'

        # cleanup workflow template
        workflow_template.delete()

    def test_workflow_template_as_entity(self, request):
        """Test Workflow Template As entity"""
        # workflow template data
        workflow_template_data = {
            'description': f'a description for {request.node.name}',
            'name': request.node.name,
            'version': 1,
        }

        # create workflow_template
        workflow_template = self.cm.workflow_template(**workflow_template_data)

        # assert a proper entity is returned
        assert workflow_template.as_entity.get('value') == workflow_template_data.get('name')
