"""Case Management Tag"""
# standard library
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr
from requests import Session

# first-party
from tcex.api.tc.v3.case_management.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.case_management_abc import CaseManagementABC
from tcex.api.tc.v3.case_management.case_management_collection_abc import (
    CaseManagementCollectionABC,
)
from tcex.api.tc.v3.case_management.filter_tag import FilterTag
from tcex.api.tc.v3.case_management.models.tag_model import TagModel, TagsModel


class Tags(CaseManagementCollectionABC):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = TagsModel(**kwargs)

    def __iter__(self) -> 'Tag':
        """Object iterator"""
        return self.iterate(base_class=Tag)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.TAGS.value

    @property
    def filter(self) -> FilterTag:
        """Return instance of FilterTags Object."""
        return FilterTag(self._session, self.tql)


class Tag(CaseManagementABC):
    """Tag object for Case Management."""

    def __init__(self, **kwargs) -> None:
        """Initialize Class properties"""
        super().__init__(kwargs.pop('session'))
        self._model = TagModel(**kwargs)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.TAGS.value

    @property
    def cases(self):
        # first-party
        from tcex.api.tc.v3.case_management.case import Cases

        yield from self._iterate_over_sublist(Cases)

    @property
    def as_entity(self):
        """Return the entity representation of the Tag."""
        return {'type': 'Tag', 'value': self.model.name, 'id': self.model.id}
