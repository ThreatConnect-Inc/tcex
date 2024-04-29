"""TcEx Framework Module"""

# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class OwnerFilter(FilterABC):
    """Filter Object for Owners"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.OWNERS.value

    def id(self, operator: Enum, id: int | list):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the Community Membership.
        """
        if isinstance(id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def owner_id(self, operator: Enum, owner_id: int | list):
        """Filter Owner ID based on **ownerId** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_id: The ID of the Owner.
        """
        if isinstance(owner_id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('ownerId', operator, owner_id, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: list | str):
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The name of the Owner.
        """
        if isinstance(owner_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def perm_apps(self, operator: Enum, perm_apps: list | str):
        """Filter Apps Permission based on **permApps** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_apps: The User's Apps permission in the Owner.
        """
        if isinstance(perm_apps, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permApps', operator, perm_apps, TqlType.STRING)

    def perm_artifact(self, operator: Enum, perm_artifact: list | str):
        """Filter Artifact Permission based on **permArtifact** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_artifact: The User's Artifact permission in the Owner.
        """
        if isinstance(perm_artifact, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permArtifact', operator, perm_artifact, TqlType.STRING)

    def perm_attribute(self, operator: Enum, perm_attribute: list | str):
        """Filter Attribute Permission based on **permAttribute** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_attribute: The User's Attribute permission in the Owner.
        """
        if isinstance(perm_attribute, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permAttribute', operator, perm_attribute, TqlType.STRING)

    def perm_attribute_type(self, operator: Enum, perm_attribute_type: list | str):
        """Filter AttributeType Permission based on **permAttributeType** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_attribute_type: The User's AttributeType permission in the Owner.
        """
        if isinstance(perm_attribute_type, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permAttributeType', operator, perm_attribute_type, TqlType.STRING)

    def perm_case_tag(self, operator: Enum, perm_case_tag: list | str):
        """Filter CaseTag Permission based on **permCaseTag** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_case_tag: The User's CaseTag permission in the Owner.
        """
        if isinstance(perm_case_tag, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permCaseTag', operator, perm_case_tag, TqlType.STRING)

    def perm_comment(self, operator: Enum, perm_comment: list | str):
        """Filter Comment Permission based on **permComment** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_comment: The User's Comment permission in the Owner.
        """
        if isinstance(perm_comment, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permComment', operator, perm_comment, TqlType.STRING)

    def perm_copy_data(self, operator: Enum, perm_copy_data: list | str):
        """Filter CopyData Permission based on **permCopyData** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_copy_data: The User's CopyData permission in the Owner.
        """
        if isinstance(perm_copy_data, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permCopyData', operator, perm_copy_data, TqlType.STRING)

    def perm_group(self, operator: Enum, perm_group: list | str):
        """Filter Group Permission based on **permGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_group: The User's Group permission in the Owner.
        """
        if isinstance(perm_group, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permGroup', operator, perm_group, TqlType.STRING)

    def perm_indicator(self, operator: Enum, perm_indicator: list | str):
        """Filter Indicator Permission based on **permIndicator** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_indicator: The User's Indicator permission in the Owner.
        """
        if isinstance(perm_indicator, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permIndicator', operator, perm_indicator, TqlType.STRING)

    def perm_invite(self, operator: Enum, perm_invite: list | str):
        """Filter Invite Permission based on **permInvite** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_invite: The User's Invite permission in the Owner.
        """
        if isinstance(perm_invite, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permInvite', operator, perm_invite, TqlType.STRING)

    def perm_members(self, operator: Enum, perm_members: list | str):
        """Filter Members Permission based on **permMembers** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_members: The User's Members permission in the Owner.
        """
        if isinstance(perm_members, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permMembers', operator, perm_members, TqlType.STRING)

    def perm_playbooks(self, operator: Enum, perm_playbooks: list | str):
        """Filter Playbooks Permission based on **permPlaybooks** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_playbooks: The User's Playbooks permission in the Owner.
        """
        if isinstance(perm_playbooks, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permPlaybooks', operator, perm_playbooks, TqlType.STRING)

    def perm_playbooks_execute(self, operator: Enum, perm_playbooks_execute: list | str):
        """Filter PlaybooksExecute Permission based on **permPlaybooksExecute** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_playbooks_execute: The User's PlaybooksExecute permission in the Owner.
        """
        if isinstance(perm_playbooks_execute, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter(
            'permPlaybooksExecute', operator, perm_playbooks_execute, TqlType.STRING
        )

    def perm_post(self, operator: Enum, perm_post: list | str):
        """Filter Post Permission based on **permPost** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_post: The User's Post permission in the Owner.
        """
        if isinstance(perm_post, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permPost', operator, perm_post, TqlType.STRING)

    def perm_publish(self, operator: Enum, perm_publish: list | str):
        """Filter Publish Permission based on **permPublish** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_publish: The User's Publish permission in the Owner.
        """
        if isinstance(perm_publish, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permPublish', operator, perm_publish, TqlType.STRING)

    def perm_security_label(self, operator: Enum, perm_security_label: list | str):
        """Filter SecurityLabel Permission based on **permSecurityLabel** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_security_label: The User's SecurityLabel permission in the Owner.
        """
        if isinstance(perm_security_label, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permSecurityLabel', operator, perm_security_label, TqlType.STRING)

    def perm_settings(self, operator: Enum, perm_settings: list | str):
        """Filter Settings Permission based on **permSettings** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_settings: The User's Settings permission in the Owner.
        """
        if isinstance(perm_settings, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permSettings', operator, perm_settings, TqlType.STRING)

    def perm_tag(self, operator: Enum, perm_tag: list | str):
        """Filter Tag Permission based on **permTag** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_tag: The User's Tag permission in the Owner.
        """
        if isinstance(perm_tag, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permTag', operator, perm_tag, TqlType.STRING)

    def perm_task(self, operator: Enum, perm_task: list | str):
        """Filter Task Permission based on **permTask** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_task: The User's Task permission in the Owner.
        """
        if isinstance(perm_task, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permTask', operator, perm_task, TqlType.STRING)

    def perm_timeline(self, operator: Enum, perm_timeline: list | str):
        """Filter Timeline Permission based on **permTimeline** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_timeline: The User's Timeline permission in the Owner.
        """
        if isinstance(perm_timeline, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permTimeline', operator, perm_timeline, TqlType.STRING)

    def perm_track(self, operator: Enum, perm_track: list | str):
        """Filter Track Permission based on **permTrack** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_track: The User's Track permission in the Owner.
        """
        if isinstance(perm_track, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permTrack', operator, perm_track, TqlType.STRING)

    def perm_users(self, operator: Enum, perm_users: list | str):
        """Filter Users Permission based on **permUsers** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_users: The User's Users permission in the Owner.
        """
        if isinstance(perm_users, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permUsers', operator, perm_users, TqlType.STRING)

    def perm_victim(self, operator: Enum, perm_victim: list | str):
        """Filter Victim Permission based on **permVictim** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_victim: The User's Victim permission in the Owner.
        """
        if isinstance(perm_victim, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('permVictim', operator, perm_victim, TqlType.STRING)

    def perm_workflow_template(self, operator: Enum, perm_workflow_template: list | str):
        """Filter WorkflowTemplate Permission based on **permWorkflowTemplate** keyword.

        Args:
            operator: The operator enum for the filter.
            perm_workflow_template: The User's WorkflowTemplate permission in the Owner.
        """
        if isinstance(perm_workflow_template, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter(
            'permWorkflowTemplate', operator, perm_workflow_template, TqlType.STRING
        )

    def user_id(self, operator: Enum, user_id: int | list):
        """Filter User ID based on **userId** keyword.

        Args:
            operator: The operator enum for the filter.
            user_id: The ID of the user.
        """
        if isinstance(user_id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('userId', operator, user_id, TqlType.INTEGER)
