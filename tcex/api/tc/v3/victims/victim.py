"""Victim / Victims Object"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tags.tag_model import TagModel
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.victims.victim_filter import VictimFilter
from tcex.api.tc.v3.victims.victim_model import VictimModel, VictimsModel

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.tags.tag import Tag


class Victims(ObjectCollectionABC):
    """Victims Collection.

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

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = VictimsModel(**kwargs)
        self._type = 'victims'

    def __iter__(self) -> 'Victim':
        """Iterate over CM objects."""
        return self.iterate(base_class=Victim)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIMS.value

    @property
    def filter(self) -> 'VictimFilter':
        """Return the type specific filter object."""
        return VictimFilter(self.tql)


class Victim(ObjectABC):
    """Victims Object.

    Args:
        data (array, kwargs): The data for the Victims.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))
        self._model = VictimModel(**kwargs)
        self._type = 'victim'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIMS.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'victim_id',
            'operator': TqlOperator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        return {'type': 'Victim', 'id': self.model.id, 'value': self.model.summary}

    def add_tag(self, **kwargs) -> None:
        """Add tag to the object.

        Args:
            description (str, kwargs): A brief description of the Tag.
            name (str, kwargs): The **name** for the Tag.
        """
        self.model.tags.data.append(TagModel(**kwargs))

    @property
    def tags(self) -> 'Tag':
        """Yield Tag from Tags."""
        # first-party
        from tcex.api.tc.v3.tags.tag import Tags

        yield from self._iterate_over_sublist(Tags)
