"""Case Management Workflow Template"""
# standard library
from typing import Dict

# third-party
from pydantic import BaseModel

# first-party
from tcex.api.tc.v3.case_management.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.case_management_abc import CaseManagementABC
from tcex.api.tc.v3.case_management.case_management_collection_abc import (
    CaseManagementCollectionABC,
)
from tcex.api.tc.v3.case_management.filter_workflow_template import FilterWorkflowTemplate
from tcex.api.tc.v3.case_management.models.workflow_template_model import (
    WorkflowTemplateData,
    WorkflowTemplateModel,
)
from tcex.api.tc.v3.case_management.tql import TQL


class WorkflowTemplates(CaseManagementCollectionABC):
    """Workflow Template Class for Case Management Collection

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        # Example of params input
        {
            'result_limit': 100,  # How many results are retrieved.
            'result_start': 10,  # Starting point on retrieved results.
            'fields': ['caseId', 'summary']  # Additional fields returned on the results
        }

    Args:
        initial_response: Initial data from ThreatConnect API.
        tql_filters: List of TQL filters.
        params: Dict of the params to be sent while retrieving the objects.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = WorkflowTemplateData(**kwargs)

    def __iter__(self) -> 'WorkflowTemplate':
        """Object iterator"""
        return self.iterate(base_class=WorkflowTemplate)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.WORKFLOW_TEMPLATES.value

    @property
    def filter(self):
        """Return instance of FilterWorkflowTemplate Object."""
        return FilterWorkflowTemplate(self._session, self.tql)


class WorkflowTemplate(CaseManagementABC):
    """Case Management Workflow Template"""

    def __init__(self, **kwargs) -> None:
        """Initialize Class properties"""
        # Might need to save id for submit request. Might be able to do a try catch though in parent.
        super().__init__(kwargs.pop('session', None))
        self._model = WorkflowTemplateModel(**kwargs)

    @property
    def _base_filter(self) -> list:
        """Return the default filter."""
        return [
            {
                'keyword': 'workflowEventId',
                'operator': TQL.Operator.EQ,
                'value': self.model.id,
                'type_': TQL.Type.INTEGER,
            }
        ]

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.WORKFLOW_TEMPLATES.value

    @property
    def as_entity(self) -> Dict[str, str]:
        """Return the entity representation of the Workflow Event."""
        return {'type': 'Workflow Template', 'value': self.model.name, 'id': self.model.id}
