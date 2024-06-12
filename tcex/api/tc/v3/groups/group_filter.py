"""TcEx Framework Module"""

# standard library
from datetime import datetime
from enum import Enum

# third-party
from arrow import Arrow

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class GroupFilter(FilterABC):
    """Filter Object for Groups"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.GROUPS.value

    def associated_indicator(self, operator: Enum, associated_indicator: int | list):
        """Filter associatedIndicator based on **associatedIndicator** keyword.

        Args:
            operator: The operator enum for the filter.
            associated_indicator: No description provided.
        """
        if isinstance(associated_indicator, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('associatedIndicator', operator, associated_indicator, TqlType.INTEGER)

    def attribute(self, operator: Enum, attribute: list | str):
        """Filter attribute based on **attribute** keyword.

        Args:
            operator: The operator enum for the filter.
            attribute: No description provided.
        """
        if isinstance(attribute, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('attribute', operator, attribute, TqlType.STRING)

    def child_group(self, operator: Enum, child_group: int | list):
        """Filter childGroup based on **childGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            child_group: No description provided.
        """
        if isinstance(child_group, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('childGroup', operator, child_group, TqlType.INTEGER)

    def created_by(self, operator: Enum, created_by: list | str):
        """Filter Created By based on **createdBy** keyword.

        Args:
            operator: The operator enum for the filter.
            created_by: The user who created the group.
        """
        if isinstance(created_by, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('createdBy', operator, created_by, TqlType.STRING)

    def date_added(self, operator: Enum, date_added: Arrow | datetime | int | str):
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the group was added to the system.
        """
        date_added = self.util.any_to_datetime(date_added).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('dateAdded', operator, date_added, TqlType.STRING)

    def document_date_added(
        self, operator: Enum, document_date_added: Arrow | datetime | int | str
    ):
        """Filter Date Added (Document) based on **documentDateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            document_date_added: The date the document was added.
        """
        document_date_added = self.util.any_to_datetime(document_date_added).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('documentDateAdded', operator, document_date_added, TqlType.STRING)

    def document_filename(self, operator: Enum, document_filename: list | str):
        """Filter Filename (Document) based on **documentFilename** keyword.

        Args:
            operator: The operator enum for the filter.
            document_filename: The file name of the document.
        """
        if isinstance(document_filename, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('documentFilename', operator, document_filename, TqlType.STRING)

    def document_filesize(self, operator: Enum, document_filesize: int | list):
        """Filter File Size (Document) based on **documentFilesize** keyword.

        Args:
            operator: The operator enum for the filter.
            document_filesize: The filesize of the document.
        """
        if isinstance(document_filesize, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('documentFilesize', operator, document_filesize, TqlType.INTEGER)

    def document_status(self, operator: Enum, document_status: list | str):
        """Filter Status (Document) based on **documentStatus** keyword.

        Args:
            operator: The operator enum for the filter.
            document_status: The status of the document.
        """
        if isinstance(document_status, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('documentStatus', operator, document_status, TqlType.STRING)

    def document_type(self, operator: Enum, document_type: list | str):
        """Filter Type (Document) based on **documentType** keyword.

        Args:
            operator: The operator enum for the filter.
            document_type: The type of document.
        """
        if isinstance(document_type, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('documentType', operator, document_type, TqlType.STRING)

    def downvote_count(self, operator: Enum, downvote_count: int | list):
        """Filter Downvote Count based on **downvoteCount** keyword.

        Args:
            operator: The operator enum for the filter.
            downvote_count: The number of downvotes the group has received.
        """
        if isinstance(downvote_count, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('downvoteCount', operator, downvote_count, TqlType.INTEGER)

    def email_date(self, operator: Enum, email_date: Arrow | datetime | int | str):
        """Filter Date (Email) based on **emailDate** keyword.

        Args:
            operator: The operator enum for the filter.
            email_date: The date of the email.
        """
        email_date = self.util.any_to_datetime(email_date).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('emailDate', operator, email_date, TqlType.STRING)

    def email_from(self, operator: Enum, email_from: list | str):
        """Filter From (Email) based on **emailFrom** keyword.

        Args:
            operator: The operator enum for the filter.
            email_from: The 'from' field of the email.
        """
        if isinstance(email_from, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('emailFrom', operator, email_from, TqlType.STRING)

    def email_score(self, operator: Enum, email_score: int | list):
        """Filter Score (Email) based on **emailScore** keyword.

        Args:
            operator: The operator enum for the filter.
            email_score: The score of the email.
        """
        if isinstance(email_score, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('emailScore', operator, email_score, TqlType.INTEGER)

    def email_score_includes_body(self, operator: Enum, email_score_includes_body: bool):
        """Filter Score Includes Body (Email) based on **emailScoreIncludesBody** keyword.

        Args:
            operator: The operator enum for the filter.
            email_score_includes_body: A true/false indicating if the body was included in the
                scoring of the email.
        """
        self._tql.add_filter(
            'emailScoreIncludesBody', operator, email_score_includes_body, TqlType.BOOLEAN
        )

    def email_subject(self, operator: Enum, email_subject: list | str):
        """Filter Subject (Email) based on **emailSubject** keyword.

        Args:
            operator: The operator enum for the filter.
            email_subject: The subject of the email.
        """
        if isinstance(email_subject, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('emailSubject', operator, email_subject, TqlType.STRING)

    def event_date(self, operator: Enum, event_date: Arrow | datetime | int | str):
        """Filter Event Date based on **eventDate** keyword.

        Args:
            operator: The operator enum for the filter.
            event_date: The event date of the group.
        """
        event_date = self.util.any_to_datetime(event_date).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('eventDate', operator, event_date, TqlType.STRING)

    def event_type(self, operator: Enum, event_type: list | str):
        """Filter Event Type based on **eventType** keyword.

        Args:
            operator: The operator enum for the filter.
            event_type: The event type of the group.
        """
        if isinstance(event_type, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('eventType', operator, event_type, TqlType.STRING)

    def external_date_added(
        self, operator: Enum, external_date_added: Arrow | datetime | int | str
    ):
        """Filter External Date Added based on **externalDateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            external_date_added: The date and time that the group was first created externally.
        """
        external_date_added = self.util.any_to_datetime(external_date_added).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('externalDateAdded', operator, external_date_added, TqlType.STRING)

    def external_date_expires(
        self, operator: Enum, external_date_expires: Arrow | datetime | int | str
    ):
        """Filter External Date Expires based on **externalDateExpires** keyword.

        Args:
            operator: The operator enum for the filter.
            external_date_expires: The date and time the group expires externally.
        """
        external_date_expires = self.util.any_to_datetime(external_date_expires).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('externalDateExpires', operator, external_date_expires, TqlType.STRING)

    def external_last_modified(
        self, operator: Enum, external_last_modified: Arrow | datetime | int | str
    ):
        """Filter External Last Modified based on **externalLastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            external_last_modified: The date and time the group was modified externally.
        """
        external_last_modified = self.util.any_to_datetime(external_last_modified).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter(
            'externalLastModified', operator, external_last_modified, TqlType.STRING
        )

    def first_seen(self, operator: Enum, first_seen: Arrow | datetime | int | str):
        """Filter First Seen based on **firstSeen** keyword.

        Args:
            operator: The operator enum for the filter.
            first_seen: The date and time that the group was first seen.
        """
        first_seen = self.util.any_to_datetime(first_seen).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('firstSeen', operator, first_seen, TqlType.STRING)

    def generated_report(self, operator: Enum, generated_report: bool):
        """Filter Generated (Report) based on **generatedReport** keyword.

        Args:
            operator: The operator enum for the filter.
            generated_report: Boolean flag indicating if the Report was auto-generated.
        """
        self._tql.add_filter('generatedReport', operator, generated_report, TqlType.BOOLEAN)

    @property
    def has_all_tags(self):
        """Return **TagFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.tags.tag_filter import TagFilter

        tags = TagFilter(Tql())
        self._tql.add_filter('hasAllTags', TqlOperator.EQ, tags, TqlType.SUB_QUERY)
        return tags

    @property
    def has_artifact(self):
        """Return **ArtifactFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.artifacts.artifact_filter import ArtifactFilter

        artifacts = ArtifactFilter(Tql())
        self._tql.add_filter('hasArtifact', TqlOperator.EQ, artifacts, TqlType.SUB_QUERY)
        return artifacts

    @property
    def has_attribute(self):
        """Return **GroupAttributeFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.group_attributes.group_attribute_filter import GroupAttributeFilter

        attributes = GroupAttributeFilter(Tql())
        self._tql.add_filter('hasAttribute', TqlOperator.EQ, attributes, TqlType.SUB_QUERY)
        return attributes

    @property
    def has_case(self):
        """Return **CaseFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.cases.case_filter import CaseFilter

        cases = CaseFilter(Tql())
        self._tql.add_filter('hasCase', TqlOperator.EQ, cases, TqlType.SUB_QUERY)
        return cases

    @property
    def has_group(self):
        """Return **GroupFilter** for further filtering."""
        groups = GroupFilter(Tql())
        self._tql.add_filter('hasGroup', TqlOperator.EQ, groups, TqlType.SUB_QUERY)
        return groups

    @property
    def has_indicator(self):
        """Return **IndicatorFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.indicators.indicator_filter import IndicatorFilter

        indicators = IndicatorFilter(Tql())
        self._tql.add_filter('hasIndicator', TqlOperator.EQ, indicators, TqlType.SUB_QUERY)
        return indicators

    def has_intel_query(self, operator: Enum, has_intel_query: int | list):
        """Filter Associated User Queries based on **hasIntelQuery** keyword.

        Args:
            operator: The operator enum for the filter.
            has_intel_query: A nested query for association to User Queries.
        """
        if isinstance(has_intel_query, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('hasIntelQuery', operator, has_intel_query, TqlType.INTEGER)

    @property
    def has_intel_requirement(self):
        """Return **IntelRequirementFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.intel_requirements.intel_requirement_filter import (
            IntelRequirementFilter,
        )

        intel_requirements = IntelRequirementFilter(Tql())
        self._tql.add_filter(
            'hasIntelRequirement', TqlOperator.EQ, intel_requirements, TqlType.SUB_QUERY
        )
        return intel_requirements

    @property
    def has_security_label(self):
        """Return **SecurityLabel** for further filtering."""
        # first-party
        from tcex.api.tc.v3.security_labels.security_label_filter import SecurityLabelFilter

        security_labels = SecurityLabelFilter(Tql())
        self._tql.add_filter('hasSecurityLabel', TqlOperator.EQ, security_labels, TqlType.SUB_QUERY)
        return security_labels

    @property
    def has_tag(self):
        """Return **TagFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.tags.tag_filter import TagFilter

        tags = TagFilter(Tql())
        self._tql.add_filter('hasTag', TqlOperator.EQ, tags, TqlType.SUB_QUERY)
        return tags

    @property
    def has_victim(self):
        """Return **VictimFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.victims.victim_filter import VictimFilter

        victims = VictimFilter(Tql())
        self._tql.add_filter('hasVictim', TqlOperator.EQ, victims, TqlType.SUB_QUERY)
        return victims

    @property
    def has_victim_asset(self):
        """Return **VictimAssetFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.victim_assets.victim_asset_filter import VictimAssetFilter

        victim_assets = VictimAssetFilter(Tql())
        self._tql.add_filter('hasVictimAsset', TqlOperator.EQ, victim_assets, TqlType.SUB_QUERY)
        return victim_assets

    def id(self, operator: Enum, id: int | list):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the group.
        """
        if isinstance(id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def insights(self, operator: Enum, insights: list | str):
        """Filter Insights (Report) based on **insights** keyword.

        Args:
            operator: The operator enum for the filter.
            insights: The AI generated synopsis of the report.
        """
        if isinstance(insights, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('insights', operator, insights, TqlType.STRING)

    def is_group(self, operator: Enum, is_group: bool):
        """Filter isGroup based on **isGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            is_group: No description provided.
        """
        self._tql.add_filter('isGroup', operator, is_group, TqlType.BOOLEAN)

    def last_modified(self, operator: Enum, last_modified: Arrow | datetime | int | str):
        """Filter Last Modified based on **lastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            last_modified: The date the group was last modified.
        """
        last_modified = self.util.any_to_datetime(last_modified).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('lastModified', operator, last_modified, TqlType.STRING)

    def last_seen(self, operator: Enum, last_seen: Arrow | datetime | int | str):
        """Filter Last Seen based on **lastSeen** keyword.

        Args:
            operator: The operator enum for the filter.
            last_seen: The date and time that the group was last seen.
        """
        last_seen = self.util.any_to_datetime(last_seen).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('lastSeen', operator, last_seen, TqlType.STRING)

    def owner(self, operator: Enum, owner: int | list):
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The Owner ID for the group.
        """
        if isinstance(owner, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: list | str):
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name for the group.
        """
        if isinstance(owner_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def parent_group(self, operator: Enum, parent_group: int | list):
        """Filter parentGroup based on **parentGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            parent_group: No description provided.
        """
        if isinstance(parent_group, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('parentGroup', operator, parent_group, TqlType.INTEGER)

    def security_label(self, operator: Enum, security_label: list | str):
        """Filter Security Label based on **securityLabel** keyword.

        Args:
            operator: The operator enum for the filter.
            security_label: The name of a security label applied to the group.
        """
        if isinstance(security_label, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('securityLabel', operator, security_label, TqlType.STRING)

    def signature_date_added(
        self, operator: Enum, signature_date_added: Arrow | datetime | int | str
    ):
        """Filter Date Added (Signature) based on **signatureDateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            signature_date_added: The date the signature was added.
        """
        signature_date_added = self.util.any_to_datetime(signature_date_added).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('signatureDateAdded', operator, signature_date_added, TqlType.STRING)

    def signature_filename(self, operator: Enum, signature_filename: list | str):
        """Filter Filename (Signature) based on **signatureFilename** keyword.

        Args:
            operator: The operator enum for the filter.
            signature_filename: The file name of the signature.
        """
        if isinstance(signature_filename, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('signatureFilename', operator, signature_filename, TqlType.STRING)

    def signature_type(self, operator: Enum, signature_type: list | str):
        """Filter Type (Signature) based on **signatureType** keyword.

        Args:
            operator: The operator enum for the filter.
            signature_type: The type of signature.
        """
        if isinstance(signature_type, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('signatureType', operator, signature_type, TqlType.STRING)

    def status(self, operator: Enum, status: list | str):
        """Filter Status based on **status** keyword.

        Args:
            operator: The operator enum for the filter.
            status: Status of the group.
        """
        if isinstance(status, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('status', operator, status, TqlType.STRING)

    def summary(self, operator: Enum, summary: list | str):
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The summary (name) of the group.
        """
        if isinstance(summary, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('summary', operator, summary, TqlType.STRING)

    def tag(self, operator: Enum, tag: list | str):
        """Filter Tag based on **tag** keyword.

        Args:
            operator: The operator enum for the filter.
            tag: The name of a tag applied to the group.
        """
        if isinstance(tag, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('tag', operator, tag, TqlType.STRING)

    def tag_owner(self, operator: Enum, tag_owner: int | list):
        """Filter Tag Owner ID based on **tagOwner** keyword.

        Args:
            operator: The operator enum for the filter.
            tag_owner: The ID of the owner of a tag.
        """
        if isinstance(tag_owner, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('tagOwner', operator, tag_owner, TqlType.INTEGER)

    def tag_owner_name(self, operator: Enum, tag_owner_name: list | str):
        """Filter Tag Owner Name based on **tagOwnerName** keyword.

        Args:
            operator: The operator enum for the filter.
            tag_owner_name: The name of the owner of a tag.
        """
        if isinstance(tag_owner_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('tagOwnerName', operator, tag_owner_name, TqlType.STRING)

    def task_assignee(self, operator: Enum, task_assignee: list | str):
        """Filter Assignee (Task) based on **taskAssignee** keyword.

        Args:
            operator: The operator enum for the filter.
            task_assignee: The assignee of the task.
        """
        if isinstance(task_assignee, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('taskAssignee', operator, task_assignee, TqlType.STRING)

    def task_assignee_pseudo(self, operator: Enum, task_assignee_pseudo: list | str):
        """Filter Assignee Pseudonym (Task) based on **taskAssigneePseudo** keyword.

        Args:
            operator: The operator enum for the filter.
            task_assignee_pseudo: The pseudonym of the assignee of the task.
        """
        if isinstance(task_assignee_pseudo, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('taskAssigneePseudo', operator, task_assignee_pseudo, TqlType.STRING)

    def task_date_added(self, operator: Enum, task_date_added: Arrow | datetime | int | str):
        """Filter Date Added (Task) based on **taskDateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            task_date_added: The date the task was added.
        """
        task_date_added = self.util.any_to_datetime(task_date_added).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('taskDateAdded', operator, task_date_added, TqlType.STRING)

    def task_due_date(self, operator: Enum, task_due_date: Arrow | datetime | int | str):
        """Filter Due Date (Task) based on **taskDueDate** keyword.

        Args:
            operator: The operator enum for the filter.
            task_due_date: The due date of a task.
        """
        task_due_date = self.util.any_to_datetime(task_due_date).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('taskDueDate', operator, task_due_date, TqlType.STRING)

    def task_escalated(self, operator: Enum, task_escalated: bool):
        """Filter Escalated (Task) based on **taskEscalated** keyword.

        Args:
            operator: The operator enum for the filter.
            task_escalated: A flag indicating if a task has been escalated.
        """
        self._tql.add_filter('taskEscalated', operator, task_escalated, TqlType.BOOLEAN)

    def task_escalation_date(
        self, operator: Enum, task_escalation_date: Arrow | datetime | int | str
    ):
        """Filter Escalation Date (Task) based on **taskEscalationDate** keyword.

        Args:
            operator: The operator enum for the filter.
            task_escalation_date: The escalation date of a task.
        """
        task_escalation_date = self.util.any_to_datetime(task_escalation_date).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('taskEscalationDate', operator, task_escalation_date, TqlType.STRING)

    def task_last_modified(self, operator: Enum, task_last_modified: Arrow | datetime | int | str):
        """Filter Last Modified based on **taskLastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            task_last_modified: The date the group was last modified.
        """
        task_last_modified = self.util.any_to_datetime(task_last_modified).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('taskLastModified', operator, task_last_modified, TqlType.STRING)

    def task_overdue(self, operator: Enum, task_overdue: bool):
        """Filter Overdue (Task) based on **taskOverdue** keyword.

        Args:
            operator: The operator enum for the filter.
            task_overdue: A flag indicating if a task has become overdue.
        """
        self._tql.add_filter('taskOverdue', operator, task_overdue, TqlType.BOOLEAN)

    def task_reminded(self, operator: Enum, task_reminded: bool):
        """Filter Reminded (Task) based on **taskReminded** keyword.

        Args:
            operator: The operator enum for the filter.
            task_reminded: A flag indicating if a task has been reminded.
        """
        self._tql.add_filter('taskReminded', operator, task_reminded, TqlType.BOOLEAN)

    def task_reminder_date(self, operator: Enum, task_reminder_date: Arrow | datetime | int | str):
        """Filter Reminder Date (Task) based on **taskReminderDate** keyword.

        Args:
            operator: The operator enum for the filter.
            task_reminder_date: The reminder date of a task.
        """
        task_reminder_date = self.util.any_to_datetime(task_reminder_date).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('taskReminderDate', operator, task_reminder_date, TqlType.STRING)

    def task_status(self, operator: Enum, task_status: list | str):
        """Filter Status (Task) based on **taskStatus** keyword.

        Args:
            operator: The operator enum for the filter.
            task_status: The status of the task.
        """
        if isinstance(task_status, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('taskStatus', operator, task_status, TqlType.STRING)

    def type(self, operator: Enum, type: int | list):  # pylint: disable=redefined-builtin
        """Filter Type based on **type** keyword.

        Args:
            operator: The operator enum for the filter.
            type: The ID of the group type.
        """
        if isinstance(type, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('type', operator, type, TqlType.INTEGER)

    def type_name(self, operator: Enum, type_name: list | str):
        """Filter Type Name based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The name of the group type.
        """
        if isinstance(type_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('typeName', operator, type_name, TqlType.STRING)

    def upvote_count(self, operator: Enum, upvote_count: int | list):
        """Filter Upvote Count based on **upvoteCount** keyword.

        Args:
            operator: The operator enum for the filter.
            upvote_count: The number of upvotes the group has received.
        """
        if isinstance(upvote_count, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('upvoteCount', operator, upvote_count, TqlType.INTEGER)

    def victim_asset(self, operator: Enum, victim_asset: list | str):
        """Filter victimAsset based on **victimAsset** keyword.

        Args:
            operator: The operator enum for the filter.
            victim_asset: No description provided.
        """
        if isinstance(victim_asset, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('victimAsset', operator, victim_asset, TqlType.STRING)
