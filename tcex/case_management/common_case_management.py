# -*- coding: utf-8 -*-
"""ThreatConnect Common Case Management"""
# third-party
from requests.exceptions import ProxyError

# first-party
from tcex.case_management.common_case_management_collection import CommonCaseManagementCollection


class CommonCaseManagement:
    """Common Class for Case Management.

    Args:
        tcex (TcEx): An instance of tcex.
        api_endpoint (str): The path to the API endpoint.
    """

    def __init__(self, tcex, api_endpoint, kwargs):
        """Initialize Class properties."""
        self.tcex = tcex
        self.api_endpoint = api_endpoint.value

        # properties
        self._fields = None
        self._id = kwargs.get('id', None)
        self._properties = None
        self._tql = None

        # process kwargs
        self._transform_kwargs(kwargs)

    def __str__(self):
        """Printable version of Object"""
        printable_string = ''
        for key, value in sorted(vars(self).items()):
            key = key.lstrip('_')
            if key in self._excluded_properties:
                continue

            # format key with trailing whitespace
            key = f'{key} '

            if isinstance(value, (int, str)) or value is None:
                printable_string += f'{key:.<40} {str(value):<50}\n'
            else:
                printable_string += f'{key:.<40} {"<object>":<50}\n'
        return printable_string

    def _camel_case_key(self, key):
        """Map key to it's appropriate Core/Test value."""
        if key in ['staged_artifact_type', 'stagedArtifactType']:  # pragma: no cover
            # used in testing when staging data
            return 'type'
        return self.tcex.utils.camel_to_snake(key)

    @property
    def _doc_string(self):
        """Return a doc string current object."""
        docstring = (
            f'\n{" " * 4}"""{self.__class__.__name__} object for Case Management.\n\n'
            f'{" " * 4}Args:\n'
            f'{" " * 8}tcex (TcEx): An instantiated instance of TcEx object.\n'
        )
        for p, pd in sorted(self.properties.items()):
            # get data array if exists
            data = pd.get('data')

            # get read-only value for display and required value
            read_only = pd.get('read-only', False)
            if read_only is None and data:
                read_only = data[0].get('read-only', False)

            # get required value or default
            required = pd.get('required', False)
            # if read_only is True:
            #     required = False

            # get type
            type_flag = ''  # used to append the word flag for bool types
            type_ = pd.get('type')
            if type_ is None and data:
                type_ = data[0].get('type')

            if type_ == 'Array':
                type_ = 'list'
            elif type_ == 'Boolean':
                type_ = 'bool'
                type_flag = ' flag'
            elif type_ == 'Date':
                type_ = 'str'
            elif type_ == 'Integer':
                type_ = 'int'
            elif type_ == 'JsonNode':
                type_ = 'dict'
            elif type_ == 'Long':
                type_ = 'int'
            elif type_ == 'String':
                type_ = 'str'

            # set description
            description = (
                f'The **{self.tcex.utils.camel_to_space(p).title()}**{type_flag} for the '
                f'{self.tcex.utils.camel_to_space(self.__class__.__name__).title()}.'
            )
            if pd.get('description'):
                description = pd.get('description')
            elif data:
                if data[0].get('description'):
                    description = data[0].get('description', '')

            # build meta with required and read-only values
            meta = []
            if required:
                required_text = 'Required'
                if pd.get('required-alt-field'):
                    required_text += f" (alt: {pd.get('required-alt-field')})"
                meta.append(required_text)
            if read_only:
                meta.append('Read-Only')
            if meta:
                meta = f" [{','.join(meta)}]"
            else:
                meta = ''

            # build docstring
            docstring += (
                f'{" " * 8}{self.tcex.utils.camel_to_snake(p)} ({type_}, kwargs):'
                f'{meta} {description}\n'
            )

        docstring += f'{" " * 4}"""\n'
        return docstring

    @property
    def _excluded_properties(self):
        """Return a list of properties to exclude when creating a dict of the children class."""
        return [
            'api_endpoint',
            'artifact_filter',
            'case_filter',
            'filter',
            'fields',
            'kwargs',
            'put_properties',
            'post_properties',
            'properties',
            'task_filter',
            'tcex',
            'tql',
            'workflow_event_filter',
        ]

    def _reverse_transform(self, kwargs):
        """Reverse mapping of the _metadata_map method."""

        def reverse_transform(current_kwargs):
            reversed_mappings = {}
            for key, value in current_kwargs.items():
                if isinstance(value, dict):
                    value = reverse_transform(value)
                elif isinstance(value, list):
                    values = []
                    for entry in value:
                        values.append(self._reverse_transform(entry))
                    reversed_mappings[key] = values
                    return reversed_mappings
                new_key = self.tcex.utils.snake_to_camel(key)
                reversed_mappings[new_key] = value
            return reversed_mappings

        return reverse_transform(kwargs)

    def _transform_kwargs(self, kwargs):
        """Map the provided kwargs to expected arguments."""
        for key in dict(kwargs):
            kwargs[self._camel_case_key(key)] = kwargs.pop(key)

    @property
    def as_entity(self):  # pragma: no cover
        """Return the object as an entity."""
        raise NotImplementedError('Child class must implement this method.')

    @property
    def as_dict(self):
        """Return the dict representation of the CM object."""
        properties = vars(self)
        as_dict = {}
        for key, value in properties.items():
            key = key.lstrip('_')
            if key in self._excluded_properties:
                continue
            if hasattr(self, key):
                value = getattr(self, key)
            try:
                value = value.as_dict
            except AttributeError:
                if isinstance(value, CommonCaseManagementCollection):
                    for added_item in value.added_items:
                        if key not in as_dict:
                            as_dict[key] = {'data': []}
                        as_dict[key]['data'].append(added_item.as_dict)
                    continue

            if value is None:
                continue
            if isinstance(value, dict) and 'data' in value and not value.get('data'):
                continue
            as_dict[key] = value

        # don't return empty dicts
        if not as_dict:
            return None

        return as_dict

    @property
    def body(self):
        """Return the body representation of the CM object."""
        properties = vars(self)
        built_body = {}
        for key, value in properties.items():
            key = key.lstrip('_')
            if key in self._excluded_properties:
                continue
            # If creating a PUT body and key is not a PUT property do not include it in body.
            if self.id and key not in map(self._camel_case_key, self.put_properties):
                continue
            # If creating a POST body and key is not a POST property do not include it in body.
            if key not in map(self._camel_case_key, self.post_properties):
                continue
            if hasattr(self, key):
                value = getattr(self, key)
            try:
                value = value.body
            except AttributeError:
                if isinstance(value, CommonCaseManagementCollection):
                    for added_item in value.added_items:
                        if key not in built_body:
                            built_body[key] = {'data': []}
                        built_body[key]['data'].append(added_item.body)
                    continue

            if value is None:
                continue
            if isinstance(value, dict) and 'data' in value and not value.get('data'):
                continue
            built_body[key] = value

        # don't return empty dicts
        if not built_body:
            return None

        return self._reverse_transform(built_body)

    @property
    def available_fields(self):
        """Return the available query param field names for this object."""
        return [fd.get('name') for fd in self.fields]

    @property
    def fields(self):
        """Return the field data for this object."""
        if self._fields is None:
            r = self.tcex.session.options(f'{self.api_endpoint}/fields', params={})
            if r.ok:
                self._fields = r.json()['data']
        return self._fields

    def delete(self):
        """Delete the Case Management Object.

        If no id is present in the obj then returns immediately.
        """
        if not self.id:  # pragma: no cover
            self.tcex.log.warning('A case without an ID cannot be deleted.')
            return

        url = f'{self.api_endpoint}/{self.id}'
        r = None
        try:
            r = self.tcex.session.delete(url)
            self.tcex.log.debug(
                f'Method: ({r.request.method.upper()}), '
                f'Status Code: {r.status_code}, '
                f'URl: ({r.url})'
            )
        except (ConnectionError, ProxyError):  # pragma: no cover
            self.tcex.handle_error(
                951, ['OPTIONS', 407, '{\"message\": \"Connection Error\"}', self.api_endpoint]
            )
        if len(r.content) < 5000:
            self.tcex.log.debug(u'response text: {}'.format(r.text))
        else:  # pragma: no cover
            self.tcex.log.debug(u'response text: (text to large to log)')
        if not self.success(r):
            err = r.text or r.reason
            if r.status_code == 404:
                self.tcex.handle_error(952, [r.request.method.upper(), r.status_code, err, r.url])
            self.tcex.handle_error(950, [r.status_code, err, r.url])
        return

    def entity_mapper(self, entity):  # pragma: no cover
        """Stub for entity mapper"""
        raise NotImplementedError('Child class must implement this method.')

    def get(self, all_available_fields=False, case_management_id=None, params=None):
        """Get the Case Management Object.

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
            all_available_fields (bool): If True all available fields will be returned.
            case_management_id (int): The id of the case management object to be returned.
            retry_count (int, optional): [description]. Defaults to 0.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Artifacts objects.

        Returns:
            Object: A artifact, case, note, task, tag, or workflow object.
        """
        if params is None:
            params = {}

        # convert all keys to camel case
        for k, v in list(params.items()):
            del params[k]
            k = self.tcex.utils.snake_to_camel(k)
            params[k] = v

        cm_id = case_management_id or self.id
        url = f'{self.api_endpoint}/{cm_id}'

        # add fields parameter if provided
        if all_available_fields:
            params['fields'] = []
            for field in self.available_fields:
                params['fields'].append(field)

        if not cm_id:  # pragma: no cover
            message = '{"message": "No ID provided.", "status": "Error"}'
            self.tcex.handle_error(952, ['GET', '404', message, url])

        r = None
        try:
            r = self.tcex.session.get(url, params=params)
        except (ConnectionError, ProxyError):  # pragma: no cover
            self.tcex.handle_error(
                951, ['OPTIONS', 407, '{\"message\": \"Connection Error\"}', self.api_endpoint]
            )
        self.tcex.log.debug(
            f'Method: ({r.request.method.upper()}), '
            f'Status Code: {r.status_code}, '
            f'URl: ({r.url})'
        )
        if len(r.content) < 5000:
            self.tcex.log.debug(u'response text: {}'.format(r.text))
        else:  # pragma: no cover
            self.tcex.log.debug(u'response text: (text to large to log)')
        if not self.success(r):
            err = r.text or r.reason
            if r.status_code == 404:
                self.tcex.handle_error(952, ['GET', r.status_code, err, r.url])
            self.tcex.handle_error(951, ['GET', r.status_code, err, r.url])
        self.entity_mapper(r.json().get('data', {}))
        return r

    @property
    def id(self):
        """Return the id of the case management object."""
        return self._id

    @id.setter
    def id(self, cm_id):
        """Set the id of the case management object."""
        self._id = cm_id

    @property
    def implemented_properties(self):
        """Return implemented Object properties."""
        properties = []
        for key in vars(self):
            key = key.lstrip('_')
            if key in self._excluded_properties:
                continue

            properties.append(key)

        return properties

    @property
    def put_properties(self):
        """Return all the properties available in PUT requests."""
        put_properties = []
        for p, pd in sorted(self.properties.items()):
            # get read-only value for display and required value
            updatable = pd.get('updatable', True)
            read_only = pd.get('read-only', False)
            if not read_only:
                if updatable:
                    put_properties.append(p)

        return put_properties

    @property
    def post_properties(self):
        """Return all the properties available in POST requests."""
        post_properties = []
        for p, pd in sorted(self.properties.items()):
            read_only = pd.get('read-only', False)
            if not read_only:
                post_properties.append(p)

        return post_properties

    @property
    def properties(self):
        """Return defined API properties for the current object."""
        if self._properties is None:
            try:
                r = self.tcex.session.options(self.api_endpoint, params={'show': 'readOnly'})
                if r.ok:
                    self._properties = r.json()
            except (ConnectionError, ProxyError):
                self.tcex.handle_error(
                    951, ['OPTIONS', 407, '{\"message\": \"Connection Error\"}', self.api_endpoint]
                )
        return self._properties

    @property
    def required_properties(self):
        """Return a list of required fields for current object."""
        rp = []
        for p, pd in self.properties.items():
            if pd.get('required'):
                rp.append(p)
        return rp

    def submit(self):
        """Create or Update the Case Management object.

        This is determined based on if the id is already present in the object.
        """
        body = self.body or {}

        method = 'POST'
        url = self.api_endpoint
        if self.id:
            # if the ID is included, its an update
            method = 'PUT'
            url = f'{self.api_endpoint}/{self.id}'

        # make the request
        r = self.tcex.session.request(method, url, json=body)

        self.tcex.log.debug(
            f'Method: ({r.request.method.upper()}), '
            f'Status Code: {r.status_code}, '
            f'URl: ({r.url})'
        )
        self.tcex.log.debug(f'body: {body}')
        if len(r.content) < 5000:
            self.tcex.log.debug(u'response text: {}'.format(r.text))
        else:  # pragma: no cover
            self.tcex.log.debug(u'response text: (text to large to log)')

        if not self.success(r):  # pragma: no cover
            err = r.text or r.reason
            if r.status_code == 404:
                self.tcex.handle_error(952, [r.request.method.upper(), r.status_code, err, r.url])
            self.tcex.handle_error(951, [r.request.method, r.status_code, err, r.url])

        r_json = r.json()
        if not self.id:
            self.id = r_json.get('data', {}).get('id')
        body['id'] = self.id
        self.entity_mapper(r_json.get('data', r_json))

        return r

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
