"""AdversaryAsset / AdversaryAssets Object"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.adversary_assets.adversary_asset_filter import AdversaryAssetFilter
from tcex.api.tc.v3.adversary_assets.adversary_asset_model import (
    AdversaryAssetModel,
    AdversaryAssetsModel,
)
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.groups.group_model import GroupModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.groups.group import Group


class AdversaryAssets(ObjectCollectionABC):
    """AdversaryAssets Collection.

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
        self._model = AdversaryAssetsModel(**kwargs)
        self.type_ = 'adversary_assets'

    def __iter__(self) -> 'AdversaryAsset':
        """Iterate over CM objects."""
        return self.iterate(base_class=AdversaryAsset)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ADVERSARY_ASSETS.value

    @property
    def filter(self) -> 'AdversaryAssetFilter':
        """Return the type specific filter object."""
        return AdversaryAssetFilter(self.tql)


class AdversaryAsset(ObjectABC):
    """AdversaryAssets Object.

    Args:
        account_name (str, kwargs): The network name.
        address (str, kwargs): The email address associated with the E-Mail Address asset.
        address_type (str, kwargs): The type of the E-Mail Address asset.
        associated_groups (Groups, kwargs): A list of groups that this victim asset is associated
            with.
        network_type (str, kwargs): The type of network.
        phone (str, kwargs): The phone number of the asset.
        social_network (str, kwargs): The type of social network.
        type (str, kwargs): Type of victim asset.
        victim_id (int, kwargs): Victim id of victim asset.
        website (str, kwargs): The website of the asset.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = AdversaryAssetModel(**kwargs)
        self._nested_filter = 'has_adversary_asset'
        self.type_ = 'Adversary Asset'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ADVERSARY_ASSETS.value

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_
        if hasattr(self.model, 'type'):
            type_ = self.model.type

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}

    def add_associated_group(self, **kwargs) -> None:
        """Add group to the object.

        Args:
            attributes (GroupAttributes, kwargs): A list of Attributes corresponding to the Group.
            body (str, kwargs): The email Body.
            due_date (str, kwargs): The date and time that the Task is due.
            escalation_date (str, kwargs): The escalation date and time.
            event_date (str, kwargs): The date and time that the incident or event was first
                created.
            file_name (str, kwargs): The document or signature file name.
            file_text (str, kwargs): The signature file text.
            file_type (str, kwargs): The signature file type.
            first_seen (str, kwargs): The date and time that the campaign was first created.
            from_ (str, kwargs): The email From field.
            header (str, kwargs): The email Header field.
            malware (bool, kwargs): Is the document malware?
            name (str, kwargs): The name of the group.
            owner_name (str, kwargs): The name of the Organization, Community, or Source that the
                item belongs to.
            password (str, kwargs): The password associated with the document (Required if Malware
                is true).
            publish_date (str, kwargs): The date and time that the report was first created.
            reminder_date (str, kwargs): The reminder date and time.
            status (str, kwargs): The status associated with this document, event, task, or incident
                (read only for task, document, and report).
            subject (str, kwargs): The email Subject section.
            to (str, kwargs): The email To field .
            type (str, kwargs): The **type** for the Group.
            xid (str, kwargs): The xid of the item.
        """
        self.model.associated_groups.data.append(GroupModel(**kwargs))

    @property
    def associated_groups(self) -> 'Group':
        """Yield Group from Groups."""
        # first-party
        from tcex.api.tc.v3.groups.group import Groups

        yield from self._iterate_over_sublist(Groups)
