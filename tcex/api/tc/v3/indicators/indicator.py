"""Indicator / Indicators Object"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.indicators.indicator_filter import IndicatorFilter
from tcex.api.tc.v3.indicators.indicator_model import IndicatorModel, IndicatorsModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tags.tag_model import TagModel
from tcex.api.tc.v3.tql.tql_operator import TqlOperator

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.tags.tag import Tag


class Indicators(ObjectCollectionABC):
    """Indicators Collection.

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
        self._model = IndicatorsModel(**kwargs)
        self._type = 'indicators'

    def __iter__(self) -> 'Indicator':
        """Iterate over CM objects."""
        return self.iterate(base_class=Indicator)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.INDICATORS.value

    @property
    def filter(self) -> 'IndicatorFilter':
        """Return the type specific filter object."""
        return IndicatorFilter(self.tql)


class Indicator(ObjectABC):
    """Indicators Object.

    Args:
        active (bool, kwargs): Is the indicator active?
        active_locked (bool, kwargs): Lock the indicator active value?
        address (str, kwargs): The email address associated with this indicator (EmailAddress
            specific summary field).
        associated_groups (Groups, kwargs): A list of groups that this indicator is associated with.
        associated_indicators (Indicators, kwargs): A list of indicators associated with this
            indicator.
        attributes (IndicatorAttributes, kwargs): A list of Attributes corresponding to the
            Indicator.
        confidence (int, kwargs): The indicator threat confidence.
        description (str, kwargs): The indicator description text.
        dns_active (bool, kwargs): Is dns active for the indicator?
        host_name (str, kwargs): The host name of the indicator (Host specific summary field).
        ip (str, kwargs): The ip address associated with this indicator (Address specific summary
            field).
        md5 (str, kwargs): The md5 associated with this indicator (File specific summary field).
        private_flag (bool, kwargs): Is this indicator private?
        rating (int, kwargs): The indicator threat rating.
        security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
            Intel item (NOTE: Setting this parameter will replace any existing tag(s) with the
            one(s) specified).
        sha1 (str, kwargs): The sha1 associated with this indicator (File specific summary field).
        sha256 (str, kwargs): The sha256 associated with this indicator (File specific summary
            field).
        size (int, kwargs): The size of the file.
        source (str, kwargs): The source for this indicator.
        tags (Tags, kwargs): A list of Tags corresponding to the item (NOTE: Setting this parameter
            will replace any existing tag(s) with the one(s) specified).
        text (str, kwargs): The url text value of the indicator (Url specific summary field).
        type (str, kwargs): The **type** for the Indicator.
        value1 (str, kwargs): Custom Indicator summary field value1.
        value2 (str, kwargs): Custom Indicator summary field value2.
        value3 (str, kwargs): Custom Indicator summary field value3.
        whois_active (bool, kwargs): Is whois active for the indicator?
        xid (str, kwargs): The xid of the item.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))
        self._model = IndicatorModel(**kwargs)
        self.type_ = 'Indicator'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.INDICATORS.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'indicator_id',
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
