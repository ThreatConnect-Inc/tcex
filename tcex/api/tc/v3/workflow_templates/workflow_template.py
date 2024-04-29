"""TcEx Framework Module"""

# standard library
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.workflow_templates.workflow_template_filter import WorkflowTemplateFilter
from tcex.api.tc.v3.workflow_templates.workflow_template_model import (
    WorkflowTemplateModel,
    WorkflowTemplatesModel,
)


class WorkflowTemplate(ObjectABC):
    """WorkflowTemplates Object.

    Args:
        config_attribute (None, kwargs): The **config attribute** for the Workflow_Template.
        description (str, kwargs): The **description** for the Workflow_Template.
        name (str, kwargs): The **name** for the Workflow_Template.
        version (int, kwargs): The **version** for the Workflow_Template.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: WorkflowTemplateModel = WorkflowTemplateModel(**kwargs)
        self._nested_field_name = 'workflowTemplates'
        self._nested_filter = 'has_workflow_template'
        self.type_ = 'Workflow Template'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.WORKFLOW_TEMPLATES.value

    @property
    def model(self) -> WorkflowTemplateModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | WorkflowTemplateModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_

        return {'type': type_, 'id': self.model.id, 'value': self.model.name}


class WorkflowTemplates(ObjectCollectionABC):
    """WorkflowTemplates Collection.

    # Example of params input
    {
        'result_limit': 100,  # Limit the retrieved results.
        'result_start': 10,  # Starting count used for pagination.
        'fields': ['caseId', 'summary']  # Select additional return fields.
    }

    Args:
        session (Session): Session object configured with TC API Auth.
        tql_filters (list): List of TQL filters.
        params (dict): Additional query params (see example above).
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = WorkflowTemplatesModel(**kwargs)
        self.type_ = 'workflow_templates'

    def __iter__(self) -> Iterator[WorkflowTemplate]:
        """Return CM objects."""
        return self.iterate(base_class=WorkflowTemplate)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.WORKFLOW_TEMPLATES.value

    @property
    def filter(self) -> WorkflowTemplateFilter:
        """Return the type specific filter object."""
        return WorkflowTemplateFilter(self.tql)
