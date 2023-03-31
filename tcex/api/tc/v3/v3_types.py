"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    # from tcex.api.tc.v3.adversary_assets.adversary_asset import AdversaryAsset
    from tcex.api.tc.v3.artifact_types.artifact_type import ArtifactType
    from tcex.api.tc.v3.artifacts.artifact import Artifact
    from tcex.api.tc.v3.cases.case import Case
    from tcex.api.tc.v3.groups.group import Group
    from tcex.api.tc.v3.indicators.indicator import Indicator
    from tcex.api.tc.v3.notes.note import Note
    from tcex.api.tc.v3.security.owner_roles.owner_role import OwnerRole
    from tcex.api.tc.v3.security.owners.owner import Owner
    from tcex.api.tc.v3.security.system_roles.system_role import SystemRole
    from tcex.api.tc.v3.security.user_groups.user_group import UserGroup
    from tcex.api.tc.v3.security.users.user import User
    from tcex.api.tc.v3.tags.tag import Tag
    from tcex.api.tc.v3.tasks.task import Task
    from tcex.api.tc.v3.victim_assets.victim_asset import VictimAsset
    from tcex.api.tc.v3.victims.victim import Victim
    from tcex.api.tc.v3.workflow_events.workflow_event import WorkflowEvent
    from tcex.api.tc.v3.workflow_templates.workflow_template import WorkflowTemplate

    V3Type = (
        # AdversaryAsset
        ArtifactType
        | Artifact
        | Case
        | Group
        | Indicator
        | Note
        | OwnerRole
        | Owner
        | SystemRole
        | UserGroup
        | User
        | Tag
        | Task
        | VictimAsset
        | Victim
        | WorkflowEvent
        | WorkflowTemplate
    )
