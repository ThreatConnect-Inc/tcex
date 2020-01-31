# -*- coding: utf-8 -*-
"""TcEx Framework Module for working with DataStore in the ThreatConnect Platform."""


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

    """

    def __init__(self, tcex, domain, data_type, mapping=None):
        """Initialize class properties.

        Args:
            tcex ([type]): [description]
            domain (str): A value of “system”, “organization”, or “local”.
            data_type (str): A free form type name for the data.
            mapping (dict, optional): Defaults to None. Elasticsearch mappings data.

        Raises:
            RuntimeError: [description]
        """
        self.tcex = tcex
        self.domain = domain
        self.data_type = data_type
        self.mapping = mapping or {'dynamic': False}

        # properties
        self._create_index()  # create the initial index.
        self._update_mappings()  # update mappings

    def _create_index(self):
        """Create index if it doesn't exist."""
        if not self.index_exists:
            rid = 'temp-index-create'
            index_settings = {}
            headers = {'Content-Type': 'application/json', 'DB-Method': 'POST'}
            url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'
            r = self.tcex.session.post(url, json=index_settings, headers=headers)

            if not r.ok:
                error = r.text or r.reason
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
                'The DataModel TcEx Module requires a Token to interact with the '
                'ThreatConnect platform.'
            )

    def _update_mappings(self):
        """Update the mappings for the current index."""
        headers = {'Content-Type': 'application/json', 'DB-Method': 'PUT'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/_mappings'
        r = self.tcex.session.post(url, json=self.mapping, headers=headers)
        self.tcex.log.debug(f'update mapping. status_code: {r.status_code}, response: "{r.text}".')

    @property
    def index_exists(self):
        """Check to see if index exists."""
        headers = {'Content-Type': 'application/json', 'DB-Method': 'GET'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/_search'
        r = self.tcex.session.post(url, headers=headers)
        if not r.ok:
            self.tcex.log.warning(f'The provided index was not found ({r.text}).')
            return False
        return True

    def add(self, rid, data, raise_on_error=True):
        """Write data to the DataStore. Alias for post() method.

        Args:
            rid (str): The record identifier.
            data (dict): The record data.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        return self.post(rid, data, raise_on_error)

    def delete(self, rid, raise_on_error=True):
        """Delete a record from the index using provide Id.

        Args:
            rid (str): The record identifier.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        self._token_available()  # ensure a token is available

        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'DELETE'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'
        r = self.tcex.session.post(url, headers=headers)
        self.tcex.log.debug(f'datastore delete status code: {r.status_code}')
        if r.ok and 'application/json' in r.headers.get('content-type', ''):
            response_data = r.json()
        else:
            error = r.text or r.reason
            self.tcex.handle_error(805, ['delete', r.status_code, error], raise_on_error)
        return response_data

    def get(self, rid=None, data=None, raise_on_error=True):
        """Get data from the DataStore.

        Args:
            rid (str, Optional): Defaults to None. The record identifier.
            data (dict, Optional): Defaults to None. A search query
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        self._token_available()  # ensure a token is available

        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'GET'}
        if rid is None:
            url = f'/v2/exchange/db/{self.domain}/{self.data_type}/'
        else:
            url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'
        r = self.tcex.session.post(url, json=data, headers=headers)
        self.tcex.log.debug(f'datastore get status code: {r.status_code}')
        if 'application/json' in r.headers.get('content-type', ''):
            # as long as the content is JSON set the value
            try:
                response_data = r.json()
            # TODO this issue should be addressed by core.  This is a temporary solution
            except Exception as e:
                self.tcex.log.warning(
                    f'DataStore API returned a non-JSON response, even though content-type was \
                        application/json: {r.content} \
                        error: {e}'
                )
        if not r.ok:
            error = r.text or r.reason
            self.tcex.handle_error(805, ['get', r.status_code, error], raise_on_error)
        return response_data

    def post(self, rid, data, raise_on_error=True):
        """Write data to the DataStore.

        Args:
            rid (str): The record identifier. If a value of None is passed an identifier elastic
                search will automatically generate a id.
            data (dict): The record data.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        self._token_available()  # ensure a token is available

        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'POST'}
        if rid is None:
            url = f'/v2/exchange/db/{self.domain}/{self.data_type}/'
        else:
            url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'
        r = self.tcex.session.post(url, json=data, headers=headers)
        self.tcex.log.debug(f'datastore post status code: {r.status_code}')
        if r.ok and 'application/json' in r.headers.get('content-type', ''):
            response_data = r.json()
        else:
            error = r.text or r.reason
            self.tcex.handle_error(805, ['post', r.status_code, error], raise_on_error)
        return response_data

    def put(self, rid, data, raise_on_error=True):
        """Update the data for the provided Id.

        Args:
            rid (str): The record identifier.
            data (dict): A search query
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        self._token_available()  # ensure a token is available

        response_data = None
        headers = {'Content-Type': 'application/json', 'DB-Method': 'PUT'}
        url = f'/v2/exchange/db/{self.domain}/{self.data_type}/{rid}'
        r = self.tcex.session.post(url, json=data, headers=headers)
        self.tcex.log.debug(f'datastore put status code: {r.status_code}')
        if r.ok and 'application/json' in r.headers.get('content-type', ''):
            response_data = r.json()
        else:
            error = r.text or r.reason
            self.tcex.handle_error(805, ['put', r.status_code, error], raise_on_error)
        return response_data

    def update(self, rid, data, raise_on_error=True):
        """Update the for the provided Id. Alias for put() method.

        Args:
            rid (str): The record identifier.
            data (dict): The record data.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        return self.put(rid, data, raise_on_error)
