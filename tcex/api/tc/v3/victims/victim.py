"""Victim / Victims Object"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelModel
from tcex.api.tc.v3.tags.tag_model import TagModel
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.victim_attributes.victim_attribute_model import VictimAttributeModel
from tcex.api.tc.v3.victims.victim_filter import VictimFilter
from tcex.api.tc.v3.victims.victim_model import VictimModel, VictimsModel

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.security_labels.security_label import SecurityLabel
    from tcex.api.tc.v3.tags.tag import Tag
    from tcex.api.tc.v3.victim_attributes.victim_attribute import VictimAttribute


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
        self.type_ = 'victims'

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
        assets (VictimAssets, kwargs): A list of victim assets corresponding to the Victim.
        associated_groups (Groups, kwargs): A list of groups that this victim is associated with.
        attributes (VictimAttributes, kwargs): A list of Attributes corresponding to the Victim.
        description (str, kwargs): Description of the Victim.
        name (str, kwargs): Name of the Victim.
        nationality (str, kwargs): Nationality of the Victim.
        org (str, kwargs): Org of the Victim.
        owner_name (str, kwargs): The name of the Organization, Community, or Source that the item
            belongs to.
        security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
            Intel item (NOTE: Setting this parameter will replace any existing tag(s) with
            the one(s) specified).
        suborg (str, kwargs): Suborg of the Victim.
        tags (Tags, kwargs): A list of Tags corresponding to the item (NOTE: Setting this parameter
            will replace any existing tag(s) with the one(s) specified).
        type (str, kwargs): The **type** for the Victim.
        work_location (str, kwargs): Work location of the Victim.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))
        self._model = VictimModel(**kwargs)
        self.type_ = 'Victim'

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
        type_ = self.type_
        if hasattr(self.model, 'type'):
            type_ = self.model.type

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}

    def add_attribute(self, **kwargs) -> None:
        """Add attribute to the object.

        Args:
            default (bool, kwargs): A flag indicating that this is the default attribute of its type
                within the object. Only applies to certain attribute and data types.
            source (str, kwargs): The attribute source.
            value (str, kwargs): Attribute value.
        """
        self.model.attributes.data.append(VictimAttributeModel(**kwargs))

    def add_security_label(self, **kwargs) -> None:
        """Add security_label to the object.

        Args:
            color (str, kwargs): Color of the security label.
            description (str, kwargs): Description of the security label.
            name (str, kwargs): Name of the security label.
        """
        self.model.security_labels.data.append(SecurityLabelModel(**kwargs))

    def add_tag(self, **kwargs) -> None:
        """Add tag to the object.

        Args:
            description (str, kwargs): A brief description of the Tag.
            name (str, kwargs): The **name** for the Tag.
        """
        self.model.tags.data.append(TagModel(**kwargs))

    @property
    def attributes(self) -> 'VictimAttribute':
        """Yield Attribute from Attributes."""
        # first-party
        from tcex.api.tc.v3.victim_attributes.victim_attribute import VictimAttributes

        yield from self._iterate_over_sublist(VictimAttributes)

    @property
    def security_labels(self) -> 'SecurityLabel':
        """Yield Security_Label from Security_Labels."""
        # first-party
        from tcex.api.tc.v3.security_labels.security_label import SecurityLabels

        yield from self._iterate_over_sublist(SecurityLabels)

    @property
    def tags(self) -> 'Tag':
        """Yield Tag from Tags."""
        # first-party
        from tcex.api.tc.v3.tags.tag import Tags

        yield from self._iterate_over_sublist(Tags)
