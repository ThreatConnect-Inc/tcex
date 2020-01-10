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
        self._id = kwargs.get('id', None)
        self._transform_kwargs(kwargs)
        self.api_endpoint = api_endpoint.value
        self.tcex = tcex

    def __str__(self):
        """Printable version of Object"""
        printable_string = ''
        for key, value in sorted(vars(self).items()):
            if key in ['tcex']:
                continue
            key = f'{key.lstrip("_")} '

            if value is None:
                printable_string += f'{key:.<40} {"null":<50}\n'
            elif isinstance(value, (int, str)):
                printable_string += f'{key:.<40} {value:<50}\n'
            else:
                printable_string += f'{key:.<40} {"<object>":<50}\n'
        return printable_string

    @property
    def _excluded_properties(self):
        """Return a list of properties to exclude when creating a dict of the children class."""
        return ['api_endpoint', 'kwargs', 'tcex']

    @property
    def _metadata_map(self):
        """Return a mapping of kwargs to expected args."""
        return {
            'artifactId': 'artifact_id',
            'artifact_type': 'type',
            'artifactType': 'type',
            'caseId': 'case_id',
            'caseXid': 'case_xid',
            'completedDate': 'completed_date',
            'createdBy': 'created_by',
            'dataType': 'data_type',
            'dateAdded': 'date_added',
            'dueDate': 'due_date',
            'eventDate': 'event_date',
            'fileData': 'file_data',
            'firstName': 'first_name',
            'intelType': 'intel_type',
            'isWorkflow': 'is_workflow',
            'lastModified': 'last_modified',
            'lastName': 'last_name',
            'parentCase': 'parent_case',
            'systemGenerated': 'system_generated',
            'taskId': 'task_id',
            'taskXid': 'task_xid',
            'userAccess': 'user_access',
            'userName': 'user_name',
            'workflowId': 'workflow_id',
            'workflowPhase': 'workflow_phase',
            'workflowStep': 'workflow_step',
            'workflowTemplate': 'workflow_template',
        }

    def _reverse_transform(self, kwargs):
        """Reverse mapping of the _metadata_map method."""
        reversed_transform_mapping = {v: k for k, v in self._metadata_map.items()}

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
                new_key = reversed_transform_mapping.get(key, key)
                if key in ['type']:
                    new_key = key
                reversed_mappings[new_key] = value
            return reversed_mappings

        return reverse_transform(kwargs)

    def _transform_kwargs(self, kwargs):
        """Map the provided kwargs to expected arguments."""
        for key in dict(kwargs):
            new_key = self._metadata_map.get(key, key)
            # if key in ['date_added', 'eventDate', 'firstSeen', 'publishDate']:
            #     transformed_value = self._utils.format_datetime(
            #         value, date_format='%Y-%m-%dT%H:%M:%SZ'
            #     )
            kwargs[new_key] = kwargs.pop(key)

    @property
    def as_entity(self):
        """Placeholder for common method."""
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
        """Stub for available fields"""
        raise NotImplementedError('Child class must implement this method.')

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

    def get(self, all_available_fields=False, case_management_id=None, retry_count=0, fields=None):
        """Get the Case Management Object.

        Args:
            all_available_fields (bool): If True all available fields will be returned.
            case_management_id (int): The id of the case management object to be returned.
            retry_count (int, optional): [description]. Defaults to 0.
            fields (list): A list of the fields that should be returned.

        Returns:
            Object: A artifact, case, note, task, tag, or workflow object.
        """
        cm_id = case_management_id or self.id
        fields = fields or []
        url = f'{self.api_endpoint}/{cm_id}'
        current_retries = -1
        entity = None
        parameters = {'fields': []}

        # add fields parameter if provided
        if all_available_fields:
            for field in self.available_fields:
                parameters['fields'].append(field)
        elif fields:
            for field in fields:
                parameters['fields'].append(field)

        # @bpurdy - what is the retry count for? tcex session has built-in retry
        while current_retries < retry_count:
            r = self.tcex.session.get(url, params=parameters)
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
        return self

    @property
    def id(self):
        """Return the id of the case management object."""
        return self._id

    @id.setter
    def id(self, cm_id):
        """Set the id of the case management object."""
        self._id = cm_id

    @property
    def required_properties(self):
        """Return a list of required fields for an object."""
        return []

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
