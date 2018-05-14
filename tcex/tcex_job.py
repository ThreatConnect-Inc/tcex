# -*- coding: utf-8 -*-
""" TcEx Framework Job Module """
import json
import re
import time


class TcExJob(object):
    """Job processing functionality.

    .. warning:: This module will be deprecated in version 0.9.0.

    Supports batch indicator adds and allows structured group adds.
    """

    def __init__(self, tcex):
        """Initialize the Class properties.

        Args:
            tcex (instance): An instance of TcEx class.
        """
        self._tcex = tcex

        # defaults batch settings
        self._batch_action = self._tcex.default_args.batch_action
        self._batch_chunk = self._tcex.default_args.batch_chunk
        self._batch_halt_on_error = self._tcex.default_args.batch_halt_on_error
        self._batch_poll_interval_max = self._tcex.default_args.batch_poll_interval_max
        self._batch_poll_interval = self._tcex.default_args.batch_poll_interval
        self._batch_write_type = self._tcex.default_args.batch_write_type

        # containers
        self._associations = []
        self._file_occurrences = []
        self._group_cache = {}
        self._group_cache_id = {}
        self._group_associations = []
        self._group_results = {
            'cached': [],
            'failed': [],
            'not_saved': [],
            'saved': [],
            'submitted': []
        }
        self._groups = []
        self._groups_response = []
        self._indicator_results = {
            'failed': [],
            'not_saved': [],
            'saved': [],
            'submitted': []
        }
        self._indicators = []
        self._indicators_response = []

        # batch "bad" errors
        self._batch_failures = [
            'Encountered an unexpected Exception while processing batch job',
            'would exceed the number of allowed indicators'
        ]

        # keep the batch_id
        self._indicator_batch_ids = []

    def _chunk_indicators(self):
        """Split indicator list into smaller more manageable numbers."""
        try:
            for i in xrange(0, len(self._indicators), self._batch_chunk):
                yield self._indicators[i:i + self._batch_chunk]
        except NameError:  # Python 3 uses range() instead of xrange()
            for i in range(0, len(self._indicators), self._batch_chunk):
                yield self._indicators[i:i + self._batch_chunk]

    def _group_add(self, resource_type, resource_name, owner, data=None):
        """Add a group to ThreatConnect.

        Args:
            resource_type (string): String with resource [group] type.
            resource_name (string): The name of the group.
            owner (string): The name of the TC owner for the group add.
            data (Optional [dictionary]): Any optional group parameters, tags,
                or attributes.

        Returns:
            (integer): The ID of the created resource.
        """
        resource_id = None
        if data is None:
            data = {}

        self._tcex.log.debug(u'Adding {} "{}" in owner {}'.format(
            resource_type, resource_name, owner))
        resource_body = {}
        resource = self._tcex.resource(resource_type)
        resource.http_method = 'POST'
        resource.owner = owner

        # dynamically handle additional parameters
        for param, value in data.items():
            if param in ['attribute', 'fileData', 'tag', 'type']:
                # attributes, fileData and tags are handled separately
                continue
            resource_body[param] = value
            self._tcex.log.debug(u'Adding parameter {}:{}'.format(
                param, value))

        resource.body = json.dumps(resource_body)
        results = resource.request()

        if results.get('status') == 'Success':
            resource_id = results['data']['id']  # get created group ID
            # update cache
            self._group_cache[owner][resource_type][resource_name] = resource_id

            self._group_results['saved'].append(resource_name)
            self._group_results['not_saved'].remove(resource_name)
            resource = self._tcex.resource(resource_type)
            resource.http_method = 'POST'

            # add attributes
            for attribute in data.get('attribute', []):
                self._tcex.log.debug(u'Adding attribute type "{}" to Group ID {}'.format(
                    attribute.get('type'), resource_id))
                resource.resource_id(resource_id)
                attribute_resource = resource.attributes()
                attribute_resource.body = json.dumps(attribute)
                a_results = attribute_resource.request()
                if a_results.get('status') != 'Success':
                    err = u'Failed adding attribute type "{}" with value "{}" to group "{}". ({})'
                    err = err.format(
                        attribute.get('type'), attribute.get('value'), resource_name,
                        a_results.get('response').text)
                    self._tcex.log.error(err)
                    self._tcex.exit_code = 3

            # add tags
            for tag in data.get('tag', []):
                self._tcex.log.debug(u'Adding tag ({})'.format(tag))
                resource.resource_id(resource_id)
                tag_resource = resource.tags(tag.get('name'))
                t_results = tag_resource.request()
                if t_results.get('status') != 'Success':
                    err = u'Failed adding tag "{}" ({})'.format(
                        tag, t_results.get('response').text)
                    self._tcex.log.error(err)
                    self._tcex.exit_code = 3

            # document upload
            if resource_type == 'Document' and data.get('fileData') is not None:
                try:
                    resource.upload(resource_id, data.get('fileData').encode('utf-8'))
                except UnicodeDecodeError:
                    resource.upload(resource_id, data.get('fileData'))  # py2 issue
                except AttributeError:
                    resource.upload(resource_id, data.get('fileData'))  # py3
                resource.http_method = 'POST'
                u_results = resource.request()
                if u_results['response'].status_code == 401:
                    # PUT if document already exists
                    resource = self._tcex.resource(resource_type)
                    resource.upload(resource_id, data.get('fileData'))
                    resource.http_method = 'PUT'
                    u_results = resource.request()

                if u_results.get('status') != 'Success':
                    err = u'Failed uploading document {} to group {}. ({})'.format(
                        data.get('fileName'), resource_name, u_results.get('response').text)
                    self._tcex.log.error(err)
                    self._tcex.exit_code = 3
        else:
            self._group_results['failed'].append(resource_name)
            err = u'Failed adding group "{}" ({})'.format(
                resource_name, results.get('response').text)
            self._tcex.log.error(err)
            self._tcex.exit_code = 3

        return resource_id

    def _group_delete_by_id(self, resource_type, resource_id):
        """Delete a group from ThreatConnect.

        Args:
            resource_type (string): String with resource [group] type.
            resource_id (string): The ID of the group.
        """
        # self._tcex.log.debug(u'Deleting {} with ID {}.'.format(resource_type, resource_id))
        resource = self._tcex.resource(resource_type)
        resource.http_method = 'DELETE'
        resource.resource_id(resource_id)
        results = resource.request()
        if results.get('status') != 'Success':
            self._tcex.log.warning(u'Deleted {} with ID {} failed ({}).'.format(
                resource_type, resource_id, results.get('response').text))

    def _group_delete_by_name(self, owner, resource_type, resource_name):
        """Delete group(s) from ThreatConnect by Name.

        Args:
            resource_type (string): String with resource [group] type.
            resource_name (string): The name of the group.
        """
        resource = self._tcex.resource(resource_type)
        resource.add_filter('name', '=', resource_name)
        resource.owner = owner
        for results in resource:
            if results.get('status') != 'Success':
                self._tcex.log.warning(u'Retrieve {} with name {} failed ({}).'.format(
                    resource_type, resource_name, results.get('response').text))
            else:
                # remove group from cache
                self.group_cache_remove(owner, resource_type, resource_name)
                for result in results['data']:
                    self._group_delete_by_id(resource_type, result.get('id'))

    def _indicators_replace_stub(self, owner):
        """Process Indicator data replacing associatedGroup stub values with the Group ID.

        Format of a stub ${<group name>:<group type>}.

        Args:
            indicators (list): Batch Indicator Data.
            owner (string):  The owner name for the indicator to be written.
        """
        for indicator_data in self._indicators:
            for group_value in list(indicator_data.get('associatedGroup', [])):
                if not str(group_value).startswith('$'):
                    continue

                # remove stub value from list
                indicator_data['associatedGroup'].remove(group_value)
                # extract group name and type from stub
                group_pattern = re.compile(r'^\$\((.+):(.+)\)$')
                group_data = re.search(group_pattern, group_value)
                group_name = group_data.group(1)
                group_type = group_data.group(2)
                group_id = self.group_id(group_name, owner, group_type)

                if group_id is not None:
                    self._tcex.log.debug('Replacing stub {} with id {}.'.format(
                        group_value, group_id))
                    # add group id returned from stub values
                    indicator_data['associatedGroup'].append(group_id)

    def _process_file_occurrences(self, owner):
        """Process file occurrences and write to TC API.

        Args:
            owner (string):  The owner name for the indicator to be written.
        """
        # POST /v2/indicators/files/BE7DE2F0CF48294400C714C9E28ECD01/fileOccurrences
        # supported format -> 2014-11-03T00:00:00-05:00

        resource = self._tcex.resource('File')
        resource.http_method = 'POST'
        resource.owner = owner
        resource.url = self._tcex.default_args.tc_api_path

        for occurrence in self._file_occurrences:
            # remove the hash from the dictionary and add to URI
            if occurrence.get('hash') is None:
                err = u'A hash value must be provided.'
                self._tcex.log.error(err)
                return
            resource.occurrence(occurrence.pop('hash'))
            resource.body = json.dumps(occurrence)
            resource.request()

    def _process_association(self, owner):
        """Process groups and write to TC API.

        Args:
            owner (string):  The owner name for the indicator to be written.
        """
        for a in self._associations:
            self._tcex.log.info(u'creating association: resource {} association {}'.format(
                a.get('resource_value'), a.get('association_value')))

            association_type = a.get('association_type')
            association_id = a.get('association_value')
            resource_type = a.get('resource_type')
            resource_id = a.get('resource_value')
            custom_association_name = a.get('custom_association_name')
            # get group id from group name (duplicate group names not supported)
            if resource_type in self._tcex.group_types:
                resource_id = self.group_id(resource_id, owner, resource_type)
            if association_type in self._tcex.group_types:
                association_id = self.group_id(association_id, owner, association_type)

            resource = self._tcex.resource(resource_type)
            resource.http_method = 'POST'
            resource.resource_id(resource_id)
            resource.owner = owner
            resource.url = self._tcex.default_args.tc_api_path

            ar = self._tcex.resource(association_type)
            ar.resource_id(association_id)
            if custom_association_name:
                association_resource = resource.association_custom(custom_association_name, ar)
            else:
                association_resource = resource.association_pivot(ar)
            association_results = association_resource.request()
            if association_results.get('status') != 'Success':
                err = 'Failed adding association ({}).'.format(
                    association_results.get('response').text)
                self._tcex.log.error(err)
                self._tcex.exit_code = 3

    def _process_group_association(self, owner):
        """Process group associations and write to ThreatConnect API.

        Args:
            owner (string): The owner name for the associations to be written.
        """
        for ga in self._group_associations:
            self._tcex.log.info(u'creating association: group "{}" indicator {}'.format(
                ga.get('group_name'), ga.get('indicator')))

            group_id = self.group_id(ga.get('group_name'), owner, ga.get('group_type'))
            if group_id is None:
                continue

            resource = self._tcex.resource(ga.get('indicator_type'))
            resource.http_method = 'POST'
            resource.indicator(ga.get('indicator'))
            resource.owner = owner
            resource.url = self._tcex.default_args.tc_api_path

            ar = self._tcex.resource(ga.get('group_type'))
            ar.resource_id(group_id)
            association_resource = resource.association_pivot(ar)
            association_resource.request()

    def _process_groups(self, owner, group_action):
        """Process groups and write to ThreatConnect API.

        Args:
            owner (string): The owner name for the groups to be written.
        """
        self._group_results['not_saved'] = list(self._group_results.get('submitted', []))
        for group in self._groups:
            # get group id from cache if exists
            group_name = group.get('name')
            group_type = group.get('type')
            group_id = self.group_id(group_name, owner, group_type)

            self._tcex.log.debug(u'Processing group ({})'.format(group_name))
            if group_action == 'duplicate':
                group_id = self._group_add(group_type, group_name, owner, group)
                if group_id is None and self._batch_halt_on_error:
                    self._tcex.log.info(u'Halt on error is enabled.')
                    self._tcex.exit_code = 1
                    break
                self._tcex.log.info(u'Created Group "{}" with id: {}'.format(group_name, group_id))
            elif group_action == 'replace':
                if group_id is not None:
                    # delete the group from TC and group cache
                    self._group_delete_by_name(owner, group_type, group_name)
                    self._tcex.log.info(u'Deleting Group "{}" with name: "{}"'.format(
                        group_type, group_name))

                group_id = self._group_add(group_type, group_name, owner, group)
                if group_id is None and self._batch_halt_on_error:
                    self._tcex.log.info(u'Halt on error is enabled.')
                    self._tcex.exit_code = 1
                    break
                else:
                    self.group_cache_add(group_name, owner, group_type, group_id)
                self._tcex.log.info(u'Created Group "{}" with id: {}'.format(group_name, group_id))
            elif group_action == 'skip':
                if group_id is None:
                    group_id = self._group_add(group_type, group_name, owner, group)
                    if group_id is None and self._batch_halt_on_error:
                        self._tcex.log.info(u'Halt on error is enabled.')
                        self._tcex.exit_code = 1
                        break
                    else:
                        self.group_cache_add(group_name, owner, group_type, group_id)
                    self._tcex.log.info(u'Created Group "{}" with id: {}'.format(
                        group_name, group_id))
                else:
                    # update group results tracking
                    self._group_results['cached'].append(group_name)
                    self._group_results['not_saved'].remove(group_name)
                    self._tcex.log.info(u'Skipping existing Group "{}")'.format(group_name))
            else:
                self._tcex.log.info(u'Invalid group action ({})'.format(group_action))

    def _process_indicators(self, owner, batch):
        """Process batch indicators and write to ThreatConnect API.

        Args:
            owner (string): The owner name for the indicator to be written.
            batch (boolean): Use the batch API to create indicators.
        """
        self._tcex.log.info(u'Processing {} indicators'.format(len(self._indicators)))
        if batch:
            self._process_indicators_batch(owner)
        else:
            self._process_indicators_v2(owner)

    def _process_indicators_batch(self, owner):
        """Process batch indicators and write to ThreatConnect API.

        .. Note:: Failed attributes and/or tags will not cause a batch import to fail.

        Args:
            owner (string):  The owner name for the indicator to be written.
        """
        batch_job_body = {
            'action': self._batch_action,
            'attributeWriteType': self._batch_write_type,
            'haltOnError': self._batch_halt_on_error,
            'owner': owner
        }

        halt = False
        for chunk in self._chunk_indicators():
            self._tcex.log.info(u'Batch Chunk Size: {}'.format(len(chunk)))

            # new batch resource for each chunk
            resource = self._tcex.resource('Batch')
            resource.http_method = 'POST'
            resource.url = self._tcex.default_args.tc_api_path
            resource.content_type = 'application/json'
            resource.body = json.dumps(batch_job_body)
            results = resource.request()

            if results['status'] == 'Success':
                batch_id = results.get('data')
                self._indicator_batch_ids.append(batch_id)

                resource.content_type = 'application/octet-stream'
                resource.batch_id(batch_id)
                resource.body = json.dumps(chunk)
                # results = resource.request()
                data_results = resource.request()

                if data_results['status'] == 'Success':
                    # bcs - add a small delay before first status check then normal delay in loop
                    time.sleep(3)

                    poll_time = 0
                    while True:
                        self._tcex.log.debug(u'poll_time: {}'.format(poll_time))
                        if poll_time >= self._batch_poll_interval_max:
                            msg = u'Status check exceeded max poll time.'
                            self._tcex.log.error(msg)
                            self._tcex.message_tc(msg)
                            self._tcex.exit(1)

                        status = self.batch_status(batch_id)
                        if status.get('completed'):
                            if status.get('errors'):
                                if self._batch_halt_on_error:
                                    self._tcex.exit_code = 1
                                    halt = True
                                    # all indicator in chunk will be not_saved
                                    self._indicator_results['not_saved'].extend(
                                        [i.get('summary') for i in chunk])
                                    break
                                else:
                                    # all indicators were saved minus failed; not_save == failed
                                    self._indicator_results['not_saved'] = self._indicator_results.get(
                                        'failed', [])
                                    self._indicator_results['saved'].extend(
                                        [i.get('summary') for i in chunk
                                         if i.get('summary') not in self._indicator_results.get(
                                             'failed', [])])
                                    self._indicators_response.extend(
                                        [i for i in chunk
                                         if i.get('summary') not in self._indicator_results.get(
                                             'failed', [])])
                            else:
                                # all indicators were saved
                                self._indicator_results['saved'].extend(
                                    [i.get('summary') for i in chunk])
                                self._indicators_response.extend(chunk)
                            break  # no need to check status anymore

                        time.sleep(self._batch_poll_interval)
                        poll_time += self._batch_poll_interval
            else:
                self._tcex.log.warning('API request failed ({}).'.format(
                    results.get('response').text))
                # TODO: move this and above duplicate code to "if halt" below after validating logic
                self._tcex.exit_code = 1
                # all indicator in chunk will be not_saved
                self._indicator_results['not_saved'].extend([i.get('summary') for i in chunk])
                halt = True

            if halt:
                self._tcex.log.info(u'Halting on error.')
                break

    def _process_indicators_v2(self, owner):
        """Process batch indicators and write to ThreatConnect API using **/v2/indicators**.

        Args:
            owner (string):  The owner name for the indicator to be written.
        """
        self._indicator_results['not_saved'] = list(self._indicator_results.get('submitted', []))
        for i_data in self._indicators:
            resource = self._tcex.resource(i_data.get('type'))

            indicators = self._tcex.expand_indicators(i_data.get('summary'))
            try:
                i_value = [i for i in indicators if i is not None][0]
            except IndexError as e:
                err = u'Cannot proceed without an Indicator. ({})'.format(e)
                self._tcex.log.error(err)
                raise RuntimeError(e)

            body = resource.entity_body(indicators)
            if i_data.get('rating') is not None:
                body['rating'] = i_data.get('rating')
            if i_data.get('confidence') is not None:
                body['confidence'] = i_data.get('confidence')
            if i_data.get('size') is not None:
                body['size'] = i_data.get('size')
            if i_data.get('dns_active') is not None:
                body['dns_active'] = i_data.get('dns_active')
            if i_data.get('whois_active') is not None:
                body['whois_active'] = i_data.get('whois_active')
            if i_data.get('source') is not None:
                body['source'] = i_data.get('source')

            resource.body = json.dumps(body)
            resource.http_method = 'POST'
            resource.owner = owner
            resource.url = self._tcex.default_args.tc_api_path

            i_results = resource.request()

            # PUT file indicator since API does not work consistently for all indicator types
            if i_data.get('type') == 'File' and i_results.get('response').status_code == 400:
                if 'MD5' in i_results.get('response').text:
                    i_value = body.get('md5', i_value)
                elif 'SHA-1' in i_results.get('response').text:
                    i_value = body.get('sha1', i_value)
                elif 'SHA-256' in i_results.get('response').text:
                    i_value = body.get('sha256', i_value)
                resource.http_method = 'PUT'
                resource.indicator(i_value)
                i_results = resource.request()
                resource.http_method = 'POST'  # reset http method after PUT

            # Log error and continue
            if i_results.get('status') != 'Success':
                self._indicator_results['failed'].append(i_data.get('summary'))
                err = u'Failed adding indicator {} type {} ({}).'.format(
                    i_data.get('summary'), i_data.get('type'), i_results.get('response').text)
                self._tcex.log.error(err)

                # halt on error check
                if self._batch_halt_on_error:
                    self._tcex.log.info(u'Halt on error is enabled.')
                    self._tcex.exit_code = 1
                    break
                else:
                    self._tcex.exit_code = 3
                    continue

            # update indicator result list
            self._indicator_results['saved'].append(i_data.get('summary'))
            self._indicator_results['not_saved'].remove(i_data.get('summary'))

            # build indicator results output
            results_data = i_results.get('data')

            # Boolen for halt on error
            halt = False

            # Add attribute to Indicator
            for attribute in i_data.get('attribute', []):
                # process attributes
                if resource.custom:
                    resource.indicator(i_data.get('summary'))
                else:
                    resource.indicator(i_value)
                attribute_resource = resource.attributes()  # pivot to attribute
                attribute_resource.http_method = 'POST'
                attribute_resource.body = json.dumps(attribute)
                a_results = attribute_resource.request()

                if a_results.get('status') != 'Success':
                    err = u'Failed adding attribute type {} with value {} to indicator {}.'
                    err = err.format(
                        attribute.get('type'), attribute.get('value'), i_data.get('summary'))
                    self._tcex.log.error(err)

                    # halt on error check
                    if self._batch_halt_on_error:
                        self._tcex.log.info(u'Halt on error is enabled.')
                        self._tcex.exit_code = 1
                        halt = True
                        break
                    else:
                        self._tcex.exit_code = 3
                        continue
                results_data.setdefault('attribute', []).append(a_results.get('data'))
            if halt:
                break

            for tag in i_data.get('tag', []):
                # process attributes
                if resource.custom:
                    resource.indicator(i_data.get('summary'))
                else:
                    resource.indicator(i_value)
                tag_resource = resource.tags(tag.get('name'))
                tag_resource.http_method = 'POST'
                t_results = tag_resource.request()
                if t_results.get('status') != 'Success':
                    err = u'Failed adding tag {} to indicator {}.'.format(
                        tag.get('name'), i_data.get('summary'))
                    self._tcex.log.error(err)

                    # halt on error check
                    if self._batch_halt_on_error:
                        self._tcex.log.info(u'Halt on error is enabled.')
                        self._tcex.exit_code = 1
                        halt = True
                        break
                    else:
                        self._tcex.exit_code = 3
                        continue
                results_data.setdefault('tag', []).append(tag)
            if halt:
                break

            for group_id in i_data.get('associatedGroup', []):
                group_type = self.group_cache_type(group_id, owner)
                if group_type is None:
                    err = u'Could not get Group Type for Group ID {} in Owner "{}"'.format(
                        group_id, owner)
                    self._tcex.log.error(err)
                    self._tcex.exit_code = 3
                    continue

                if resource.custom:
                    resource.indicator(i_data.get('summary'))
                else:
                    resource.indicator(i_value)
                ar = self._tcex.resource(group_type)
                ar.resource_id(group_id)
                association_resource = resource.association_pivot(ar)
                association_resource.http_method = 'POST'
                a_results = association_resource.request()
                if a_results.get('status') != 'Success':
                    err = u'Failed association group id {} to indicator {}.'.format(
                        group_id, i_data.get('summary'))
                    self._tcex.log.error(err)

                    # halt on error check
                    if self._batch_halt_on_error:
                        self._tcex.log.info(u'Halt on error is enabled.')
                        self._tcex.exit_code = 1
                        halt = True
                        break
                    else:
                        self._tcex.exit_code = 3
                        continue
                results_data.setdefault('associatedGroup', []).append(group_id)
            if halt:
                break

            self._indicators_response.append(results_data)

    def association(self, associations):
        """Add association data to TcEx job.

        This method will add association data to the association list.

        .. Warning:: There is no validation of the data passed to this method.

        **Example Data** *(required fields are highlighted)*

        .. code-block:: javascript
            :linenos:
            :lineno-start: 1
            :emphasize-lines: 2-5

            [{
              'association_value': '1.1.1.1',
              'association_type': 'Address',
              'resource_value': 'adversary-002',
              'resource_type': 'Adversary'
            },{
              'association_value': 'adversary-001',
              'association_type': 'Adversary',
              'resource_value': '1.1.1.1',
              'resource_type': 'Address'
            },{
              'association_value': 'adversary-001',
              'association_type': 'Adversary',
              'resource_value': 'threat-001',
              'resource_type': 'Threat',
            }]

        **Example Data for Creating Indicator-to-Indicator Associations**
        *(required fields are highlighted)*

        .. code-block:: javascript
            :linenos:
            :lineno-start: 1
            :emphasize-lines: 2-6

            {
              "association_value": "ASN1234",
              "association_type": tcex.safe_rt("ASN"),
              "resource_value": "1.2.3.4",
              "resource_type": "Address",
              "custom_association_name": "ASN to Address"
            }

        Args:
            associations (dict | list): Dictionary or List containing
                association data
        """
        if isinstance(associations, list):
            self._associations.extend(associations)
        elif isinstance(associations, dict):
            self._associations.append(associations)

    def batch_action(self, action):
        """Set the default batch action for argument parser.

        Args:
            action (string): Set batch job action.
        """
        if action in ['Create', 'Delete']:
            self._batch_action = action

    def batch_chunk(self, chunk_size):
        """Set batch chunk_size for argument parser.

        Args:
            chunk_size (integer): Set batch job chunk size.
        """
        self._batch_chunk = chunk_size

    def batch_halt_on_error(self, halt_on_error):
        """Set batch halt on error boolean for argument parser.

        Args:
            halt_on_error (boolean): Boolean value for halt on error.
        """
        if isinstance(halt_on_error, bool):
            self._batch_halt_on_error = halt_on_error

    def batch_indicator_success(self):
        """Check completion for all batch jobs associated with this instance.

        Iterate over self._indicator_batch_ids set in
        :py:meth:`~tcex.tcex_job.TcExJob._process_indicators` and return the status of all job.

        .. code-block:: javascript
            :linenos:
            :lineno-start: 1
            :emphasize-lines: 3

            {
              "status": "Success",
              "data": {
                "batchStatus": {
                  "id": 392,
                  "status": "Completed",
                  "errorCount": 1,
                  "successCount": 4,
                  "unprocessCount": 0
                }
              }
            }

        Returns:
            (dictionary): The status results from the Batch jobs.
        """

        status = {'success': 0, 'failure': 0, 'unprocessed': 0}

        resource = self._tcex.resource('Batch')
        resource.url = self._tcex.default_args.tc_api_path

        for batch_id in self._indicator_batch_ids:
            resource.batch_id(batch_id)
            results = resource.request()
            batch_status = results.get('data', {}).get('batchStatus', {})

            if results.get('status') == 'Success' and batch_status.get('status') == 'Completed':
                status['success'] += batch_status.get('successCount', 0)
                status['failure'] += batch_status.get('errorCount', 0)
                status['unprocessed'] += batch_status.get('unprocessCount', 0)

        return status

    def batch_poll_interval(self, interval):
        """Set batch polling interval for argument parser.

        Args:
            interval (integer): Seconds between polling.
        """
        if isinstance(interval, int):
            self._batch_poll_interval = interval

    def batch_poll_interval_max(self, interval_max):
        """Set batch polling interval max for argument parser.

        Args:
            interval_max (integer): Max seconds before timeout on batch.
        """
        if isinstance(interval_max, int):
            self._batch_poll_interval_max = interval_max

    def batch_status(self, batch_id):
        """Check the status of a batch job.

        This method will get the status of a batch job. Any errors returned from the batch status
        will be automatically logged.

        Critical errors are defined in the __init__ method in the self._batch_failures dictionary.
        If any of the critical errors are found the execution of the App will halt with a exit
        code of 1.  All other errors will set the status code to 3, but will not cause the execution
        to halt.

        Args:
            batch_id (int): Id of the batch job.

        Returns:
            (dict): A dictionary with status and error boolean.
        """
        status = {
            'completed': False,
            'errors': False
        }

        resource = self._tcex.resource('Batch')
        resource.url = self._tcex.default_args.tc_api_path
        resource.batch_id(batch_id)
        results = resource.request()

        self._tcex.log.info(u'batch id: {}'.format(batch_id))
        if results.get('status') == 'Success':
            if results['data']['status'] == 'Completed':
                status['completed'] = True

                status_msg = u'Batch Job completed, totals: '
                status_msg += u'succeeded: {}, '.format(results.get('data').get('successCount'))
                status_msg += u'failed: {}, '.format(results.get('data').get('errorCount'))
                status_msg += u'unprocessed: {}'.format(results.get('data').get('unprocessCount'))
                self._tcex.log.info(status_msg)

                if results['data']['errorCount'] > 0:
                    status['errors'] = True
                    self._tcex.exit_code = 3
                    time.sleep(2)

                    poll_time = 0
                    while True:
                        resource = self._tcex.resource('Batch')
                        resource.url = self._tcex.default_args.tc_api_path
                        resource.errors(batch_id)
                        error_results = resource.request()
                        if poll_time >= self._batch_poll_interval_max:
                            msg = u'Status check exceeded max poll time.'
                            self._tcex.log.error(msg)
                            self._tcex.message_tc(msg)
                            self._tcex.exit(1)
                        elif error_results.get('response').status_code == 200:
                            break
                        self._tcex.log.info(u'Error retrieve sleep ({} seconds)'.format(
                            self._batch_poll_interval))
                        time.sleep(self._batch_poll_interval)
                        poll_time += self._batch_poll_interval

                    try:
                        errors = json.loads(self._tcex.s(error_results.get('data')))
                    except TypeError as e:
                        err = u'Error loading Batch Error data ({})'.format(e)
                        self._tcex.log.error(err)
                        errors = []

                    for error in errors:
                        error_reason = error.get('errorReason')
                        error_source = error.get('errorSource')
                        # fix issue with API response
                        if error_source is not None and '  :  ' in error_source:
                            error_source = error.get('errorSource').replace('  ', ' ')
                        # errorSource won't always have an indicator per cblades
                        if error_source in self._indicator_results.get('submitted', []):
                            self._indicator_results['failed'].append(error_source)
                        for error_msg in self._batch_failures:
                            if re.findall(error_msg, error_reason):
                                # Critical Error
                                err = u'Batch Error: {}'.format(error)
                                self._tcex.message_tc(err)
                                self._tcex.log.error(err)
                                self._tcex.exit(1)
                        self._tcex.log.warn(u'Batch Error: {}'.format(error))
            else:
                self._tcex.log.debug(u'Batch Status: {}'.format(results.get('data').get('status')))

        return status

    def batch_write_type(self, write_type):
        """Set batch attributes write type for argument parser.

        Args:
            write_type (string): Type of Append or Replace.
        """
        if write_type in ['Append', 'Replace']:
            self._batch_write_type = write_type

    def file_occurrence(self, fo):
        """Add a file occurrence to job.

        Args:
            fo (dictionary): The file occurrence data.

        .. Warning:: There is no validation of the data passed to this method.

        **Example Data** *(required fields are highlighted)*

        .. code-block:: javascript
            :linenos:
            :lineno-start: 1
            :emphasize-lines: 3

            {
                "date" : "2014-11-03T00:00:00-05:00",
                "fileName" : "win999301.dll",
                "hash": "BE7DE2F0CF48294400C714C9E28ECD01",
                "path" : "C:\\Windows\\System"
            }

        .. Note:: The hash in the example above is not posted in the body, but extracted to use
                  in the URI.
        """
        # POST /v2/indicators/files/BE7DE2F0CF48294400C714C9E28ECD01/fileOccurrences

        if isinstance(fo, list):
            self._file_occurrences.extend(fo)
        elif isinstance(fo, dict):
            self._file_occurrences.append(fo)

    def group(self, group):
        """Add group data to TcEx job.

        This method will accept a list or dictionary of formatted *Group* data and submit it to the
        API when the :py:meth:`~tcex.tcex_job.TcExJob.process` method is called.

        .. Warning:: There is no validation of the data passed to this method. Any duplicate group
                     name will be skipped.

        **Example Data** *(required fields are highlighted)*

        .. code-block:: javascript
            :linenos:
            :lineno-start: 1
            :emphasize-lines: 9,14

            {
              'attribute': [
                {
                  'type': 'Description',
                  'value': 'Test Description'
                }
              ],
              'eventDate': '2015-03-7T00:00:00Z'
              'name': 'adversary-001',
              'tag': [{
                'name': 'Pop Star'
              }],
              'type': 'Adversary'
            }

        Args:
            group (dict | list): Dictionary or List containing group data.
        """
        if isinstance(group, dict):
            group = [group]

        for g in group:
            if g.get('name') not in [n.get('name') for n in self._groups]:
                self._group_results['submitted'].append(g.get('name'))
                self._groups.append(g)

    def group_association(self, associations):
        """Add group association data to TcEx job.

        This method will add group association data to the group association list.

        .. Warning:: There is no validation of the data passed to this method.

        **Example Data** *(required fields are highlighted)*

        .. code-block:: javascript
            :linenos:
            :lineno-start: 1
            :emphasize-lines: 2-5

            {
              'group_name': 'adversary-001',
              'group_type': 'Adversary',
              'indicator': '1.1.1.1',
              'indicator_type': 'Address'
            }

        Args:
            associations (dict | list): Dictionary or List containing group
                association data.
        """
        if isinstance(associations, list):
            self._group_associations.extend(associations)
        elif isinstance(associations, dict):
            self._group_associations.append(associations)

    @property
    def group_association_len(self):
        """The current length of the group association list.

        Returns:
            (integer): The length of the group association list.
        """
        return len(self._group_associations)

    def group_cache(self, owner, resource_type):
        """Cache group data from the ThreatConnect Platform.

        The method will cache ThreatConnect group data by owner and type.

        **Cache Structure**
        ::

            Owner -> Group Type -> Group Name:Group Id

        Args:
            owner (string): The name of the ThreatConnect owner
            resource_type (string): The resource type name

        Returns:
            (dictionary): Dictionary of group resources
        """
        # already cached
        if owner in self._group_cache:
            if resource_type in self._group_cache.get(owner):
                return self._group_cache.get(owner).get(resource_type)

        self._tcex.log.info(u'Caching group type {} for owner {}'.format(resource_type, owner))
        self._group_cache.setdefault(owner, {})
        self._group_cache[owner].setdefault(resource_type, {})

        resource = self._tcex.resource(resource_type)
        resource.owner = owner
        resource.url = self._tcex.default_args.tc_api_path
        data = []
        for results in resource:
            if results.get('status') == 'Success':
                data += results.get('data')
            else:
                err = u'Failed retrieving result during pagination.'
                self._tcex.log.error(err)
                raise RuntimeError(err)

        for group in data:
            self._tcex.log.debug(u'cache - group name: ({})'.format(group.get('name')))
            dup = self._group_cache.get(owner, {}).get(resource_type, {}).get(group.get('name'))
            if dup is not None:
                warn = u'A duplicate Group name was found ({}). '
                warn += u'Duplicates are not supported in cache.'
                warn = warn.format(group.get('name'))
                self._tcex.log.warning(warn)
            self._group_cache[owner][resource_type][group['name']] = group.get('id')

        return self._group_cache.get(owner).get(resource_type)

    def group_id(self, name, owner, resource_type):
        """Get the group id from the group cache.

        Args:
            name(string): The name of the Group.
            owner (string): The TC Owner where the resource should be found.
            resource_type (string): The resource type name.

        Returns:
            (integer): The ID for the provided group name and owner.
        """
        self._tcex.log.debug(u'Retrieving {} ID for group "{}" in "{}".'.format(
            resource_type, name, owner
        ))
        if self._group_cache.get(owner, {}).get(resource_type) is None:
            self.group_cache(owner, resource_type)

        return self._group_cache.get(owner, {}).get(resource_type, {}).get(name)

    def group_cache_add(self, name, owner, resource_type, resource_id):
        """Add a group to the group cache.

        Args:
            name(string): The name of the Group.
            owner (string): The TC Owner where the resource should be found.
            resource_type (string): The resource type name.

        Returns:
            (integer): The ID for the provided group name and owner.
        """
        if self._group_cache.get(owner, {}).get(resource_type, {}) is None:
            self.group_cache(owner, resource_type)

        self._group_cache[owner][resource_type][name] = resource_id

    def group_cache_remove(self, name, owner, resource_type):
        """Remove a group from the group cache.

        Args:
            name(string): The name of the Group.
            owner (string): The TC Owner where the resource should be found.
            resource_type (string): The resource type name.

        Returns:
            (integer): The ID for the provided group name and owner.
        """
        self._tcex.log.debug(
            u'Removing {} ID for group "{}" in "{}".'.format(
                resource_type, name, owner))
        if self._group_cache.get(owner, {}).get(resource_type, {}).get(name) is not None:
            del self._group_cache[owner][resource_type][name]

    def group_cache_type(self, group_id, owner):
        """Get the group type for the provided group id.

        **Cache Structure**
        ::

            Owner -> Group Id:Group Type

        Args:
            group_id (string): The group id to lookup.
            owner (string): The TC Owner where the resource should be found.
            resource_type (string): The resource type name.

        Returns:
            (integer): The ID for the provided group name and owner.
        """
        group_id = int(group_id)
        if self._group_cache_id.get(owner) is None:

            self._tcex.log.info(u'Caching groups for owner {}'.format(owner))
            self._group_cache_id.setdefault(owner, {})

            resource = self._tcex.resource('Group')
            resource.owner = owner
            resource.url = self._tcex.default_args.tc_api_path
            for results in resource:
                if results['status'] == 'Success':
                    for group in results.get('data'):
                        self._group_cache_id[owner][int(group.get('id'))] = group.get('type')
                else:
                    err = u'Failed retrieving result during pagination.'
                    self._tcex.log.error(err)
                    raise RuntimeError(err)

        return self._group_cache_id.get(owner, {}).get(group_id)

    @property
    def group_len(self):
        """The current length of the group list.

        Returns:
            (integer): The length of the group list.
        """
        return len(self._groups)

    @property
    def group_results(self):
        """Result dictionary of failed, saved, not_saved, and submitted groups.

        Returns:
            (dictionary): Dictionary of group names for each status.
        """
        return self._group_results

    def indicator(self, indicator):
        """Add indicator data to TcEx job.

        This method will add indicator data to this TcEx job to be submitted via batch import.

        .. Warning:: There is no validation of the data passed to this method. Any duplicate
                     indicator will be skipped.

        **Example Data** *(required fields are highlighted)*

        .. code-block:: javascript
            :linenos:
            :lineno-start: 1
            :emphasize-lines: 14,19

            {
              'associatedGroup': [
                '1',
                '8'
              ],
              'attribute': [
                {
                  'type': 'Attribute Name',
                  'value': 'Description'
                }
              ],
              'confidence': 5,
              'rating': 3.2,
              'summary': '1.1.1.1',
              'tag': [
                {
                  'name': 'APT',
                },
                {
                  'name': 'CrimeWare',
                }
              ],
              'type': 'Address'
            }

        Args:
            indicator (dict | list): Dictionary or List containing indicator
                data.
        """
        if isinstance(indicator, dict):
            indicator = [indicator]

        for i in indicator:  # Not extending now since we need to build submitted list
            # verify indicator is not a duplicate before adding
            if i.get('summary') not in self._indicators:
                self._indicator_results['submitted'].append(i.get('summary'))
                self._indicators.append(i)

    @property
    def unprocessed_indicators(self):
        """Return indicators (unprocessed).

        Returns:
            (list): The list of unprocessed indicator.
        """
        return self._indicators

    @unprocessed_indicators.setter
    def unprocessed_indicators(self, value):
        """Set indicators list.

        Args:
            value (list): List of indicators

        """
        self._indicators = value

    @property
    def indicator_data(self):
        """Return the current indicator list.

        Returns:
            (list): The indicator list.
        """
        return self._indicators_response

    @property
    def indicator_len(self):
        """The current length of the indicator list.

        Returns:
            (integer): The length of the indicator list
        """
        return len(self._indicators)

    @property
    def indicator_results(self):
        """Result dictionary of failed, saved, not_saved, and submitted indicators.

        Returns:
            (dictionary): Dictionary of indicator values for each status.
        """
        return self._indicator_results

    def process(self, owner, indicator_batch=True, group_action='skip'):
        """Process all groups, indicator data, and associations.

        Process each of the supported data types for this job, in the following
        order (left to right):

            groups > indicators > file occurrences > group associations > associations

        Args:
            owner (string): The owner name for the data to be written.
            indicator_batch (bool): If true use the Batch Api otherwise use `/v2` REST API.
            group_action (string): The action to use on group create (duplicate, replace, skip).
        """
        if self._groups:
            self._tcex.log.info(u'Processing Groups')
            self._process_groups(owner, group_action.lower())

        if self._indicators:
            # update indicator data replacing group stub with group ids
            self._tcex.log.info(u'Processing Indicators')
            self._indicators_replace_stub(owner)
            self._process_indicators(owner, indicator_batch)

        if self._file_occurrences:
            self._tcex.log.info(u'Processing File Occurrences')
            self._process_file_occurrences(owner)

        if self._group_associations:
            self._tcex.log.info(u'Processing Group Associations')
            self._process_group_association(owner)

        if self._associations:
            self._tcex.log.info(u'Processing Associations')
            self._process_association(owner)
