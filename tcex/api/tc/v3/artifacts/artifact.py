"""TcEx Framework Module"""

# standard library
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.artifacts.artifact_filter import ArtifactFilter
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel, ArtifactsModel
from tcex.api.tc.v3.groups.group_model import GroupModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorModel
from tcex.api.tc.v3.notes.note_model import NoteModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.groups.group import Group  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.indicators.indicator import Indicator  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.notes.note import Note  # CIRCULAR-IMPORT


class Artifact(ObjectABC):
    """Artifacts Object.

    Args:
        associated_groups (Groups, kwargs): A list of Groups associated with this Artifact.
        associated_indicators (Indicators, kwargs): A list of Indicators associated with this
            Artifact.
        case_id (int, kwargs): The **case id** for the Artifact.
        case_xid (str, kwargs): The **case xid** for the Artifact.
        derived_link (bool, kwargs): Flag to specify if this artifact should be used for potentially
            associated cases or not.
        field_name (str, kwargs): The field name for the artifact.
        file_data (str, kwargs): Base64 encoded file attachment required only for certain artifact
            types.
        hash_code (str, kwargs): Hashcode of Artifact of type File.
        notes (Notes, kwargs): A list of Notes corresponding to the Artifact.
        source (str, kwargs): The **source** for the Artifact.
        summary (str, kwargs): The **summary** for the Artifact.
        task_id (int, kwargs): The ID of the task which the Artifact references.
        task_xid (str, kwargs): The XID of the task which the Artifact references.
        type (str, kwargs): The **type** for the Artifact.
    """

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
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}

    @property
    def associated_groups(self) -> Generator['Group', None, None]:
        """Yield Group from Groups."""
        # first-party
        from tcex.api.tc.v3.groups.group import Groups

        yield from self._iterate_over_sublist(Groups)  # type: ignore

    @property
    def associated_indicators(self) -> Generator['Indicator', None, None]:
        """Yield Indicator from Indicators."""
        # first-party
        from tcex.api.tc.v3.indicators.indicator import Indicators

        yield from self._iterate_over_sublist(Indicators)  # type: ignore

    @property
    def notes(self) -> Generator['Note', None, None]:
        """Yield Note from Notes."""
        # first-party
        from tcex.api.tc.v3.notes.note import Notes

        yield from self._iterate_over_sublist(Notes)  # type: ignore

    def stage_associated_group(self, data: dict | ObjectABC | GroupModel):
        """Stage group on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = GroupModel(**data)

        if not isinstance(data, GroupModel):
            raise RuntimeError('Invalid type passed in to stage_associated_group')
        data._staged = True
        self.model.associated_groups.data.append(data)  # type: ignore

    def stage_associated_indicator(self, data: dict | ObjectABC | IndicatorModel):
        """Stage indicator on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = IndicatorModel(**data)

        if not isinstance(data, IndicatorModel):
            raise RuntimeError('Invalid type passed in to stage_associated_indicator')
        data._staged = True
        self.model.associated_indicators.data.append(data)  # type: ignore

    def stage_note(self, data: dict | ObjectABC | NoteModel):
        """Stage note on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = NoteModel(**data)

        if not isinstance(data, NoteModel):
            raise RuntimeError('Invalid type passed in to stage_note')
        data._staged = True
        self.model.notes.data.append(data)  # type: ignore


class Artifacts(ObjectCollectionABC):
    """Artifacts Collection.

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
