"""TcEx Framework Module"""

from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING

from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.artifacts.artifact_filter import ArtifactFilter
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel, ArtifactsModel
from tcex.api.tc.v3.groups.group_model import GroupModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorModel
from tcex.api.tc.v3.notes.note_model import NoteModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC

if TYPE_CHECKING:  # pragma: no cover
    from tcex.api.tc.v3.groups.group import Group  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.indicators.indicator import Indicator  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.notes.note import Note  # CIRCULAR-IMPORT


class Artifact(ObjectABC):
    """Artifacts Object."""

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: ArtifactModel = ArtifactModel(**kwargs)
        self._nested_field_name = 'artifacts'
        self._nested_filter = 'has_artifact'
        self.type_ = 'Artifact'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ARTIFACTS.value

    @property
    def model(self) -> ArtifactModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | ArtifactModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            ex_msg = f'Invalid data type: {type(data)} provided.'
            raise RuntimeError(ex_msg)  # noqa: TRY004

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}

    @property
    def associated_groups(self) -> Generator['Group', None, None]:
        """Yield Group from Groups."""
        from tcex.api.tc.v3.groups.group import Groups  # noqa: PLC0415

        yield from self._iterate_over_sublist(Groups)  # type: ignore

    @property
    def associated_indicators(self) -> Generator['Indicator', None, None]:
        """Yield Indicator from Indicators."""
        from tcex.api.tc.v3.indicators.indicator import Indicators  # noqa: PLC0415

        yield from self._iterate_over_sublist(Indicators)  # type: ignore

    @property
    def notes(self) -> Generator['Note', None, None]:
        """Yield Note from Notes."""
        from tcex.api.tc.v3.notes.note import Notes  # noqa: PLC0415

        yield from self._iterate_over_sublist(Notes)  # type: ignore

    def stage_associated_group(self, data: dict | ObjectABC | GroupModel):
        """Stage group on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = GroupModel(**data)

        if not isinstance(data, GroupModel):
            ex_msg = 'Invalid type passed in to stage_associated_group'
            raise RuntimeError(ex_msg)  # noqa: TRY004
        data._staged = True  # noqa: SLF001
        self.model.associated_groups.data.append(data)  # type: ignore

    def stage_associated_indicator(self, data: dict | ObjectABC | IndicatorModel):
        """Stage indicator on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = IndicatorModel(**data)

        if not isinstance(data, IndicatorModel):
            ex_msg = 'Invalid type passed in to stage_associated_indicator'
            raise RuntimeError(ex_msg)  # noqa: TRY004
        data._staged = True  # noqa: SLF001
        self.model.associated_indicators.data.append(data)  # type: ignore

    def stage_note(self, data: dict | ObjectABC | NoteModel):
        """Stage note on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = NoteModel(**data)

        if not isinstance(data, NoteModel):
            ex_msg = 'Invalid type passed in to stage_note'
            raise RuntimeError(ex_msg)  # noqa: TRY004
        data._staged = True  # noqa: SLF001
        self.model.notes.data.append(data)  # type: ignore


class Artifacts(ObjectCollectionABC):
    """Artifacts Collection.

    # Example of params input
    {
        "result_limit": 100,  # Limit the retrieved results.
        "result_start": 10,  # Starting count used for pagination.
        "fields": ["caseId", "summary"]  # Select additional return fields.
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
        self._model = ArtifactsModel(**kwargs)
        self.type_ = 'artifacts'

    def __iter__(self) -> Iterator[Artifact]:
        """Return CM objects."""
        return self.iterate(base_class=Artifact)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ARTIFACTS.value

    @property
    def filter(self) -> ArtifactFilter:
        """Return the type specific filter object."""
        return ArtifactFilter(self.tql)
