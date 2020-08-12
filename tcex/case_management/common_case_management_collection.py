# -*- coding: utf-8 -*-
"""ThreatConnect Case Management Collection"""
# third-party
from requests.exceptions import ProxyError

from .tql import TQL


class CommonCaseManagementCollection:
    """Common Class for Case Management Collection

    Object encapsulates common methods used by child classes.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        # Example of params input
        {
            'result_limit': 100,  # How many results are retrieved.
            'result_start': 10,  # Starting point on retrieved results.
            'fields': ['caseId', 'summary']  # Additional fields returned on the results
        }

    Args:
        tcex ([type]): [description]
        api_endpoint ([type]): [description]
        tql_filters ([type], optional): [description]. Defaults to None.
        initial_response ([type], optional): [description]. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
                    retrieving the Case Management objects.

    Returns:
        [type]: [description]

    Yields:
        [type]: [description]
    """

    def __init__(
        self, tcex, api_endpoint, tql_filters=None, initial_response=None, params=None,
    ):
        """Initialize Class properties."""

        self._added_items = []
        self._initial_response = initial_response
        self._params = params or {}
        self._tql_data = None
        self._tql_filters = tql_filters or []
        self.api_endpoint = api_endpoint.value
        self.tcex = tcex
        self.tql = TQL()

    def __len__(self):
        """Return the length of the collection."""
        parameters = self.params
        parameters['result_limit'] = 1
        tql_string = self.tql.raw_tql
        if not self.tql.raw_tql:
            self.tql.filters = self._tql_filters + self.tql.filters
            tql_string = self.tql.as_str
        if tql_string:
            parameters['tql'] = tql_string

        # convert all keys to camel case
        for k, v in list(parameters.items()):
            del parameters[k]
            k = self.tcex.utils.snake_to_camel(k)
            parameters[k] = v

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
    def _filter_map_method(self):
        """Return a property for keywork mapping."""
        method_data = (
            f'\n{" " * 4}@property\n'
            f'\n{" " * 4}def keyword_map(self):\n'
            f'{" " * 8}"""Return keyword to method name map."""\n\n'
            f'{" " * 8}return {{\n'
        )
        for t in sorted(self.tql_data, key=lambda i: i['keyword']):
            method_data += f"""{" " * 12}'{t.get('keyword')}': '{t.get('keyword')}',\n"""
        method_data += f'{" " * 8}}}\n'

        return method_data

    @property
    def _filter_class(self):
        """Return a Filter Class current object."""
        filter_class = (
            f'\nclass Filter{self.__class__.__name__}(Filter):\n'
            f'{" " * 4}"""Filter Object for {self.__class__.__name__}"""\n'
        )

        for t in sorted(self.tql_data, key=lambda i: i['keyword']):
            class_name = self.tcex.utils.camel_to_space(self.__class__.__name__).title()
            description = t.get('description')
            keyword = t.get('keyword')
            keyword_snake = self.tcex.utils.camel_to_snake(keyword)

            # get the arg type
            keyword_type = 'str'
            tql_type = 'TQL.Type.STRING'
            if t.get('type') in ['Integer', 'Long']:
                keyword_type = 'int'
                tql_type = 'TQL.Type.INTEGER'
            elif t.get('type') == 'Boolean':
                keyword_type = 'bool'
                tql_type = 'TQL.Type.BOOLEAN'

            comment = ''
            if keyword_snake in ['id', 'type']:
                comment = '  # pylint: disable=redefined-builtin'

            if keyword_snake == 'has_artifact':
                filter_class += (
                    f'\n{" " * 4}@property\n'
                    f'{" " * 4}def has_artifact(self):\n'
                    f'{" " * 8}"""Return **FilterArtifacts** for further filtering."""\n'
                    f'{" " * 8}from .artifact import FilterArtifacts\n\n'
                    f'{" " * 8}artifacts = FilterArtifacts'
                    f'(ApiEndpoints.ARTIFACTS, self._tcex, TQL())\n'
                    f"""{" " * 8}self._tql.add_filter('hasArtifact', """
                    f'TQL.Operator.EQ, artifacts, TQL.Type.SUB_QUERY)\n'
                    f'{" " * 8}return artifacts\n'
                )
            elif keyword_snake == 'has_case':
                filter_class += (
                    f'\n{" " * 4}@property\n'
                    f'{" " * 4}def has_case(self):\n'
                    f'{" " * 8}"""Return **FilterCases** for further filtering."""\n'
                    f'{" " * 8}from .case import FilterCases  # pylint: disable=cyclic-import\n\n'
                    f'{" " * 8}cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())\n'
                    f"""{" " * 8}self._tql.add_filter('hasCase', """
                    f'TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)\n'
                    f'{" " * 8}return cases\n'
                )
            elif keyword_snake == 'has_note':
                filter_class += (
                    f'\n{" " * 4}@property\n'
                    f'{" " * 4}def has_note(self):\n'
                    f'{" " * 8}"""Return **FilterNotes** for further filtering."""\n'
                    f'{" " * 8}from .note import FilterNotes\n\n'
                    f'{" " * 8}notes = FilterNotes(ApiEndpoints.NOTES, self._tcex, TQL())\n'
                    f"""{" " * 8}self._tql.add_filter('hasNote', """
                    f'TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)\n'
                    f'{" " * 8}return notes\n'
                )
            elif keyword_snake == 'has_tag':
                filter_class += (
                    f'\n{" " * 4}@property\n'
                    f'{" " * 4}def has_tag(self):\n'
                    f'{" " * 8}"""Return **FilterTags** for further filtering."""\n'
                    f'{" " * 8}from .tag import FilterTags\n\n'
                    f'{" " * 8}tags = FilterTags(ApiEndpoints.TAGS, self._tcex, TQL())\n'
                    f"""{" " * 8}self._tql.add_filter('hasTag', """
                    f'TQL.Operator.EQ, tags, TQL.Type.SUB_QUERY)\n'
                    f'{" " * 8}return tags\n'
                )
            elif keyword_snake == 'has_task':
                filter_class += (
                    f'\n{" " * 4}@property\n'
                    f'{" " * 4}def has_task(self):\n'
                    f'{" " * 8}"""Return **FilterTask** for further filtering."""\n'
                    f'{" " * 8}from .task import FilterTasks\n'
                    f'{" " * 8}tasks = FilterTasks(ApiEndpoints.TASKS, self._tcex, TQL())\n'
                    f"""{" " * 8}self._tql.add_filter('hasTask', """
                    f'TQL.Operator.EQ, tasks, TQL.Type.SUB_QUERY)\n'
                    f'{" " * 8}return tasks\n'
                )
            else:
                # build method
                filter_class += (
                    f'\n{" " * 4}def {keyword_snake}(self, operator, {keyword_snake}):{comment}\n'
                    f'{" " * 8}"""Filter {class_name} based on **{keyword}** keyword.\n\n'
                    f'{" " * 8}Args:\n'
                    f'{" " * 12}operator (enum): The operator enum for the filter.\n'
                    f'{" " * 12}{keyword_snake} ({keyword_type}): {description}.\n'
                    f'{" " * 8}"""\n'
                    f"{' ' * 8}self._tql.add_filter('{keyword}', operator, "
                    f'{keyword_snake}, {tql_type})\n'
                )

        return filter_class

    @property
    def added_items(self):
        """Return the added items to the collection"""
        return self._added_items

    @added_items.setter
    def added_items(self, added_items):
        """Set the added items to the collection"""
        self._added_items = added_items

    def entity_map(self, entity):  # pragma: no cover
        """Stub for common method."""
        raise NotImplementedError('Child class must implement this method.')

    @property
    def filter(self):  # pragma: no cover
        """Return filter method."""
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

        # convert all keys to camel case
        for k, v in list(parameters.items()):
            del parameters[k]
            k = self.tcex.utils.snake_to_camel(k)
            parameters[k] = v

        url = self.api_endpoint

        tql_string = self.tql.raw_tql
        if not self.tql.raw_tql:
            self.tql.filters = self._tql_filters + self.tql.filters
            tql_string = self.tql.as_str

        if tql_string:
            parameters['tql'] = tql_string

        if initial_response:
            url = initial_response.get('next_url', None)
            entities = initial_response.get('data', [])
            for entity in entities:
                yield self.entity_map(entity)
            if not url:
                return

        while True:
            r = None
            try:
                r = self.tcex.session.get(url, params=parameters)
                self.tcex.log.debug(
                    f'Method: ({r.request.method.upper()}), '
                    f'Status Code: {r.status_code}, '
                    f'URl: ({r.url})'
                )
                self.tcex.log.trace(f'response: {r.text}')
            except (ConnectionError, ProxyError):  # pragma: no cover
                self.tcex.handle_error(
                    951, ['OPTIONS', 407, '{\"message\": \"Connection Error\"}', self.api_endpoint]
                )

            if not self.success(r):
                err = r.text or r.reason
                self.tcex.handle_error(950, [r.status_code, err, r.url])

            # reset some vars
            parameters = {}

            data = r.json().get('data', [])
            url = r.json().pop('next', None)

            for result in data:
                yield self.entity_map(result)

            if not url:
                yield from self.added_items
                break

    @staticmethod
    def list_as_dict(added_items):
        """Return the dict representation of the case management collection object."""
        as_dict = {'data': []}
        for item in added_items:
            as_dict['data'].append(item.as_dict)
        return as_dict

    @property
    def params(self):
        """Return the parameters of the case management object collection."""
        return self._params

    @params.setter
    def params(self, params):
        """Set the parameters of the case management object collection."""
        self._params = params

    @staticmethod
    def success(r):
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
    def timeout(self):
        """Return the timeout of the case management object collection."""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        """Set the timeout of the case management object collection."""
        self._timeout = timeout

    @property
    def tql_data(self):
        """Return TQL data keywords."""
        if self._tql_data is None:
            r = self.tcex.session.options(f'{self.api_endpoint}/tql', params={})
            if r.ok:
                self._tql_data = r.json()['data']

        return self._tql_data
