# -*- coding: utf-8 -*-
"""ThreatConnect Case Management Collection"""
from .tql import TQL


class CommonCaseManagementCollection:
    """Common Class for Case Management Collection

    Object encapsulates common methods used by child classes.

    params example: {
        'result_limit': 100, # How many results are retrieved.
        'result_start': 10,  # Starting point on retrieved results.
        'fields': ['caseId', 'summary'] # Additional fields returned on the results
    }

    Args:
        tcex ([type]): [description]
        api_endpoint ([type]): [description]
        tql_filters ([type], optional): [description]. Defaults to None.
        page_size (int, optional): [description]. Defaults to 1000.
        next_url ([type], optional): [description]. Defaults to None.
        previous_url ([type], optional): [description]. Defaults to None.
        retry_count (int, optional): [description]. Defaults to 5.
        timeout (int, optional): [description]. Defaults to 1000.
        initial_response ([type], optional): [description]. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
                    retrieving the Case Management objects.

    Returns:
        [type]: [description]

    Yields:
        [type]: [description]
    """

    def __init__(
        self,
        tcex,
        api_endpoint,
        tql_filters=None,
        page_size=1000,
        next_url=None,
        previous_url=None,
        retry_count=5,
        timeout=1000,
        initial_response=None,
        params=None,
    ):
        """Initialize Class properties."""

        self._params = params
        if params is None:
            self.params = {}
        if tql_filters is None:
            tql_filters = []
        self._added_items = []
        self._initial_response = initial_response
        self._next_url = next_url
        self._previous_url = previous_url
        self._page_size = page_size
        self._retry_count = retry_count
        self._timeout = timeout
        self._tql_filters = tql_filters
        self.api_endpoint = api_endpoint.value
        self.tcex = tcex
        self.tql = TQL()

    def __len__(self):
        """Return the length of the collection."""
        parameters = {'resultLimit': 1}
        r = self.tcex.session.get(self.api_endpoint, params=parameters)
        return r.json().get('count')

    def __str__(self):
        """Object iterator"""
        printable_string = ''
        for obj in self.iterate(initial_response=self.initial_response):
            printable_string += f'{"-" * 50}\n'
            printable_string += str(obj)
        return printable_string

    @property
    def added_items(self):
        """Return the added items to the collection"""
        return self._added_items

    @added_items.setter
    def added_items(self, added_items):
        """Set the added items to the collection"""
        self._added_items = added_items

    def entity_map(self, entity):
        """Stub for common method."""
        raise NotImplementedError('Child class must implement this method.')

    @property
    def initial_response(self):
        """Return the initial response of the case management object collection."""
        return self._initial_response

    def iterate(self, initial_response=None):
        """Iterate over the case management object collection objects.

        Args:
            initial_response ([type], optional): [description]. Defaults to None.

        Yields:
            [type]: [description]
        """
        parameters = self.params
        self.to_camel_case(parameters)
        url = self.api_endpoint

        tql_string = self.tql.raw_tql
        if not self.tql.raw_tql:
            tql_string = self.tql.as_str
            self.tql.filters = self._tql_filters + self.tql.filters

        if tql_string:
            parameters['tql'] = tql_string

        current_retries = 0
        if initial_response:
            url = initial_response.get('next_url', None)
            entities = initial_response.get('data', [])
            for entity in entities:
                yield self.entity_map(entity)
            if not url:
                return

        while True:
            r = self.tcex.session.get(url, params=parameters)
            self.tcex.log.debug(
                f'Method: ({r.request.method.upper()}), '
                f'Status Code: {r.status_code}, '
                f'URl: ({r.url})'
            )
            self.tcex.log.trace(f'response: {r.text}')

            if not self.success(r):
                current_retries += 1
                if current_retries > self.retry_count:
                    err = r.text or r.reason
                    self.tcex.handle_error(950, [r.status_code, err, r.url])
                else:
                    continue

            # reset some vars
            parameters = {}
            current_retries = 0

            data = r.json().get('data', [])
            url = r.json().pop('next', None)

            for result in data:
                yield self.entity_map(result)

            if not url:
                yield from self.added_items
                break

    # def json(self):
    #    generator with built in API call and pagination

    @staticmethod
    def list_as_dict(added_items):
        """Return the dict representation of the case management collection object."""
        as_dict = {'data': []}
        for item in added_items:
            as_dict['data'].append(item.as_dict)
        return as_dict

    @property
    def next_url(self):
        """Return the next url of the case management object collection."""
        return self._next_url

    @next_url.setter
    def next_url(self, next_url):
        """Set the next url of the case management object collection."""
        self._next_url = next_url

    # def openioc(self):
    #    json to stix2

    @property
    def params(self):
        """Return the parameters of the case management object collection."""
        return self._params

    @params.setter
    def params(self, params):
        """Set the parameters of the case management object collection."""
        self._params = params

    @property
    def page_size(self):
        """Return the page size of the case management object collection."""
        return self._page_size

    @property
    def previous_url(self):
        """Return the previous url of the case management object collection."""
        return self._previous_url

    @previous_url.setter
    def previous_url(self, previous_url):
        """Set the previous url of the case management object collection."""
        self._previous_url = previous_url

    @page_size.setter
    def page_size(self, page_size):
        """Set the page size of the case management object collection."""
        self._page_size = page_size

    @property
    def retry_count(self):
        """Return the retry count of the case management object collection."""
        return self._retry_count

    @retry_count.setter
    def retry_count(self, retry_count):
        """Set the retry count of the case management object collection."""
        self._retry_count = retry_count

    # def stix2(self):
    #    json to stix2

    @staticmethod
    def success(r):
        """Validates if the response is valid.

        Args:
            r ([type]): [description]

        Returns:
            [type]: [description]
        """
        status = True
        if r.ok:
            try:
                if r.json().get('status') != 'Success':
                    status = False
            except Exception:
                status = False
        else:
            status = False
        return status

    @property
    def timeout(self):
        """Return the timeout of the case management object collection."""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        """Set the timeout of the case management object collection."""
        self._timeout = timeout

    @staticmethod
    def to_camel_case(kwargs):
        """
        Converts snake_case to camelCase

        Args:
            kwargs (dict): The dictionary you wish to convert keys to camel case.
        """
        for key in dict(kwargs):
            if not key:
                continue
            components = key.split('_')
            new_key = components[0] + ''.join(x.title() for x in components[1:])
            kwargs[new_key] = kwargs.pop(key)
