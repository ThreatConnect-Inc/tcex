# -*- coding: utf-8 -*-


class CommonCaseManagementCollection(object):
    """
    Common Case Management Collection object that encapsalates common methods used by
     children classes.
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
    ):
        """
        Initialize CommonCaseManagementCollection Class
        """
        if tql_filters is None:
            tql_filters = []
        self.api_endpoint = api_endpoint
        self._next_url = next_url
        self._previous_url = previous_url
        self._page_size = page_size
        self._retry_count = retry_count
        self._timeout = timeout
        self._tcex = tcex
        self._initial_response = initial_response
        self._tql_filters = tql_filters

    def list_as_dict(self, added_items):
        """
        Returns the dict representation of the case management collection object.
        """
        as_dict = {'data': []}
        for item in added_items:
            as_dict['data'].append(item.as_dict)
        return as_dict

    @property
    def tcex(self):
        """
        Returns the tcex of the case management object collection.
        """
        return self._tcex

    @property
    def next_url(self):
        """
        Returns the next url of the case management object collection.
        """
        return self._next_url

    @next_url.setter
    def next_url(self, next_url):
        """
        Sets the next url of the case management object collection.
        """
        self._next_url = next_url

    @property
    def previous_url(self):
        """
        Returns the previous url of the case management object collection.
        """
        return self._previous_url

    @previous_url.setter
    def previous_url(self, previous_url):
        """
        Sets the previous url of the case management object collection.
        """
        self._previous_url = previous_url

    @property
    def page_size(self):
        """
        Returns the page size of the case management object collection.
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """
        Sets the page size of the case management object collection.
        """
        self._page_size = page_size

    @property
    def retry_count(self):
        """
        Returns the retry count of the case management object collection.
        """
        return self._retry_count

    @retry_count.setter
    def retry_count(self, retry_count):
        """
        Sets the retry count of the case management object collection.
        """
        self._retry_count = retry_count

    @property
    def timeout(self):
        """
        Returns the timeout of the case management object collection.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        """
        Sets the timeout of the case management object collection.
        """
        self._timeout = timeout

    @property
    def initial_response(self):
        """
        Returns the initial response of the case management object collection.
        """
        return self._initial_response

    def iterate(self, initial_response=None, added_entities=None):
        """
        iterates over the case management object collection objects.
        """
        if added_entities is None:
            added_entities = []

        url = self.api_endpoint
        if self.tql.raw_tql:
            tql_string = self.tql.raw_tql
        else:
            self.tql.filters = self._tql_filters + self.tql.filters
            tql_string = self.tql.as_str
        parameters = {'fields': [], 'tql': tql_string}
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
            url = r.json().pop('next_url', None)

            for result in data:
                yield self.entity_map(result)

            if not url:
                for entity in added_entities:
                    yield entity
                break

    # def json(self):
    #    generator with built in API call and pagination
    # def stix2(self):
    #    json to stix2
    # def openioc(self):
    #    json to stix2

    def entity_map(self, entity):
        """
        Overwritten by children methods
        """
        return None

    def __len__(self):
        """
        Returns the length of the collection.
        """
        count = 0
        for cm in self:
            count += 1
        return count

    @staticmethod
    def success(r):
        """
        Validates if the response is valid.
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
