# -*- coding: utf-8 -*-
"""TcEx Framework Module for working with DataStore in the ThreatConnect Platform."""
# standard library
from typing import Optional

# third-party
from requests.models import Response


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
        tcex (TcEx): An instance of TcEx.
        domain (str): A value of “system”, “organization”, or “local”.
        data_type (str): A free form type name for the data.
        mapping (Optional[dict] = None): Defaults to None. Elasticsearch mappings data.
    """

    def __init__(self, tcex: object, domain: str, data_type: str, mapping: Optional[dict] = None):
        """Initialize class properties."""
        self.tcex: object = tcex
        self.domain: str = domain
        self.data_type: str = data_type
        self.mapping: Optional[dict] = mapping or {'dynamic': False}

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
            r: Response = self.tcex.session.post(url, json=index_settings, headers=headers)

            if not r.ok:
                error: str = r.text or r.reason
                self.tcex.handle_error(800, [r.status_code, error])
            self.tcex.log.debug(
                f'creating index. status_code: {r.status_code}, response: "{r.text}".'
            )
            # delete temporary record
            self.delete(rid, False)

    def _token_available(self):
        """Raise an error if token is not available.

        This check needs to be made after args are parsed to ensure token module has initialized.
        """
        # This module requires a token.
        if self.tcex.token.token is None:  # pragma: no cover
            raise RuntimeError(
                'The DataModel TcEx Module requires a Token to '
                'interact with the ThreatConnect platform.'
            )

    def _update_mappings(self):
        """Update the mappings for the current index."""
        headers = {'Content-Type': 'application/json', 'DB-Method': 'PUT'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/_mappings'
        r: Response = self.tcex.session.post(url, json=self.mapping, headers=headers)
        self.tcex.log.debug(f'update mapping. status_code: {r.status_code}, response: "{r.text}".')

    @property
    def index_exists(self) -> bool:
        """Check to see if index exists."""
        headers = {'Content-Type': 'application/json', 'DB-Method': 'GET'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/_search'
        r: Response = self.tcex.session.post(url, headers=headers)
        if not r.ok:
            self.tcex.log.warning(f'The provided index was not found ({r.text}).')
            return False
        return True

    def add(self, rid: str, data: dict, raise_on_error: Optional[bool] = True) -> dict:
        """Write data to the DataStore. Alias for post() method.

        Args:
            rid (str): The record identifier.
            data (dict): The record data.
            raise_on_error (Optional[bool] = True): If True and not r.ok this
                method will raise a RunTimeError.

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
            rid (str): The record identifier.
            raise_on_error (Optional[bool] = True): If True and not r.ok this
                method will raise a RunTimeError.

        Returns:
            dict : The response data.
        """
        self._token_available()  # ensure a token is available

        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'DELETE'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'
        r: Response = self.tcex.session.post(url, headers=headers)
        self.tcex.log.debug(f'datastore delete status code: {r.status_code}')
        if r.ok and 'application/json' in r.headers.get('content-type', ''):
            response_data: dict = r.json()
        else:
            error: str = r.text or r.reason
            self.tcex.handle_error(805, ['delete', r.status_code, error], raise_on_error)
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
            rid (Optional[str] = None): The record identifier.
            data (Optional[dict] = None): A search query
            raise_on_error (Optional[bool] = True): If True and not r.ok this
                method will raise a RunTimeError.

        Returns:
            dict : Python request response.
        """
        self._token_available()  # ensure a token is available

        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'GET'}
        if rid is None:
            url = f'/v2/exchange/db/{self.domain}/{self.data_type}/'
        else:
            url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'
        r: Response = self.tcex.session.post(url, json=data, headers=headers)
        self.tcex.log.debug(f'datastore get status code: {r.status_code}')
        if 'application/json' in r.headers.get('content-type', ''):
            # as long as the content is JSON set the value
            try:
                response_data: dict = r.json()
            except Exception as e:  # pragma: no cover
                # This issue should be addressed by core in a future release.
                self.tcex.log.warning(
                    'DataStore API returned a non-JSON response, even though '
                    f'content-type was application/json: {r.content} error: {e}'
                )
        if not r.ok:
            error: str = r.text or r.reason
            self.tcex.handle_error(805, ['get', r.status_code, error], raise_on_error)
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
            rid (str): The record identifier. If a value of None is passed an identifier elastic
                search will automatically generate a id.
            data (dict): The record data.
            raise_on_error (Optional[bool] = True): If True and not r.ok this
                method will raise a RunTimeError.

        Returns:
            dict : The response data.
        """
        self._token_available()  # ensure a token is available

        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'POST'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/'
        if rid is not None:
            url = f'{url}{rid}'

        r: Response = self.tcex.session.post(url, json=data, headers=headers)
        self.tcex.log.debug(f'datastore post status code: {r.status_code}')

        if r.ok and 'application/json' in r.headers.get('content-type', ''):
            response_data: dict = r.json()
        else:
            error: str = r.text or r.reason
            self.tcex.handle_error(805, ['post', r.status_code, error], raise_on_error)
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
            rid (str): The record identifier.
            data (dict): A search query
            raise_on_error (Optional[bool] = True): If True and not r.ok this
                method will raise a RunTimeError.

        Returns:
            dict : The response dict.
        """
        self._token_available()  # ensure a token is available

        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'PUT'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'

        r: Response = self.tcex.session.post(url, json=data, headers=headers)
        self.tcex.log.debug(f'datastore put status code: {r.status_code}')

        if r.ok and 'application/json' in r.headers.get('content-type', ''):
            response_data: dict = r.json()
        else:
            error: str = r.text or r.reason
            self.tcex.handle_error(805, ['put', r.status_code, error], raise_on_error)
        return response_data

    def update(self, rid: str, data: dict, raise_on_error: Optional[bool] = True):
        """Update the for the provided Id. Alias for put() method.

        Args:
            rid (str): The record identifier.
            data (dict): The record data.
            raise_on_error (Optional[bool] = True): If True and not r.ok this
                method will raise a RunTimeError.

        Returns:
            dict : The response data.
        """
        return self.put(rid, data, raise_on_error)
