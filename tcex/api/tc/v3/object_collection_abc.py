"""Case Management Collection Abstract Base Class"""
# standard library
import logging
from abc import ABC
from typing import TYPE_CHECKING, Optional, Union

# third-party
from requests import Response
from requests.exceptions import ProxyError, RetryError

# first-party
from tcex.api.tc.v3.tql.tql import Tql
from tcex.backports import cached_property
from tcex.exit.error_codes import handle_error
from tcex.utils import Utils

if TYPE_CHECKING:
    # third-party
    from pydantic import BaseModel

    # first-party
    from tcex.api.tc.v3.artifacts.artifact import Artifact
    from tcex.api.tc.v3.cases.case import Case
    from tcex.api.tc.v3.notes.note import Note
    from tcex.api.tc.v3.tags.tag import Tag
    from tcex.api.tc.v3.tasks.task import Task
    from tcex.api.tc.v3.workflow_events.workflow_event import WorkflowEvent

    # Case Management Types
    CaseManagementType = Union[
        Artifact,
        Case,
        Note,
        Tag,
        Task,
        WorkflowEvent,
    ]

# get tcex logger
logger = logging.getLogger('tcex')


class ObjectCollectionABC(ABC):
    """Case Management Collection Abstract Base Class

    This class is a base class for Case Management collections that use
    multi-inheritance with a pydantic BaseModel class. To ensure
    properties are not added to the model both @property and @setter
    methods are used.
    """

    def __init__(
        self,
        session,
        tql_filters: Optional[list] = None,  # This will be removed!
        params: Optional[dict] = None,
    ) -> None:
        """Initialize class properties."""
        self._params = params or {}
        self._tql_filters = tql_filters or []

        # properties
        self._session = session
        self.log = logger
        self.request = None
        self.tql = Tql()
        self._model = None
        self.type_ = None  # defined in child class
        self.utils = Utils()

    def __len__(self) -> int:
        """Return the length of the collection."""
        parameters = self._params.copy()
        parameters['resultLimit'] = 1
        parameters['count'] = True
        tql_string = self.tql.raw_tql
        if not self.tql.raw_tql:
            tql_string = self.tql.as_str
        if tql_string:
            parameters['tql'] = tql_string

        # convert all keys to camel case
        for k, v in list(parameters.items()):
            k = self.utils.snake_to_camel(k)
            # if result_limit and resultLimit both show up use the proper cased version
            if k not in parameters:
                parameters[k] = v

        self._request(
            'GET',
            self._api_endpoint,
            body=None,
            params=parameters,
            headers={'content-type': 'application/json'},
        )
        return self.request.json().get('count', len(self.request.json().get('data', [])))

    @property
    def _api_endpoint(self) -> None:  # pragma: no cover
        """Return filter method."""
        raise NotImplementedError('Child class must implement this method.')

    def _request(
        self,
        method: str,
        url: str,
        body: Optional[Union[bytes, str]] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> None:
        """Handle standard request with error checking."""
        try:
            self.request = self._session.request(
                method, url, data=body, headers=headers, params=params
            )
            self.log.debug(f'feature=api-tc-v3, request-body={self.request.request.body}')
        except (ConnectionError, ProxyError, RetryError):  # pragma: no cover
            handle_error(
                code=951,
                message_values=[
                    method.upper(),
                    None,
                    '{\"message\": \"Connection/Proxy Error/Retry\"}',
                    url,
                ],
            )

        if not self.success(self.request):
            err = self.request.text or self.request.reason
            handle_error(
                code=950,
                message_values=[
                    self.request.request.method.upper(),
                    self.request.status_code,
                    err,
                    self.request.url,
                ],
            )

        # log content for debugging
        self.log_response_text(self.request)

    @property
    def filter(self) -> None:  # pragma: no cover
        """Return filter method."""
        raise NotImplementedError('Child class must implement this method.')

    def log_response_text(self, response: Response) -> None:
        """Log the response text."""
        response_text = 'response text: (text to large to log)'
        if len(response.content) < 5000:  # check size of content for performance
            response_text = response.text
        self.log.debug(f'feature=api-tc-v3, response-body={response_text}')

    @property
    def model(self):
        """Return the model."""
        return self._model

    @model.setter
    def model(self, data):
        self._model = type(self.model)(**data)

    def iterate(
        self,
        base_class: 'BaseModel',
        api_endpoint: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> 'CaseManagementType':
        """Iterate over CM/TI objects."""
        url = api_endpoint or self._api_endpoint
        params = params or self.params

        # special parameter for indicators to enable the return the the indicator fields
        # (value1, value2, value3) on std-custom/custom-custom indicator types.
        if self.type_ == 'Indicators' and api_endpoint is None:
            params.setdefault('fields', []).append('genericCustomIndicatorValues')

        # convert all keys to camel case
        for k, v in list(params.items()):
            k = self.utils.snake_to_camel(k)
            params[k] = v

        tql_string = self.tql.raw_tql or self.tql.as_str

        if tql_string:
            params['tql'] = tql_string

        while True:
            self._request(
                'GET',
                body=None,
                url=url,
                headers={'content-type': 'application/json'},
                params=params,
            )

            # reset some vars
            params = {}

            response = self.request.json()
            data = response.get('data', [])
            url = response.pop('next', None)

            for result in data:
                yield base_class(session=self._session, **result)

            # break out of pagination if no next url present in results
            if not url:
                break

    # @staticmethod
    # def list_as_dict(added_items: 'CaseManagementType') -> dict:
    #     """Return the dict representation of the case management collection object."""
    #     as_dict = {'data': []}
    #     for item in added_items:
    #         as_dict['data'].append(item.as_dict)
    #     return as_dict

    @property
    def params(self) -> dict:
        """Return the parameters of the case management object collection."""
        return self._params

    @params.setter
    def params(self, params: dict) -> None:
        """Set the parameters of the case management object collection."""
        self._params = params

    @staticmethod
    def success(r: Response) -> bool:
        """Validate the response is valid.

        Args:
            r (requests.response): The response object.

        Returns:
            bool: True if status is "ok"
        """
        status = True
        if r.ok:
            try:
                if r.json().get('status') != 'Success':  # pragma: no cover
                    status = False
            except Exception:  # pragma: no cover
                status = False
        else:
            status = False
        return status

    @property
    def timeout(self) -> int:
        """Return the timeout of the case management object collection."""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: int) -> None:
        """Set the timeout of the case management object collection."""
        self._timeout = timeout

    @cached_property
    def tql_options(self):
        """Return TQL data keywords."""
        _data = []
        r = self._session.options(f'{self._api_endpoint}/tql', params={})
        if r.ok:
            _data = r.json()['data']
        return _data

    @property
    def tql_keywords(self):
        """Return supported TQL keywords."""
        return [to.get('keyword') for to in self.tql_options]
