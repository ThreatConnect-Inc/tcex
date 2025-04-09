"""TcEx Framework Module"""

# standard library
from collections.abc import Generator
from typing import Any

# third-party
from pydantic import ValidationError
from requests.exceptions import ProxyError

# first-party
from tcex.api.tc.v3._gen._options_abc import OptionsABC
from tcex.api.tc.v3._gen.model._filter_model import FilterModel
from tcex.pleb.cached_property import cached_property
from tcex.util.render.render import Render

# The OptionsData class is used to download the options data for a given object type and
# correct and/or update the data to ensure it is usable for the code generation process.
# The "plan" is to have a single class that handles downloading the data and updating it.
# The contents* methods download, update, and load to the model. The content_models method
# is typically the entry point to this class.


class OptionsDataFilter(OptionsABC):
    """Gen Model Download Options Class"""

    def __init__(self, api_url: str, object_type: str):
        """Initialize instance properties."""
        self.api_url = api_url
        self.object_type = object_type

        # properties
        self.messages = []

    @cached_property
    def contents(self) -> list[dict[str, Any]]:
        """Return defined API properties for the current object.

        Response:
        {
            "keyword": "analyticsScore",
            "name": "Analytics Score",
            "type": "Integer",
            "description": "The intel score of the artifact",
            "groupable": false,
            "targetable": true
        }
        """
        _properties = []
        try:
            r = self.session.options(f'{self.api_url}/tql', params={})
            # print(r.request.method, r.request.url, r.text)
            if r.ok:
                _properties = r.json().get('data', [])
        except (ConnectionError, ProxyError) as ex:
            Render.panel.failure(f'Failed getting types properties ({ex}).')

        return _properties

    @property
    def contents_updated(self) -> Generator:
        """Update the properties contents, fixing issues in core data."""
        # Provided invalid type "BigInteger" on tql options call and correcting it to String
        for filter_data in self.contents:
            if self.object_type == 'indicators':
                title = 'Indicator Keyword Type'
                if filter_data['keyword'] == 'addressIpval' and filter_data['type'] != 'String':
                    self.messages.append(f'- [{self.object_type}] - ({title}) - fix required.')
                    filter_data['type'] = 'String'
                else:
                    self.messages.append(f'- [{self.object_type}] - ({title}) - fix NOT required.')

            if self.object_type == 'cases' and 'description' in filter_data:
                # fix misspelling in core data
                miss_map = {
                    'occured': 'occurred',
                    'Threatassess': 'ThreatAssess',
                }
                for c, w in miss_map.items():
                    if c in filter_data['description']:
                        filter_data['description'] = filter_data['description'].replace(c, w)

            yield filter_data

    @cached_property
    def content_models(self) -> Generator[FilterModel, None, None]:
        for field_data in self.contents_updated:
            try:
                yield FilterModel(**field_data)
            except ValidationError as ex:
                Render.panel.failure(f'Failed generating filter model: data={field_data} ({ex}).')
