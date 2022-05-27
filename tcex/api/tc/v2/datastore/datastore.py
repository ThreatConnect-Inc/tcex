"""TcEx Framework Module for working with DataStore in the ThreatConnect Platform."""
# standard library
import logging
from typing import TYPE_CHECKING, Optional

# first-party
from tcex.exit.error_codes import handle_error

if TYPE_CHECKING:
    # third-party
    from requests import Response, Session

# get tcex logger
logger = logging.getLogger('tcex')


class DataStore:
    """TcEx DataStore Class.

    **domain**

    This can be either “system”, “organization”, or “local”. Any string not defined as these
    3 will return a “Resource Not Found” error response.

    **dataType**

    This is a free form index type name as allowed by ElasticSearch. The ThreatConnect API will
    use this resource verbatim for ElasticSearch calls.

    **searchCommand**

    The URI string after the typeName is assumed to be ElasticSearch relevant information and is
    passed directly to ElasticSearch.

    Args:
        session_tc: A requests.Session instance with auth configured for the ThreatConnect API.
        domain: A value of “system”, “organization”, or “local”.
        data_type: A free form type name for the data.
        mapping: Elasticsearch mappings data.
    """

    def __init__(
        self, session_tc: 'Session', domain: str, data_type: str, mapping: Optional[dict] = None
    ):
        """Initialize class properties."""
        self.domain = domain
        self.data_type = data_type
        self.mapping = mapping or {'dynamic': False}
        self.session_tc = session_tc

        # properties
        self.log = logger

        # setup
        self._create_index()  # create the initial index.
        self._update_mappings()  # update mappings

    def _create_index(self):
        """Create index if it doesn't exist."""
        if not self.index_exists:
            rid = 'temp-index-create'
            index_settings = {}
            headers = {'Content-Type': 'application/json', 'DB-Method': 'POST'}
            url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'
            r: 'Response' = self.session_tc.post(url, json=index_settings, headers=headers)

            if not r.ok:
                error: str = r.text or r.reason
                handle_error(code=800, message_values=[r.status_code, error])
            self.log.debug(f'creating index. status_code: {r.status_code}, response: "{r.text}".')
            # delete temporary record
            self.delete(rid, False)

    def _update_mappings(self):
        """Update the mappings for the current index."""
        headers = {'Content-Type': 'application/json', 'DB-Method': 'PUT'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/_mappings'
        r: 'Response' = self.session_tc.post(url, json=self.mapping, headers=headers)
        self.log.debug(f'update mapping. status_code: {r.status_code}, response: "{r.text}".')

    @property
    def index_exists(self) -> bool:
        """Check to see if index exists."""
        headers = {'Content-Type': 'application/json', 'DB-Method': 'GET'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/_search'
        r: 'Response' = self.session_tc.post(url, headers=headers)
        if not r.ok:
            self.log.warning(f'The provided index was not found ({r.text}).')
            return False
        return True

    def add(self, rid: str, data: dict, raise_on_error: Optional[bool] = True) -> dict:
        """Write data to the DataStore. Alias for post() method.

        Args:
            rid: The record identifier.
            data: The record data.
            raise_on_error: If True and not r.ok this method will raise a RunTimeError.

        Returns:
            dict : The response data.
        """
        return self.post(rid, data, raise_on_error)

    def delete(self, rid: str, raise_on_error: Optional[bool] = True) -> dict:
        """Delete a record from the index using provide Id.

        **Example Response**

        .. code-block:: json

            {
              "_index": "$local.usr5_pytest",
              "_type": "pytest",
              "_id": "three",
              "_version": 4,
              "result": "deleted",
              "_shards": {
                "total": 2,
                "successful": 1,
                "failed": 0
              },
              "_seq_no": 45,
              "_primary_term": 1
            }

        Args:
            rid: The record identifier.
            raise_on_error: If True and not r.ok this method will raise a RunTimeError.

        Returns:
            dict : The response data.
        """
        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'DELETE'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'
        r: 'Response' = self.session_tc.post(url, headers=headers)
        self.log.debug(f'datastore delete status code: {r.status_code}')
        if r.ok and 'application/json' in r.headers.get('content-type', ''):
            response_data: dict = r.json()
        else:
            error: str = r.text or r.reason
            handle_error(
                code=805,
                message_values=['delete', r.status_code, error],
                raise_error=raise_on_error,
            )
        return response_data

    def get(
        self,
        rid: Optional[str] = None,
        data: Optional[dict] = None,
        raise_on_error: Optional[bool] = True,
    ) -> dict:
        """Get data from the DataStore.

        **Example Response**

        .. code-block:: json

            {
              "_index": "$local.usr5_pytest",
              "_type": "pytest",
              "_id": "two",
              "_version": 1,
              "found": true,
              "_source": {
                "two": 2
              }
            }

        Args:
            rid: The record identifier.
            data: The search query.
            raise_on_error: If True and not r.ok this method will raise a RunTimeError.

        Returns:
            dict : Python request response.
        """
        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'GET'}
        if rid is None:
            url = f'/v2/exchange/db/{self.domain}/{self.data_type}/'
        else:
            url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'
        r: 'Response' = self.session_tc.post(url, json=data, headers=headers)
        self.log.debug(f'datastore get status code: {r.status_code}')
        if 'application/json' in r.headers.get('content-type', ''):
            # as long as the content is JSON set the value
            try:
                response_data: dict = r.json()
            except Exception as e:  # pragma: no cover
                # This issue should be addressed by core in a future release.
                self.log.warning(
                    'DataStore API returned a non-JSON response, even though '
                    f'content-type was application/json: {r.content} error: {e}'
                )
        if not r.ok:
            error: str = r.text or r.reason
            handle_error(
                code=805,
                message_values=['get', r.status_code, error],
                raise_error=raise_on_error,
            )
        return response_data

    def post(self, rid: str, data: str, raise_on_error: Optional[bool] = True) -> dict:
        """Write data to the DataStore.

        **Example Response**

        .. code-block:: json

            {
              "_index": "$local.usr5_pytest",
              "_type": "pytest",
              "_id": "one",
              "_version": 31,
              "result": "updated",
              "_shards": {
                "total": 2,
                "successful": 1,
                "failed": 0
              },
              "_seq_no": 53,
              "_primary_term": 1
            }

        Args:
            rid: The record identifier. If a value of None is passed an identifier elastic
                search will automatically generate a id.
            data: The record data.
            raise_on_error: If True and not r.ok this method will raise a RunTimeError.

        Returns:
            dict : The response data.
        """
        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'POST'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/'
        if rid is not None:
            url = f'{url}{rid}'

        r: 'Response' = self.session_tc.post(url, json=data, headers=headers)
        self.log.debug(f'datastore post status code: {r.status_code}')

        if r.ok and 'application/json' in r.headers.get('content-type', ''):
            response_data: dict = r.json()
        else:
            error: str = r.text or r.reason
            handle_error(
                code=805,
                message_values=['post', r.status_code, error],
                raise_error=raise_on_error,
            )
        return response_data

    def put(self, rid: str, data: dict, raise_on_error: Optional[bool] = True) -> dict:
        """Update the data for the provided Id.

        **Example Response**

        .. code-block:: json

            {
              "_index": "$local.usr5_pytest",
              "_type": "pytest",
              "_id": "one",
              "_version": 33,
              "result": "updated",
              "_shards": {
                "total": 2,
                "successful": 1,
                "failed": 0
              },
              "_seq_no": 55,
              "_primary_term": 1
            }

        Args:
            rid: The record identifier.
            data: A search query
            raise_on_error: If True and not r.ok this method will raise a RunTimeError.

        Returns:
            dict : The response dict.
        """
        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'PUT'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'

        r: 'Response' = self.session_tc.post(url, json=data, headers=headers)
        self.log.debug(f'datastore put status code: {r.status_code}')

        if r.ok and 'application/json' in r.headers.get('content-type', ''):
            response_data: dict = r.json()
        else:
            error: str = r.text or r.reason
            handle_error(
                code=805,
                message_values=['put', r.status_code, error],
                raise_error=raise_on_error,
            )
        return response_data

    def update(self, rid: str, data: dict, raise_on_error: Optional[bool] = True) -> dict:
        """Update the for the provided Id. Alias for put() method.

        Args:
            rid: The record identifier.
            data: The record data.
            raise_on_error: If True and not r.ok this method will raise a RunTimeError.

        Returns:
            dict : The response data.
        """
        return self.put(rid, data, raise_on_error)
