"""Group TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class GroupFilter(FilterABC):
    """Filter Object for Groups"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.GROUPS.value

    def associated_indicator(self, operator: Enum, associated_indicator: int) -> None:
        """Filter associatedIndicator based on **associatedIndicator** keyword.

        Args:
            operator: The operator enum for the filter.
            associated_indicator: None.
        """
        self._tql.add_filter('associatedIndicator', operator, associated_indicator, TQL.Type.INTEGER)

    def attribute(self, operator: Enum, attribute: str) -> None:
        """Filter attribute based on **attribute** keyword.

        Args:
            operator: The operator enum for the filter.
            attribute: None.
        """
        self._tql.add_filter('attribute', operator, attribute, TQL.Type.STRING)

    def child_group(self, operator: Enum, child_group: int) -> None:
        """Filter childGroup based on **childGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            child_group: None.
        """
        self._tql.add_filter('childGroup', operator, child_group, TQL.Type.INTEGER)

    def created_by(self, operator: Enum, created_by: str) -> None:
        """Filter Created By based on **createdBy** keyword.

        Args:
            operator: The operator enum for the filter.
            created_by: The user who created the group.
        """
        self._tql.add_filter('createdBy', operator, created_by, TQL.Type.STRING)

    def date_added(self, operator: Enum, date_added: str) -> None:
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the group was added to the system.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

    def document_date_added(self, operator: Enum, document_date_added: str) -> None:
        """Filter Date Added (Document) based on **documentDateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            document_date_added: The date the document was added.
        """
        self._tql.add_filter('documentDateAdded', operator, document_date_added, TQL.Type.STRING)

    def document_filename(self, operator: Enum, document_filename: str) -> None:
        """Filter Filename (Document) based on **documentFilename** keyword.

        Args:
            operator: The operator enum for the filter.
            document_filename: The file name of the document.
        """
        self._tql.add_filter('documentFilename', operator, document_filename, TQL.Type.STRING)

    def document_filesize(self, operator: Enum, document_filesize: int) -> None:
        """Filter File Size (Document) based on **documentFilesize** keyword.

        Args:
            operator: The operator enum for the filter.
            document_filesize: The filesize of the document.
        """
        self._tql.add_filter('documentFilesize', operator, document_filesize, TQL.Type.INTEGER)

    def document_status(self, operator: Enum, document_status: str) -> None:
        """Filter Status (Document) based on **documentStatus** keyword.

        Args:
            operator: The operator enum for the filter.
            document_status: The status of the document.
        """
        self._tql.add_filter('documentStatus', operator, document_status, TQL.Type.STRING)

    def document_type(self, operator: Enum, document_type: str) -> None:
        """Filter Type (Document) based on **documentType** keyword.

        Args:
            operator: The operator enum for the filter.
            document_type: The type of document.
        """
        self._tql.add_filter('documentType', operator, document_type, TQL.Type.STRING)

    def downvote_count(self, operator: Enum, downvote_count: int) -> None:
        """Filter Downvote Count based on **downvoteCount** keyword.

        Args:
            operator: The operator enum for the filter.
            downvote_count: The number of downvotes the group has received.
        """
        self._tql.add_filter('downvoteCount', operator, downvote_count, TQL.Type.INTEGER)

    def email_date(self, operator: Enum, email_date: str) -> None:
        """Filter Date (Email) based on **emailDate** keyword.

        Args:
            operator: The operator enum for the filter.
            email_date: The date of the email.
        """
        self._tql.add_filter('emailDate', operator, email_date, TQL.Type.STRING)

    def email_from(self, operator: Enum, email_from: str) -> None:
        """Filter From (Email) based on **emailFrom** keyword.

        Args:
            operator: The operator enum for the filter.
            email_from: The 'from' field of the email.
        """
        self._tql.add_filter('emailFrom', operator, email_from, TQL.Type.STRING)

    def email_score(self, operator: Enum, email_score: int) -> None:
        """Filter Score (Email) based on **emailScore** keyword.

        Args:
            operator: The operator enum for the filter.
            email_score: The score of the email.
        """
        self._tql.add_filter('emailScore', operator, email_score, TQL.Type.INTEGER)

    def email_score_includes_body(self, operator: Enum, email_score_includes_body: bool) -> None:
        """Filter Score Includes Body (Email) based on **emailScoreIncludesBody** keyword.

        Args:
            operator: The operator enum for the filter.
            email_score_includes_body: A true/false indicating if the body was included in the scoring of the email.
        """
        self._tql.add_filter('emailScoreIncludesBody', operator, email_score_includes_body, TQL.Type.BOOLEAN)

    def email_subject(self, operator: Enum, email_subject: str) -> None:
        """Filter Subject (Email) based on **emailSubject** keyword.

        Args:
            operator: The operator enum for the filter.
            email_subject: The subject of the email.
        """
        self._tql.add_filter('emailSubject', operator, email_subject, TQL.Type.STRING)

    def event_date(self, operator: Enum, event_date: str) -> None:
        """Filter Event Date based on **eventDate** keyword.

        Args:
            operator: The operator enum for the filter.
            event_date: The event date of the group.
        """
        self._tql.add_filter('eventDate', operator, event_date, TQL.Type.STRING)

    @property
    def has_artifact(self):
        """Return **FilterArtifacts** for further filtering."""
        from tcex.api.tc.v3.artifacts.filter import ArtifactFilter

        artifacts = FilterArtifacts(ApiEndpoints.ARTIFACTS, self._tcex, TQL())
        self._tql.add_filter('hasArtifact', TQL.Operator.EQ, artifacts, TQL.Type.SUB_QUERY)
        return artifacts

    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        from tcex.api.tc.v3.cases.filter import CaseFilter

        cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    def has_group(self, operator: Enum, has_group: int) -> None:
        """Filter Associated Group based on **hasGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            has_group: A nested query for association to other groups.
        """
        self._tql.add_filter('hasGroup', operator, has_group, TQL.Type.INTEGER)

    def has_indicator(self, operator: Enum, has_indicator: int) -> None:
        """Filter Associated Indicator based on **hasIndicator** keyword.

        Args:
            operator: The operator enum for the filter.
            has_indicator: A nested query for association to other indicators.
        """
        self._tql.add_filter('hasIndicator', operator, has_indicator, TQL.Type.INTEGER)

    @property
    def has_tag(self):
        """Return **FilterTags** for further filtering."""
        from tcex.api.tc.v3.tags.filter import TagFilter

        tags = FilterTags(ApiEndpoints.TAGS, self._tcex, TQL())
        self._tql.add_filter('hasTag', TQL.Operator.EQ, tags, TQL.Type.SUB_QUERY)
        return tags

    def has_victim(self, operator: Enum, has_victim: int) -> None:
        """Filter Associated Victim based on **hasVictim** keyword.

        Args:
            operator: The operator enum for the filter.
            has_victim: A nested query for association to other victims.
        """
        self._tql.add_filter('hasVictim', operator, has_victim, TQL.Type.INTEGER)

    def has_victimasset(self, operator: Enum, has_victimasset: int) -> None:
        """Filter Associated Victim Asset based on **hasVictimasset** keyword.

        Args:
            operator: The operator enum for the filter.
            has_victimasset: A nested query for association to other victim assets.
        """
        self._tql.add_filter('hasVictimasset', operator, has_victimasset, TQL.Type.INTEGER)

    def hasattribute(self, operator: Enum, hasattribute: int) -> None:
        """Filter Associated Attribute based on **hasattribute** keyword.

        Args:
            operator: The operator enum for the filter.
            hasattribute: A nested query for association to attributes.
        """
        self._tql.add_filter('hasattribute', operator, hasattribute, TQL.Type.INTEGER)

    def hassecuritylabel(self, operator: Enum, hassecuritylabel: int) -> None:
        """Filter Associated Security Label based on **hassecuritylabel** keyword.

        Args:
            operator: The operator enum for the filter.
            hassecuritylabel: A nested query for association to other security labels.
        """
        self._tql.add_filter('hassecuritylabel', operator, hassecuritylabel, TQL.Type.INTEGER)

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the group.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def is_group(self, operator: Enum, is_group: bool) -> None:
        """Filter isGroup based on **isGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            is_group: None.
        """
        self._tql.add_filter('isGroup', operator, is_group, TQL.Type.BOOLEAN)

    def owner(self, operator: Enum, owner: int) -> None:
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The Owner ID for the group.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str) -> None:
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name for the group.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TQL.Type.STRING)

    def parent_group(self, operator: Enum, parent_group: int) -> None:
        """Filter parentGroup based on **parentGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            parent_group: None.
        """
        self._tql.add_filter('parentGroup', operator, parent_group, TQL.Type.INTEGER)

    def security_label(self, operator: Enum, security_label: str) -> None:
        """Filter Security Label based on **securityLabel** keyword.

        Args:
            operator: The operator enum for the filter.
            security_label: The name of a security label applied to the group.
        """
        self._tql.add_filter('securityLabel', operator, security_label, TQL.Type.STRING)

    def signature_date_added(self, operator: Enum, signature_date_added: str) -> None:
        """Filter Date Added (Signature) based on **signatureDateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            signature_date_added: The date the signature was added.
        """
        self._tql.add_filter('signatureDateAdded', operator, signature_date_added, TQL.Type.STRING)

    def signature_filename(self, operator: Enum, signature_filename: str) -> None:
        """Filter Filename (Signature) based on **signatureFilename** keyword.

        Args:
            operator: The operator enum for the filter.
            signature_filename: The file name of the signature.
        """
        self._tql.add_filter('signatureFilename', operator, signature_filename, TQL.Type.STRING)

    def signature_type(self, operator: Enum, signature_type: str) -> None:
        """Filter Type (Signature) based on **signatureType** keyword.

        Args:
            operator: The operator enum for the filter.
            signature_type: The type of signature.
        """
        self._tql.add_filter('signatureType', operator, signature_type, TQL.Type.STRING)

    def status(self, operator: Enum, status: str) -> None:
        """Filter Status based on **status** keyword.

        Args:
            operator: The operator enum for the filter.
            status: Status of the group.
        """
        self._tql.add_filter('status', operator, status, TQL.Type.STRING)

    def summary(self, operator: Enum, summary: str) -> None:
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The summary (name) of the group.
        """
        self._tql.add_filter('summary', operator, summary, TQL.Type.STRING)

    def tag(self, operator: Enum, tag: str) -> None:
        """Filter Tag based on **tag** keyword.

        Args:
            operator: The operator enum for the filter.
            tag: The name of a tag applied to the group.
        """
        self._tql.add_filter('tag', operator, tag, TQL.Type.STRING)

    def tag_owner(self, operator: Enum, tag_owner: int) -> None:
        """Filter Tag Owner ID based on **tagOwner** keyword.

        Args:
            operator: The operator enum for the filter.
            tag_owner: The ID of the owner of a tag.
        """
        self._tql.add_filter('tagOwner', operator, tag_owner, TQL.Type.INTEGER)

    def tag_owner_name(self, operator: Enum, tag_owner_name: str) -> None:
        """Filter Tag Owner Name based on **tagOwnerName** keyword.

        Args:
            operator: The operator enum for the filter.
            tag_owner_name: The name of the owner of a tag.
        """
        self._tql.add_filter('tagOwnerName', operator, tag_owner_name, TQL.Type.STRING)

    def task_assignee(self, operator: Enum, task_assignee: str) -> None:
        """Filter Assignee (Task) based on **taskAssignee** keyword.

        Args:
            operator: The operator enum for the filter.
            task_assignee: The assignee of the task.
        """
        self._tql.add_filter('taskAssignee', operator, task_assignee, TQL.Type.STRING)

    def task_assignee_pseudo(self, operator: Enum, task_assignee_pseudo: str) -> None:
        """Filter Assignee Pseudonym (Task) based on **taskAssigneePseudo** keyword.

        Args:
            operator: The operator enum for the filter.
            task_assignee_pseudo: The pseudonym of the assignee of the task.
        """
        self._tql.add_filter('taskAssigneePseudo', operator, task_assignee_pseudo, TQL.Type.STRING)

    def task_date_added(self, operator: Enum, task_date_added: str) -> None:
        """Filter Date Added (Task) based on **taskDateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            task_date_added: The date the task was added.
        """
        self._tql.add_filter('taskDateAdded', operator, task_date_added, TQL.Type.STRING)

    def task_due_date(self, operator: Enum, task_due_date: str) -> None:
        """Filter Due Date (Task) based on **taskDueDate** keyword.

        Args:
            operator: The operator enum for the filter.
            task_due_date: The due date of a task.
        """
        self._tql.add_filter('taskDueDate', operator, task_due_date, TQL.Type.STRING)

    def task_escalated(self, operator: Enum, task_escalated: bool) -> None:
        """Filter Escalated (Task) based on **taskEscalated** keyword.

        Args:
            operator: The operator enum for the filter.
            task_escalated: A flag indicating if a task has been escalated.
        """
        self._tql.add_filter('taskEscalated', operator, task_escalated, TQL.Type.BOOLEAN)

    def task_escalation_date(self, operator: Enum, task_escalation_date: str) -> None:
        """Filter Escalation Date (Task) based on **taskEscalationDate** keyword.

        Args:
            operator: The operator enum for the filter.
            task_escalation_date: The escalation date of a task.
        """
        self._tql.add_filter('taskEscalationDate', operator, task_escalation_date, TQL.Type.STRING)

    def task_last_modified(self, operator: Enum, task_last_modified: str) -> None:
        """Filter Last Modified (Task) based on **taskLastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            task_last_modified: The date the task was last modified.
        """
        self._tql.add_filter('taskLastModified', operator, task_last_modified, TQL.Type.STRING)

    def task_overdue(self, operator: Enum, task_overdue: bool) -> None:
        """Filter Overdue (Task) based on **taskOverdue** keyword.

        Args:
            operator: The operator enum for the filter.
            task_overdue: A flag indicating if a task has become overdue.
        """
        self._tql.add_filter('taskOverdue', operator, task_overdue, TQL.Type.BOOLEAN)

    def task_reminded(self, operator: Enum, task_reminded: bool) -> None:
        """Filter Reminded (Task) based on **taskReminded** keyword.

        Args:
            operator: The operator enum for the filter.
            task_reminded: A flag indicating if a task has been reminded.
        """
        self._tql.add_filter('taskReminded', operator, task_reminded, TQL.Type.BOOLEAN)

    def task_reminder_date(self, operator: Enum, task_reminder_date: str) -> None:
        """Filter Reminder Date (Task) based on **taskReminderDate** keyword.

        Args:
            operator: The operator enum for the filter.
            task_reminder_date: The reminder date of a task.
        """
        self._tql.add_filter('taskReminderDate', operator, task_reminder_date, TQL.Type.STRING)

    def task_status(self, operator: Enum, task_status: str) -> None:
        """Filter Status (Task) based on **taskStatus** keyword.

        Args:
            operator: The operator enum for the filter.
            task_status: The status of the task.
        """
        self._tql.add_filter('taskStatus', operator, task_status, TQL.Type.STRING)

    def type(self, operator: Enum, type: int) -> None:  # pylint: disable=redefined-builtin
        """Filter Type based on **type** keyword.

        Args:
            operator: The operator enum for the filter.
            type: The ID of the group type.
        """
        self._tql.add_filter('type', operator, type, TQL.Type.INTEGER)

    def type_name(self, operator: Enum, type_name: str) -> None:
        """Filter Type Name based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The name of the group type.
        """
        self._tql.add_filter('typeName', operator, type_name, TQL.Type.STRING)

    def upvote_count(self, operator: Enum, upvote_count: int) -> None:
        """Filter Upvote Count based on **upvoteCount** keyword.

        Args:
            operator: The operator enum for the filter.
            upvote_count: The number of upvotes the group has received.
        """
        self._tql.add_filter('upvoteCount', operator, upvote_count, TQL.Type.INTEGER)

    def victim_asset(self, operator: Enum, victim_asset: str) -> None:
        """Filter victimAsset based on **victimAsset** keyword.

        Args:
            operator: The operator enum for the filter.
            victim_asset: None.
        """
        self._tql.add_filter('victimAsset', operator, victim_asset, TQL.Type.STRING)
