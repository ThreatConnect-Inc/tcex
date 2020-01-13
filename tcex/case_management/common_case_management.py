# -*- coding: utf-8 -*-
"""ThreatConnect Common Case Management"""
from tcex.case_management.common_case_management_collection import CommonCaseManagementCollection


class CommonCaseManagement:
    """Common Class for Case Management.

    Args:
        tcex ([type]): [description]
        api_endpoint ([type]): [description]
        kwargs ([type]): [description]
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

            if value is None:
                printable_string += f'{key:.<40} {"null":<50}\n'
            elif isinstance(value, (int, str)):
                printable_string += f'{key:.<40} {value:<50}\n'
            else:
                printable_string += f'{key:.<40} {"<object>":<50}\n'
        return printable_string

    def _camel_case_key(self, key):
        """Map key to it's appropriate Core/Test value."""
        if key in ['artifact_type', 'artifactType']:
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
            'case_filter',
            'filter',
            'fields',
            'kwargs',
            'properties',
            'tcex',
            'tql',
        ]

    def _reverse_transform(self, kwargs):
        """Reverse mapping of the _metadata_map method."""

        def reverse_transform(kwargs):
            reversed_mappings = {}
            for key, value in kwargs.items():
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
    def as_entity(self):
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
        if not as_dict:
            return None
        return as_dict

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

    def delete(self, retry_count=0):
        """Delete the Case Management Object.

        If no id is present in the obj then returns immediately.
        """
        if not self.id:
            self.tcex.log.warning('A case without an ID cannot be deleted.')
            return None

        url = f'{self.api_endpoint}/{self.id}'
        current_retries = -1
        while current_retries < retry_count:
            r = self.tcex.session.delete(url)
            self.tcex.log.debug(
                f'Method: ({r.request.method.upper()}), '
                f'Status Code: {r.status_code}, '
                f'URl: ({r.url})'
            )
            self.tcex.log.trace(f'response: {r.text}')
            if not self.success(r):
                current_retries += 1
                if current_retries >= retry_count:
                    err = r.text or r.reason
                    self.tcex.handle_error(950, [r.status_code, err, r.url])
                else:
                    continue
            break
        return None

    def entity_mapper(self, entity):
        """Stub for entity mapper"""
        raise NotImplementedError('Child class must implement this method.')

    def get(self, all_available_fields=False, case_management_id=None, retry_count=0, params=None):
        """Get the Case Management Object.

        params example: {
            'result_limit': 100, # How many results are retrieved.
            'result_start': 10,  # Starting point on retrieved results.
            'fields': ['caseId', 'summary'] # Additional fields returned on the results
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
            k = self.tcex.util.snake_to_camel(k)
            params[k] = v

        cm_id = case_management_id or self.id
        url = f'{self.api_endpoint}/{cm_id}'
        current_retries = -1
        entity = None

        # add fields parameter if provided
        if all_available_fields:
            params['fields'] = []
            for field in self.available_fields:
                params['fields'].append(field)

        if not cm_id:
            message = '{"message": "No ID provided.", "status": "Error"}'
            self.tcex.handle_error(951, ['GET', '404', message, url])

        # @bpurdy - what is the retry count for? tcex session has built-in retry
        r = None
        while current_retries < retry_count:
            r = self.tcex.session.get(url, params=params)
            self.tcex.log.debug(
                f'Method: ({r.request.method.upper()}), '
                f'Status Code: {r.status_code}, '
                f'URl: ({r.url})'
            )
            self.tcex.log.trace(f'response: {r.text}')
            if not self.success(r):
                current_retries += 1
                if current_retries >= retry_count:
                    err = r.text or r.reason
                    self.tcex.handle_error(951, ['GET', r.status_code, err, r.url])
                else:
                    continue
            entity = r.json()
            break
        self.entity_mapper(entity.get('data', {}))
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
    def properties(self):
        """Return defined API properties for the current object."""
        if self._properties is None:
            r = self.tcex.session.options(self.api_endpoint, params={'show': 'readOnly'})
            if r.ok:
                self._properties = r.json()
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
        as_dict = self.as_dict

        method = 'POST'
        url = self.api_endpoint
        if self.id:
            # if the ID is included, its an update
            method = 'PUT'
            url = f'{self.api_endpoint}/{self.id}'

        # make the request
        r = self.tcex.session.request(method, url, json=self._reverse_transform(as_dict))
        self.tcex.log.debug(
            f'Method: ({r.request.method.upper()}), '
            f'Status Code: {r.status_code}, '
            f'URl: ({r.url})'
        )
        self.tcex.log.trace(f'body: {self._reverse_transform(as_dict)}')
        self.tcex.log.trace(f'response: {r.text}')

        if not r.ok:
            err = r.text or r.reason
            self.tcex.handle_error(951, [r.request.method, r.status_code, err, r.url])

        r_json = r.json()
        if not self.id:
            self.id = r_json.get('data', {}).get('id')
        as_dict['id'] = self.id
        self.entity_mapper(r_json.get('data', r_json))

        return r

    @staticmethod
    def success(r):
        """[summary]

        Args:
            r:

        Return:

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
    def tql(self):
        """Return TQL data keywords."""
        if self._tql is None:
            r = self.tcex.session.options(f'{self.api_endpoint}/tql', params={})
            if r.ok:
                self._tql = r.json()['data']

        return self._tql
