"""Case Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class FilterCase(FilterABC):
    """Filter Object for Cases"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.CASES.value

    def created_by(self, operator: Enum, created_by: str) -> None:
        """Filter Cases based on **createdBy** keyword.

        Args:
            operator: The operator enum for the filter.
            created_by: The account login of the user who created the case.
        """
        self._tql.add_filter('createdBy', operator, created_by, TQL.Type.STRING)

    def created_by_id(self, operator: Enum, created_by_id) -> None:
        """Filter Cases based on **createdById** keyword.

        Args:
            operator: The operator enum for the filter.
            created_by_id: The user ID for the creator of the case.
        """
        self._tql.add_filter('createdById', operator, created_by_id, TQL.Type.INTEGER)

    def date_added(self, operator: Enum, date_added) -> None:
        """Filter Cases based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the case was added to the system.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

    def description(self, operator: Enum, description) -> None:
        """Filter Cases based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the case.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    # TODO: [low] cyclic import typing
    @property
    def has_artifact(self):
        """Return **FilterArtifacts** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_artifact import FilterArtifact

        artifacts = FilterArtifact(self._session, TQL())
        self._tql.add_filter('hasArtifact', TQL.Operator.EQ, artifacts, TQL.Type.SUB_QUERY)
        return artifacts

    # TODO: [low] cyclic import typing
    @property
    def has_note(self):
        """Return **FilterNotes** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_note import FilterNote

        notes = FilterNote(self._session, TQL())
        self._tql.add_filter('hasNote', TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)
        return notes

    # TODO: [low] cyclic import typing
    @property
    def has_tag(self):
        """Return **FilterTags** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_tag import FilterTag

        tags = FilterTag(self._session, TQL())
        self._tql.add_filter('hasTag', TQL.Operator.EQ, tags, TQL.Type.SUB_QUERY)
        return tags

    # TODO: Implement this
    @property
    def has_group(self):
        """Return **FilterTags** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_tag import FilterTag

        tags = FilterTag(self._session, TQL())
        self._tql.add_filter('hasGroup', TQL.Operator.EQ, tags, TQL.Type.SUB_QUERY)
        return tags

    # TODO: Implement this
    @property
    def has_indicator(self):
        """Return **FilterTags** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_tag import FilterTag

        tags = FilterTag(self._session, TQL())
        self._tql.add_filter('hasIndicator', TQL.Operator.EQ, tags, TQL.Type.SUB_QUERY)
        return tags

    # TODO: [low] cyclic import typing
    @property
    def has_task(self):
        """Return **FilterTask** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_task import FilterTask

        tasks = FilterTask(self._session, TQL())
        self._tql.add_filter('hasTask', TQL.Operator.EQ, tasks, TQL.Type.SUB_QUERY)
        return tasks

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter Cases based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the case.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def name(self, operator: Enum, name: str) -> None:
        """Filter Cases based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the case.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def owner(self, operator: Enum, owner: str) -> None:
        """Filter Cases based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The Owner ID for the case.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str) -> None:
        """Filter Cases based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name for the case.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TQL.Type.STRING)

    def resolution(self, operator: Enum, resolution: str) -> None:
        """Filter Cases based on **resolution** keyword.

        Args:
            operator: The operator enum for the filter.
            resolution: The resolution of the case.
        """
        self._tql.add_filter('resolution', operator, resolution, TQL.Type.STRING)

    def severity(self, operator: Enum, severity: str) -> None:
        """Filter Cases based on **severity** keyword.

        Args:
            operator: The operator enum for the filter.
            severity: The severity of the case.
        """
        self._tql.add_filter('severity', operator, severity, TQL.Type.STRING)

    def status(self, operator: Enum, status: str) -> None:
        """Filter Cases based on **status** keyword.

        Args:
            operator: The operator enum for the filter.
            status: The status of the case.
        """
        self._tql.add_filter('status', operator, status, TQL.Type.STRING)

    def tag(self, operator: Enum, tag: str) -> None:
        """Filter Cases based on **tag** keyword.

        Args:
            operator: The operator enum for the filter.
            tag: The name of a tag applied to a case.
        """
        self._tql.add_filter('tag', operator, tag, TQL.Type.STRING)

    def target_id(self, operator: Enum, target_id: int) -> None:
        """Filter Cases based on **targetId** keyword.

        Args:
            operator: The operator enum for the filter.
            target_id: The assigned user or group ID for the case.
        """
        self._tql.add_filter('targetId', operator, target_id, TQL.Type.INTEGER)

    def target_type(self, operator: Enum, target_type: str) -> None:
        """Filter Cases based on **targetType** keyword.

        Args:
            operator: The operator enum for the filter.
            target_type: The target type for this case (either User or Group).
        """
        self._tql.add_filter('targetType', operator, target_type, TQL.Type.STRING)

    def xid(self, operator: Enum, xid: str) -> None:
        """Filter Cases based on **xid** keyword.

        Args:
            operator: The operator enum for the filter.
            xid: The XID of the case.
        """
        self._tql.add_filter('xid', operator, xid, TQL.Type.STRING)
