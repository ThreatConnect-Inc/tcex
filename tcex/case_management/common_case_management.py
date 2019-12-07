# -*- coding: utf-8 -*-
class CommonCaseManagement(object):
    def __init__(self, tcex, api_endpoint, kwargs):
        self._tcex = tcex
        self._id = kwargs.get('id', None)
        self._transform_kwargs(kwargs)
        self.api_endpoint = api_endpoint

    @property
    def required_properties(self):
        return []

    @property
    def _excluded_properties(self):
        return ['tcex', 'kwargs', 'api_endpoint']

    @property
    def tcex(self):
        return self._tcex

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, cm_id):
        self._id = cm_id

    @property
    def as_dict(self):
        properties = vars(self)
        as_dict = {}
        for key, value in properties.items():
            key = key.lstrip('_')
            if key in self._excluded_properties:
                continue
            try:
                value = value.as_dict
            except AttributeError:
                pass
            if value is None:
                continue
            as_dict[key] = value
        if not as_dict:
            return None
        return as_dict

    def _transform_kwargs(self, kwargs):
        for key, value in dict(kwargs).items():
            new_key = self._metadata_map.get(key, key)
            # if key in ['date_added', 'eventDate', 'firstSeen', 'publishDate']:
            #     transformed_value = self._utils.format_datetime(value,
            #                                                   date_format='%Y-%m-%dT%H:%M:%SZ')
            kwargs[new_key] = kwargs.pop(key)

    @property
    def _metadata_map(self):
        return {
            'caseId': 'case_id',
            'caseXid': 'case_xid',
            'taskId': 'task_id',
            'artifactId': 'artifact_id',
            'dateAdded': 'date_added',
            'lastModified': 'last_modified',
            'userName': 'user_name',
            'createdBy': 'created_by',
            'dataType': 'data_type',
            'intelType': 'intel_type',
            'isWorkflow': 'is_workflow',
            'workflowId': 'workflow_id',
            'workflowPhase': 'workflow_phase',
            'workflowStep': 'workflow_step',
            'artifact_type': 'type',
            'artifactType': 'type',
            'fileData': 'file_data',
            'eventDate': 'event_date',
            'systemGenerated': 'system_generated',
            'parentCase': 'parent_case'
        }

    def delete(self, retry_count=0):
        if not self.id:
            return
        url = '{}/{}'.format(self.api_endpoint, self.id)
        current_retries = -1
        while current_retries < retry_count:
            response = self.tcex.session.delete(url)
            if not self.success(response):
                current_retries += 1
                if current_retries >= retry_count:
                    err = response.text or response.reason
                    self.tcex.handle_error(950, [response.status_code, err, response.url])
                else:
                    continue
            break
        return None

    def get(self, all_available_fields=False, case_management_id=None, retry_count=0, fields=None):
        if fields is None:
            fields = []
        cm_id = case_management_id or self.id
        url = '{}/{}'.format(self.api_endpoint, cm_id)
        current_retries = -1
        entity = None
        parameters = {'fields': []}
        if all_available_fields:
            for field in self.available_fields:
                parameters['fields'].append(field)
        elif fields:
            for field in fields:
                parameters['fields'].append(field)

        while current_retries < retry_count:
            response = self.tcex.session.get(url, params=parameters)
            if not self.success(response):
                current_retries += 1
                if current_retries >= retry_count:
                    err = response.text or response.reason
                    self.tcex.handle_error(951, ['GET', response.status_code, err, response.url])
                else:
                    continue
            entity = response.json()
            break
        self.entity_mapper(entity.get('data', {}))
        return self

    @property
    def available_fields(self):
        return []

    def _reverse_transform(self, kwargs):
        reversed_transform_mapping = dict((v, k) for k, v in self._metadata_map.items())

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

        # for key, value in dict(kwargs).items():
        #     if isinstance(value, dict):
        #     if isinstance(value, list):
        #         for entry in value:
        #             value = self._reverse_transform(entry)
        #         if value:
        #             reversed_mappings[key] = [value]
        #     else:
        #         for mapped_key, mapped_value in self._metadata_map.items():
        #             if key == mapped_value:
        #                 key = mapped_key
        #
        # return reversed_mappings

    def submit(self):
        url = self.api_endpoint
        as_dict = self.as_dict

        # if the ID is included, its an update
        if self.id:
            url = '{}/{}'.format(self.api_endpoint, self.id)
            r = self.tcex.session.put(url, json=self._reverse_transform(as_dict))
        else:
            r = self.tcex.session.post(url, json=self._reverse_transform(as_dict))

        if r.ok:
            r_json = r.json()
            if not self.id:
                self.id = r_json.get('data', {}).get('id')
            as_dict['id'] = self.id
            self.entity_mapper(self.get().as_dict)
            return self
        else:
            err = r.text or r.reason
            if self.id:
                self.tcex.handle_error(951, ['PUT', r.status_code, err, r.url])
            else:
                self.tcex.handle_error(951, ['POST', r.status_code, err, r.url])
        return r

    @staticmethod
    def success(r):
        """

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
