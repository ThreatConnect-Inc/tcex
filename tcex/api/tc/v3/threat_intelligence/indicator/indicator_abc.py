"""Indicator Abstract Base Class"""
from tcex.api.v3.threat_intelligence.threat_intelligence_abc import ThreatIntelligenceABC
from tcex.api.v3.threat_intelligence.indicator.api_endpoints import ApiEndpoints
from tcex.api.tql import Operator


class IndicatorABC(ThreatIntelligenceABC):

    def __init__(self, session):
        super().__init__(session, 'Indicator')

    def _base_filter(self) -> dict:
        return {
            'keyword': 'id',
            'operator': Operator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

        # TODO: [low] does this output a dict or json string?

    def _generate_body(self, method: str) -> dict:
        """Return the generated POST body."""
        schema = self.model.schema()
        properties = schema.get('properties', schema)
        valid_fields = {}
        filtered_fields = {**self.model.dict(exclude_unset=True), **self.model.dict(exclude_none=True)}
        for key, value in filtered_fields.items():
            supported_methods = properties.get(key).get('methods', [])
            if method.upper() in supported_methods:
                valid_fields[key] = value
        return valid_fields

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.INDICATORS.value

    @property
    def as_entity(self):
        """Return the entity representation of the Note."""
        return {'type': self.model.type, 'value': self.model.summary, 'id': self.model.id}