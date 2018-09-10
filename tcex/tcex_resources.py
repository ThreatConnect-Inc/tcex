# -*- coding: utf-8 -*-
""" TcEx Framework Resource Module """
import copy
import gzip
import ipaddress
import json
import os
import re
import shutil
import uuid


class Resource(object):
    """Common settings for All ThreatConnect API Endpoints"""

    def __init__(self, tcex):
        """Initialize the Class properties.

        Args:
            tcex (object): Instance of TcEx.
        """
        self.tcex = tcex

        # request
        self._request = self.tcex.request(self.tcex.session)
        # set default. can be overwritten for individual requests.
        self._request.content_type = 'application/json'

        # common
        self._api_branch = None
        self._api_branch_base = None
        self._api_entity = None
        self._api_uri = None
        self._case_preference = 'sensitive'
        self._custom = False
        self._http_method = 'GET'
        self._filters = []
        self._filter_or = False
        self._name = None
        self._parsable = False
        self._paginate = True
        self._paginate_count = 0
        self._parent = None
        self._request_entity = None
        self._request_uri = None
        self._result_count = None
        self._result_limit = 500
        self._result_start = 0
        self._stream = False
        self._status_codes = {}
        self._value_fields = []

    def _apply_filters(self):
        """Apply any filters added to the resource.
        """
        # apply filters
        filters = []
        for f in self._filters:
            filters.append('{}{}{}'.format(f['name'], f['operator'], f['value']))
        self.tcex.log.debug(u'filters: {}'.format(filters))

        if filters:
            self._request.add_payload('filters', ','.join(filters))

    def _request_bulk(self, response):
        """
        """
        try:
            # write bulk download to disk with unique ID
            temp_file = os.path.join(self.tcex.default_args.tc_temp_path, '{}.json'.format(
                uuid.uuid4()))
            self.tcex.log.debug(u'temp json file: {}'.format(temp_file))
            with open(temp_file, 'wb') as fh:
                for block in response.iter_content(1024):
                    fh.write(block)
            with open(temp_file, 'r') as fh:
                data = json.load(fh)

            # remove temporary json file
            if self.tcex.default_args.logging == 'debug':
                try:
                    with open(temp_file, 'rb') as f_in, gzip.open(
                        '{}.gz'.format(temp_file), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                except Exception:
                    self.tcex.log.warning(u'Could not compress temporary bulk JSON file.')
            os.remove(temp_file)

        except IOError as e:
            self.tcex.handle_error(300, [e])

        return data

    def _request_process(self, response):
        """
        """
        data = []
        status = None

        if response.status_code in self._status_codes[self._http_method]:
            # Process all JSON type responses
            if response.status_code == 204:
                # 204 is a no data response
                data = None
                status = 'Success'
            elif response.headers['content-type'] == 'application/json':
                data, status = self._request_process_json(response)
            elif response.headers['content-type'] == 'application/octet-stream':
                data, status = self._request_process_octet(response)
            elif response.headers['content-type'] == 'text/plain':
                data, status = self._request_process_text(response)
            else:
                err = u'Failed Request: {}'.format(response.text)
                self.tcex.log.error(err)
        else:
            status = 'Failure'
            err = u'Failed Request {}: Status Code ({}) not in {}. API Response: "{}".'.format(
                self._name, response.status_code, self._status_codes[self._http_method],
                response.text)
            self.tcex.log.error(err)

        return data, status

    # def _request_process_failure(self):
    #     """
    #     """
    #     pass

    def _request_process_json(self, response):
        """Handle response data of type JSON

        Return:
            (string): The data from the download
            (string): The status of the download
        """
        data = []
        try:
            if self._api_branch == 'bulk':
                response_data = self._request_bulk(response)
            else:
                response_data = response.json()

            if self._request_entity is None:
                data = response_data
                status = 'Success'
            elif self._api_branch == 'bulk':
                data, status = self._request_process_json_bulk(response_data)
            elif response_data.get('data') is None:
                data, status = self._request_process_json_status(response_data)
            elif response_data.get('status') == 'Success':
                data, status = self._request_process_json_standard(response_data)

                # setup pagination
                if self._result_count is None:
                    self._result_count = response_data.get('data', {}).get('resultCount')
            else:
                self.tcex.log.error('Failed Request: {}'.format(response.text))
                status = 'Failure'
        except KeyError as e:
            # TODO: Remove try/except block
            status = 'Failure'
            msg = u'Error: Invalid key {}. [{}] '.format(e, self.request_entity)
            self.tcex.log.error(msg)
        except ValueError as e:
            # TODO: Remove try/except block
            status = 'Failure'
            msg = u'Error: ({})'.format(e)
            self.tcex.log.error(msg)

        return data, status

    def _request_process_json_bulk(self, response_data):
        """Handle bulk JSON response

        Return:
            (string): The response data
            (string): The response status
        """
        status = 'Failure'
        data = response_data.get(self.request_entity, [])
        if data:
            status = 'Success'
        return data, status

    def _request_process_json_standard(self, response_data):
        """Handle JSON response

        This should be the most common response from the ThreatConnect API.

        Return:
            (string): The response data
            (string): The response status
        """
        data = response_data.get('data', {}).get(self.request_entity, [])
        status = response_data.get('status', 'Failure')
        return data, status

    def _request_process_json_status(self, response_data):
        """Handle JSON response with no "data" entity

        Return:
            (string): The response data
            (string): The response status
        """
        # bcs - not sure about this one.  may need a better check for results
        #       that only returns {"status":"Success"}
        data = []
        status = response_data.get('status')
        return data, status

    def _request_process_octet(self, response):
        """Handle Document download.

        Return:
            (string): The data from the download
            (string): The status of the download
        """
        status = 'Failure'
        # Handle document download
        data = response.content
        if data:
            status = 'Success'

        return data, status

    def _request_process_text(self, response):
        """Handle Signature download.

        Return:
            (string): The data from the download
            (string): The status of the download
        """
        status = 'Failure'
        # Handle document download
        data = response.content
        if data:
            status = 'Success'

        return data, status

    def add_filter(self, name, operator, value):
        """Add ThreatConnect API Filter for this resource request.

        External Reference:
            https://docs.threatconnect.com

        Args:
            name (string): The filter field name.
            operator (string): The filter comparison operator.
            value (string): The filter value.
        """
        self._filters.append({
            'name': name,
            'operator': operator,
            'value': value
        })

    def add_payload(self, key, val, append=False):
        """Add a key value pair to payload for this request.

        .. Note:: For ``_search`` you can pass a search argument. (e.g. _search?summary=1.1.1.1).

        Args:
            key (string): The payload key
            val (string): The payload value
            append (bool): Indicate whether the value should be appended
        """
        self._request.add_payload(key, val, append)

    @property
    def api_branch(self):
        """The ThreatConnect API branch for this resource.

        Return:
            (str): The **addresses** endpoint from ``/v2/indicators/addresses/``.
        """
        return self._api_branch

    @property
    def api_branch_base(self):
        """The ThreatConnect API branch base (parent branch) for this resource.

        Return:
            (str): The **indicators** endpoint from ``/v2/indicators`` or
                   ``/v2/indicators/addresses``.
        """
        return self._api_branch_base

    @property
    def api_entity(self):
        """The ThreatConnect API entity for this resource.

        Return:
            (str): The **address** JSON entity from JSON response to ``/v2/indicators/addresses``.
        """
        return self._api_entity

    @property
    def api_uri(self):
        """The ThreatConnect API URI for this resource.

        Return:
            (string): The API URI endpoint ``/v2/indicators/addresses``.
        """
        return self._api_uri

    def association_custom(self, association_name, association_resource=None):
        """Custom Indicator association for this resource with resource value.

        **Example Endpoints URI's**

        +--------+--------------------------------------------------------------------------+
        | HTTP   | API Endpoint URI's                                                       |
        +========+==========================================================================+
        | {base} | /v2/indicators/{indicatorType}/{uniqueId}/associations/{associationName} |
        +--------+--------------------------------------------------------------------------+
        | GET    | {base}/indicators                                                        |
        +--------+--------------------------------------------------------------------------+
        | GET    | {base}/indicators/{indicatorType}                                        |
        +--------+--------------------------------------------------------------------------+
        | DELETE | {base}/indicators/{indicatorType}/{value}                                |
        +--------+--------------------------------------------------------------------------+
        | POST   | {base}/indicators/{indicatorType}/{value}                                |
        +--------+--------------------------------------------------------------------------+

        Args:
            association_name (string): The name of the custom association as defined in the UI.
            association_resource (object): An instance of Resource for an Indicator or sub type.
        """
        resource = self.copy()
        association_api_branch = self.tcex.indicator_associations_types_data.get(
            association_name, {}).get('apiBranch')
        if association_api_branch is None:
            self.tcex.handle_error(305, [association_name])

        # handle URL difference between Custom Associations and File Actions
        custom_type = 'associations'
        file_action = self.tcex.utils.to_bool(self.tcex.indicator_associations_types_data.get(
            association_name, {}).get('fileAction'))
        if file_action:
            custom_type = 'actions'

        resource._request_entity = 'indicator'
        if association_resource is not None:
            resource._request_uri = '{}/{}/{}/{}'.format(
                resource._request_uri, custom_type, association_api_branch,
                association_resource.request_uri)
        else:
            resource._request_uri = '{}/{}/{}/indicators'.format(
                resource._request_uri, custom_type, association_api_branch)
        return resource

    def association_pivot(self, association_resource):
        """Pivot point on association for this resource.

        This method will return all *resources* (group, indicators, task, victims, etc) for this
        resource that are associated with the provided resource.

        **Example Endpoints URI's**

        +---------+--------------------------------------------------------------------------------+
        | METHOD  | API Endpoint URI's                                                             |
        +=========+================================================================================+
        | GET     | /v2/groups/{pivot resourceType}/{pivot uniqueId}/{resourceType}                |
        +---------+--------------------------------------------------------------------------------+
        | GET     | /v2/groups/{pivot resourceType}/{pivot uniqueId}/{resourceType}/{uniqueId}     |
        +---------+--------------------------------------------------------------------------------+
        | POST    | /v2/groups/{pivot resourceType}/{pivot uniqueId}/{resourceType}/{uniqueId}     |
        +---------+--------------------------------------------------------------------------------+
        | GET     | /v2/indicators/{pivot resourceType}/{pivot uniqueId}/{resourceType}            |
        +---------+--------------------------------------------------------------------------------+
        | GET     | /v2/indicators/{pivot resourceType}/{pivot uniqueId}/{resourceType}/{uniqueId} |
        +---------+--------------------------------------------------------------------------------+
        | POST    | /v2/indicator/{pivot resourceType}/{pivot uniqueId}/{resourceType}/{uniqueId}  |
        +---------+--------------------------------------------------------------------------------+

        Args:
            resource_api_branch (string): The resource pivot api branch including resource id.
        """
        resource = self.copy()
        resource._request_uri = '{}/{}'.format(
            association_resource.request_uri, resource._request_uri)
        return resource

    def associations(self, association_resource):
        """Retrieve Association for this resource of the type in association_resource.

        This method will return all *resources* (group, indicators, task, victims, etc) for this
        resource that are associated with the provided association resource_type.

        **Example Endpoints URI's**

        +--------+----------------------------------------------------------------------+
        | Method | API Endpoint URI's                                                   |
        +========+======================================================================+
        | {base} | /v2/{resourceClass}/{resourceType}/{resourceId}                      |
        +--------+----------------------------------------------------------------------+
        | GET    | {base}/{assoc resourceClass}/{assoc resourceType}                    |
        +--------+----------------------------------------------------------------------+
        | POST   | {base}/{assoc resourceClass}/{assoc resourceType}/{assoc resourceId} |
        +--------+----------------------------------------------------------------------+
        | DELETE | {base}/{assoc resourceClass}/{assoc resourceType}/{assoc resourceId} |
        +--------+----------------------------------------------------------------------+

        + resourceClass - Groups/Indicators
        + resourceType - Adversary, Incident, etc / Address, EmailAddress, etc
        + resourceId - Group Id / Indicator Value

        Args:
            association_resource (Resource Instance): A resource object with optional resource_id.
        Return:
            (instance): A copy of this resource instance cleaned and updated for associations.
        """
        resource = self.copy()
        resource._request_entity = association_resource.api_entity
        resource._request_uri = '{}/{}'.format(
            resource._request_uri, association_resource.request_uri)
        return resource

    def attributes(self, resource_id=None):
        """Attribute endpoint for this resource with optional attribute id.

        This method will set the resource endpoint for working with Attributes.
        The HTTP GET method will return all attributes applied to this resource
        or if a resource id (attribute id) is provided it will return the
        provided attribute if exists on this resource. An attribute can be added
        to this resource using the HTTP POST method and passing a JSON body
        containing the attribute type and attribute value. Using the HTTP PUT
        method with a provided resource id an attribute can be updated. The
        HTTP DELETE method will remove the provided attribute from this
        resource.

        **Example Endpoints URI's**

        +--------------+--------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                           |
        +==============+==============================================================+
        | GET          | /v2/groups/{resourceType}/{uniqueId}/attributes              |
        +--------------+--------------------------------------------------------------+
        | GET          | /v2/groups/{resourceType}/{uniqueId}/attributes/{resourceId} |
        +--------------+--------------------------------------------------------------+
        | DELETE       | /v2/groups/{resourceType}/{uniqueId}/attributes/{resourceId} |
        +--------------+--------------------------------------------------------------+
        | POST         | /v2/groups/{resourceType}/{uniqueId}/attributes              |
        +--------------+--------------------------------------------------------------+
        | PUT          | /v2/groups/{resourceType}/{uniqueId}/attributes/{resourceId} |
        +--------------+--------------------------------------------------------------+

        Args:
            resource_id (Optional [string]): The resource id (attribute id).
        """
        resource = self.copy()
        resource._request_entity = 'attribute'
        resource._request_uri = '{}/attributes'.format(resource._request_uri)
        if resource_id is not None:
            resource._request_uri = '{}/{}'.format(resource._request_uri, resource_id)
        return resource

    # def authorization_method(self, method):
    #     """Method to create authorization header for this resource request.

    #     Args:
    #         method (method): The method to use to generate the authorization header(s).
    #     """
    #     self._authorization_method = method

    @property
    def body(self):
        """The body for this resource request.

        Return:
            (any): The HTTP request body.
        """
        return self._request.body

    @body.setter
    def body(self, data):
        """The POST/PUT body content for this resource request."""
        self._request.body = data

    @property
    def case_preference(self):
        """String value for Custom Indicators case preference

        Return:
            (string): Either lower, upper or case sensitive.
        """
        return self._case_preference

    @property
    def content_type(self):
        """The Content-Type header value for this resource request."""
        return self._request.content_type

    @content_type.setter
    def content_type(self, data):
        """The Content-Type header for this resource request."""
        self._request.content_type = data

    def copy_reset(self):
        """Reset values after instance has been copied"""
        # Reset settings
        self._filters = []
        self._filter_or = False
        self._paginate = True
        self._paginate_count = 0
        self._result_count = None
        self._result_limit = 500
        self._result_start = 0

    def copy(self):
        """Return a "clean" copy of this instance.

        Return:
            (instance): A clean copy of this instance.
        """
        resource = copy.copy(self)

        # workaround for bytes/str issue in Py3 with copy of instance
        # TypeError: a bytes-like object is required, not 'str' (ssl.py)
        resource._request = self.tcex.request(self.tcex.session)

        # reset properties of resource
        resource.copy_reset()

        # Preserve settings
        resource.http_method = self.http_method
        if self._request.payload.get('owner') is not None:
            resource.owner = self._request.payload.get('owner')

        # future bcs - these should not need to be reset. correct?
        # resource._request_entity = self._api_entity
        # resource._request_uri = self._api_uri
        return resource

    @property
    def custom(self):
        """Boolean value for Custom Indicators

        Return:
            (boolean): True if the Indicator is a Custom Type.
        """
        return self._custom

    def group_pivot(self, group_resource):
        """Pivot point on groups for this resource.

        This method will return all *resources* (indicators, tasks, victims, etc) for this resource
        that are associated with the provided resource id (indicator value).

        **Example Endpoints URI's**

        +--------+---------------------------------------------------------------------------------+
        | Method | API Endpoint URI's                                                              |
        +========+=================================================================================+
        | GET    | /v2/groups/{resourceType}/{resourceId}/indicators/{resourceType}                |
        +--------+---------------------------------------------------------------------------------+
        | GET    | /v2/groups/{resourceType}/{resourceId}/indicators/{resourceType}/{uniqueId}     |
        +--------+---------------------------------------------------------------------------------+
        | GET    | /v2/groups/{resourceType}/{resourceId}/tasks/                                   |
        +--------+---------------------------------------------------------------------------------+
        | GET    | /v2/groups/{resourceType}/{resourceId}/tasks/{uniqueId}                         |
        +--------+---------------------------------------------------------------------------------+
        | GET    | /v2/groups/{resourceType}/{resourceId}/victims/                                 |
        +--------+---------------------------------------------------------------------------------+
        | GET    | /v2/groups/{resourceType}/{resourceId}/victims/{uniqueId}                       |
        +--------+---------------------------------------------------------------------------------+

        Args:
            group_resource (Resource Instance): A resource object with optional resource_id.
        Return:
            (instance): A copy of this resource instance cleaned and updated for group associations.

        """
        resource = self.copy()
        resource._request_uri = '{}/{}'.format(group_resource.request_uri, resource._request_uri)
        return resource

    @property
    def http_method(self):
        """The HTTP Method for this resource request.

        Return:
            (string): The HTTP request method (GET, POST, etc.)
        """
        return self._request.http_method

    @http_method.setter
    def http_method(self, data):
        """The HTTP Method for this resource request."""
        data = data.upper()
        if data in ['DELETE', 'GET', 'POST', 'PUT']:
            self._request.http_method = data
            self._http_method = data

    def indicator_pivot(self, indicator_resource):
        """Pivot point on indicators for this resource.

        This method will return all *resources* (groups, tasks, victims, etc)
        for this resource that are associated with the provided resource id
        (indicator value).

        **Example Endpoints URI's**

        +--------+---------------------------------------------------------------------------------+
        | Method | API Endpoint URI's                                                              |
        +========+=================================================================================+
        | GET    | /v2/indicators/{resourceType}/{resourceId}/groups/{resourceType}                |
        +--------+---------------------------------------------------------------------------------+
        | GET    | /v2/indicators/{resourceType}/{resourceId}/groups/{resourceType}/{uniqueId}     |
        +--------+---------------------------------------------------------------------------------+
        | GET    | /v2/indicators/{resourceType}/{resourceId}/tasks/                               |
        +--------+---------------------------------------------------------------------------------+
        | GET    | /v2/indicators/{resourceType}/{resourceId}/tasks/{uniqueId}                     |
        +--------+---------------------------------------------------------------------------------+
        | GET    | /v2/indicators/{resourceType}/{resourceId}/victims/                             |
        +--------+---------------------------------------------------------------------------------+
        | GET    | /v2/indicators/{resourceType}/{resourceId}/victims/{uniqueId}                   |
        +--------+---------------------------------------------------------------------------------+

        Args:
            resource_type (string): The resource pivot resource type (indicator type).
            resource_id (integer): The resource pivot id (indicator value).
        """
        resource = self.copy()
        resource._request_uri = '{}/{}'.format(
            indicator_resource.request_uri, resource._request_uri)
        return resource

    @property
    def name(self):
        """The name value for this resource.

        Return:
            (str): The name of the Resource Type (e.g. Indicator, Task, etc.)
        """
        return self._name

    @property
    def owner(self):
        """The Owner payload value for this resource request.

        Return:
            (str): The ThreatConnect owner name set during request.
        """
        return self._request.payload.get('owner')

    @owner.setter
    def owner(self, data):
        """The Owner payload value for this resource request."""
        if data is not None:
            self._request.add_payload('owner', data)
        else:
            self.tcex.log.warn(u'Provided owner was invalid. ({})'.format(data))

    @property
    def parent(self):
        """The parent object name for this resource.

        Return:
            (str): The API endpoint parent value (e.g. Indicator for Address or Group
                   for Adversary.)
        """
        return self._parent

    def paginate(self):
        """Paginate results from ThreatConnect API

        .. Attention:: This method will be deprecated in a future release.

        Return:
            (dictionary): Resource Data
        """
        self.tcex.log.warning(u'Using deprecated method (paginate).')
        resources = []
        self._request.add_payload('resultStart', self._result_start)
        self._request.add_payload('resultLimit', self._result_limit)
        results = self.request()
        response = results.get('response')
        if results.get('status') == 'Success':
            data = response.json()['data']
            resources = data[self.request_entity]

            # set results count returned by first API call
            if data.get('resultCount') is not None:
                self._result_count = data.get('resultCount')
                # self._result_start = self._result_limit

            self.tcex.log.debug(u'Result Count: {}'.format(self._result_count))

            while True:
                if len(resources) >= self._result_count:
                    break
                self._result_start += self._result_limit
                self._request.add_payload('resultStart', self._result_start)
                results = self.request()
                resources.extend(results['data'])

            self.tcex.log.debug(u'Resource Count: {}'.format(len(resources)))

        return resources

    @property
    def parsable(self):
        """Boolean value for Custom Indicators parsable setting.

        Return:
            (boolean): True if the Custom Indicator is parsable.
        """
        return self._parsable

    def request(self):
        """Send the request to the API.

        This method will send the request to the API.  It will try to handle
        all the types of responses and provide the relevant data when possible.
        Some basic error detection and handling is implemented, but not all failure
        cases will get caught.

        Return:
            (dictionary): Response/Results data.
        """
        # self._request.authorization_method(self._authorization_method)
        self._request.url = '{}/v2/{}'.format(self.tcex.default_args.tc_api_path, self._request_uri)
        self._apply_filters()
        self.tcex.log.debug(u'Resource URL: ({})'.format(self._request.url))

        response = self._request.send(stream=self._stream)
        data, status = self._request_process(response)

        # # bcs - to reset or not to reset?
        # self._request.body = None
        # # self._request.reset_headers()
        # # self._request.reset_payload()
        # self._request_uri = self._api_uri
        # self._request_entity = self._api_entity

        return {
            'data': data,
            'response': response,
            'status': status
        }

    @property
    def request_entity(self):
        """The temporary entity name used for the request.

        The request entity starts as the resource api_entity and changes
        depending on the pivot resource. This value is reset after the
        *request()* method is called.

        Return:
            (str): The entity field in the API results data.
        """
        return self._request_entity

    @property
    def request_uri(self):
        """The temporary uri used for the request.

        The request uri starts as the resource api_uri and changes depending on
        the pivot resource. This value is reset after the *request()* method is
        called.

        Return:
            (str): The requests API URI.
        """
        return self._request_uri

    @property
    def result_count(self):
        """Boolean for API pagination when there are previous results to retrieve.

        Return:
            (int): The number of results a paginated API call will return.
        """
        return self._result_count

    @property
    def result_limit(self):
        """Return the ThreatConnect API query parameter for the number of results.

        Return:
            (int): The limit of results to return during pagination.
        """
        return self._result_limit

    @result_limit.setter
    def result_limit(self, limit):
        """Set the ThreatConnect API query parameter for the number of results.

        Args:
            limit (int): The limit of results to return during pagination.
        """
        self._result_limit = limit

    def security_label_pivot(self, security_label_resource):
        """Pivot point on security labels for this resource.

        This method will return all *resources* (group, indicators, task,
        victims, etc) for this resource that have the provided security
        label applied.

        **Example Endpoints URI's**

        +--------------+----------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                   |
        +==============+======================================================================+
        | GET          | /v2/securityLabels/{resourceId}/groups/{resourceType}                |
        +--------------+----------------------------------------------------------------------+
        | GET          | /v2/securityLabels/{resourceId}/groups/{resourceType}/{uniqueId}     |
        +--------------+----------------------------------------------------------------------+
        | GET          | /v2/securityLabels/{resourceId}/indicators/{resourceType}            |
        +--------------+----------------------------------------------------------------------+
        | GET          | /v2/securityLabels/{resourceId}/indicators/{resourceType}/{uniqueId} |
        +--------------+----------------------------------------------------------------------+

        Args:
            resource_id (string): The resource pivot id (security label name).
        """
        resource = self.copy()
        resource._request_uri = '{}/{}'.format(
            security_label_resource.request_uri, resource._request_uri)
        return resource

    def security_labels(self, resource_id=None):
        """Security Label endpoint for this resource with optional label name.

        This method will set the resource endpoint for working with Security
        Labels.  The HTTP GET method will return all security labels applied
        to this resource or if a resource id (security label name) is provided
        it will return the provided security label if it has been applied,
        which could be useful to verify a security label is applied.  The
        provided resource_id (security label name) can be applied to this
        resource using the HTTP POST method.  The HTTP DELETE method will
        remove the provided security label from this resource.

        **Example Endpoints URI's**

        +--------------+-----------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                        |
        +==============+===========================================================+
        | GET          | /v2/{resourceType}/{uniqueId}/securityLabels              |
        +--------------+-----------------------------------------------------------+
        | GET          | /v2/{resourceType}/{uniqueId}/securityLabels/{resourceId} |
        +--------------+-----------------------------------------------------------+
        | DELETE       | /v2/{resourceType}/{uniqueId}/securityLabels/{resourceId} |
        +--------------+-----------------------------------------------------------+
        | POST         | /v2/{resourceType}/{uniqueId}/securityLabels/{resourceId} |
        +--------------+-----------------------------------------------------------+

        Args:
            resource_id (Optional [string]): The resource id (security label name).
        """
        resource = self.copy()
        resource._request_entity = 'securityLabel'
        resource._request_uri = '{}/securityLabels'.format(resource._request_uri)
        if resource_id is not None:
            resource._request_uri = '{}/{}'.format(resource._request_uri, resource_id)
        return resource

    def tag_pivot(self, tag_resource):
        """Pivot point on tags for this resource.

        This method will return all *resources* (group, indicators, task,
        victims, etc) for this resource that have the provided tag applied.

        **Example Endpoints URI's**

        +--------------+------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                         |
        +==============+============================================================+
        | GET          | /v2/tags/{resourceId}/groups/{resourceType}                |
        +--------------+------------------------------------------------------------+
        | GET          | /v2/tags/{resourceId}/groups/{resourceType}/{uniqueId}     |
        +--------------+------------------------------------------------------------+
        | GET          | /v2/tags/{resourceId}/indicators/{resourceType}            |
        +--------------+------------------------------------------------------------+
        | GET          | /v2/tags/{resourceId}/indicators/{resourceType}/{uniqueId} |
        +--------------+------------------------------------------------------------+
        | POST         | /v2/tags/{resourceId}/groups/{resourceType}/{uniqueId}     |
        +--------------+------------------------------------------------------------+
        | POST         | /v2/tags/{resourceId}/indicators/{resourceType}/{uniqueId} |
        +--------------+------------------------------------------------------------+

        Args:
            resource_id (string): The resource pivot id (tag name).
        """
        resource = self.copy()
        resource._request_uri = '{}/{}'.format(tag_resource.request_uri, resource._request_uri)
        return resource

    def tags(self, resource_id=None):
        """Tag endpoint for this resource with optional tag name.

        This method will set the resource endpoint for working with Tags. The
        HTTP GET method will return all tags applied to this resource or if a
        resource id (tag name) is provided it will return the provided tag if
        it has been applied, which could be useful to verify a tag is applied.
        The provided resource_id (tag) can be applied to this resource using
        the HTTP POST method.  The HTTP DELETE method will remove the provided
        tag from this resource.

        **Example Endpoints URI's**

        +--------------+------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                         |
        +==============+============================================================+
        | GET          | /v2/groups/{resourceType}/{uniqueId}/tags                  |
        +--------------+------------------------------------------------------------+
        | GET          | /v2/groups/{resourceType}/{uniqueId}/tags/{resourceId}     |
        +--------------+------------------------------------------------------------+
        | GET          | /v2/indicators/{resourceType}/{uniqueId}/tags              |
        +--------------+------------------------------------------------------------+
        | GET          | /v2/indicators/{resourceType}/{uniqueId}/tags/{resourceId} |
        +--------------+------------------------------------------------------------+
        | DELETE       | /v2/groups/{resourceType}/{uniqueId}/tags/{resourceId}     |
        +--------------+------------------------------------------------------------+
        | DELETE       | /v2/indicators/{resourceType}/{uniqueId}/tags/{resourceId} |
        +--------------+------------------------------------------------------------+
        | POST         | /v2/groups/{resourceType}/{uniqueId}/tags/{resourceId}     |
        +--------------+------------------------------------------------------------+
        | POST         | /v2/indicators/{resourceType}/{uniqueId}/tags/{resourceId} |
        +--------------+------------------------------------------------------------+

        Args:
            resource_id (Optional [string]): The resource id (tag name).
        """
        resource = self.copy()
        resource._request_entity = 'tag'
        resource._request_uri = '{}/tags'.format(resource._request_uri)
        if resource_id is not None:
            resource._request_uri = '{}/{}'.format(
                resource._request_uri, self.tcex.safetag(resource_id))
        return resource

    def task_pivot(self, task_resource):
        """Pivot point on Tasks for this resource.

        This method will return all *resources* (group, indicators, victims,
        etc) for this resource that are associated with the provided task id.

        **Example Endpoints URI's**

        +--------------+-------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                          |
        +==============+=============================================================+
        | GET          | /v2/tasks/{resourceId}/groups/{resourceType}                |
        +--------------+-------------------------------------------------------------+
        | GET          | /v2/tasks/{resourceId}/groups/{resourceType}/{uniqueId}     |
        +--------------+-------------------------------------------------------------+
        | GET          | /v2/tasks/{resourceId}/indicators/{resourceType}            |
        +--------------+-------------------------------------------------------------+
        | GET          | /v2/tasks/{resourceId}/indicators/{resourceType}/{uniqueId} |
        +--------------+-------------------------------------------------------------+

        Args:
            resource_id (integer): The resource pivot id (task id).
        """
        resource = self.copy()
        resource._request_uri = '{}/{}'.format(
            task_resource.request_uri, resource._request_uri)
        return resource

    @property
    def value_fields(self):
        """The value fields for this resource.

        Returns:
            (list): The fields in the response JSON that have the key value (e.g. ['md5',
                   'sha1', 'sha256'] or ['ip']).
        """
        return self._value_fields

    def victims(self, victim_resource):
        """Pivot point on Victims for this resource.

        This method will return all *resources* (group, indicators, task,
        etc) for this resource that are associated with the provided victim id.

        **Example Endpoints URI's**

        +--------------+--------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                       |
        +==============+==========================================================================+
        | GET          | /v2/{resourceId}/groups/{resourceType}/{uniqueId}/victims                |
        +--------------+--------------------------------------------------------------------------+
        | GET          | /v2/{resourceId}/groups/{resourceType}/{uniqueId}/victims/{victimId}     |
        +--------------+--------------------------------------------------------------------------+
        | GET          | /v2/{resourceId}/indicators/{resourceType}/{uniqueId}/victims            |
        +--------------+--------------------------------------------------------------------------+
        | GET          | /v2/{resourceId}/indicators/{resourceType}/{uniqueId}/victims/{victimId} |
        +--------------+--------------------------------------------------------------------------+
        | DELETE       | /v2/{resourceId}/groups/{resourceType}/{uniqueId}/victims/{victimId}     |
        +--------------+--------------------------------------------------------------------------+
        | POST         | /v2/{resourceId}/groups/{resourceType}/{uniqueId}/victims/{victimId}     |
        +--------------+--------------------------------------------------------------------------+

        Args:
            resource_id (integer): The resource pivot id (victim id).
        """
        resource = self.copy()
        resource._request_entity = 'victim'
        resource._request_uri = '{}/{}'.format(
            resource._request_uri, victim_resource.request_uri)
        return resource

    def victim_pivot(self, victim_resource):
        """Pivot point on Victims for this resource.

        This method will return all *resources* (group, indicators, task,
        etc) for this resource that are associated with the provided victim id.

        **Example Endpoints URI's**

        +--------------+---------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                            |
        +==============+===============================================================+
        | GET          | /v2/victims/{resourceId}/groups/{resourceType}                |
        +--------------+---------------------------------------------------------------+
        | GET          | /v2/victims/{resourceId}/groups/{resourceType}/{uniqueId}     |
        +--------------+---------------------------------------------------------------+
        | GET          | /v2/victims/{resourceId}/indicators/{resourceType}            |
        +--------------+---------------------------------------------------------------+
        | GET          | /v2/victims/{resourceId}/indicators/{resourceType}/{uniqueId} |
        +--------------+---------------------------------------------------------------+

        Args:
            resource_id (integer): The resource pivot id (victim id).
        """
        resource = self.copy()
        resource._request_uri = '{}/{}'.format(
            victim_resource.request_uri, resource._request_uri)
        return resource

    def victim_assets(self, asset_type=None, asset_id=None):
        """Victim Asset endpoint for this resource with optional asset type.

        This method will set the resource endpoint for working with Victim Assets.
        The HTTP GET method will return all Victim Assets associated with this
        resource or if a asset type is provided it will return the provided asset
        type if it has been associated. The provided asset type can be associated
        to this resource using the HTTP POST method.  The HTTP DELETE method will
        remove the provided tag from this resource.

        **Example Endpoints URI's**

        +---------+--------------------------------------------------------------------------------+
        | Method  | API Endpoint URI's                                                             |
        +=========+================================================================================+
        | GET     | /v2/groups/{resourceType}/{uniqueId}/victimAssets                              |
        +---------+--------------------------------------------------------------------------------+
        | GET     | /v2/groups/{resourceType}/{uniqueId}/victimAssets/{assetType}                  |
        +---------+--------------------------------------------------------------------------------+
        | GET     | /v2/groups/{resourceType}/{uniqueId}/victimAssets/{assetType}/{resourceId}     |
        +---------+--------------------------------------------------------------------------------+
        | GET     | /v2/indicators/{resourceType}/{uniqueId}/victimAssets                          |
        +---------+--------------------------------------------------------------------------------+
        | GET     | /v2/indicators/{resourceType}/{uniqueId}/victimAssets/{assetType}              |
        +---------+--------------------------------------------------------------------------------+
        | GET     | /v2/indicators/{resourceType}/{uniqueId}/victimAssets/{assetType}/{resourceId} |
        +---------+--------------------------------------------------------------------------------+
        | GET     | /v2/victim/{uniqueId}/victimAssets/{assetType}                                 |
        +---------+--------------------------------------------------------------------------------+
        | GET     | /v2/victim/{uniqueId}/victimAssets/{assetType}/{resourceId}                    |
        +---------+--------------------------------------------------------------------------------+
        | DELETE  | /v2/groups/{resourceType}/{uniqueId}/victimAssets/{assetType}/{resourceId}     |
        +---------+--------------------------------------------------------------------------------+
        | POST    | /v2/groups/{resourceType}/{uniqueId}/victimAssets/{assetType}/{resourceId}     |
        +---------+--------------------------------------------------------------------------------+

        Args:
            asset_type (Optional [string]): The asset type.
            asset_id (Optional [string]): The asset id.
        """
        type_entity_map = {
            'emailAddresses': 'victimEmailAddress',
            'networkAccounts': 'victimNetworkAccount',
            'phoneNumbers': 'victimPhone',
            'socialNetworks': 'victimSocialNetwork',
            'webSites': 'victimWebSite'
        }
        resource = self.copy()
        resource._request_entity = 'victimAsset'
        resource._request_uri = '{}/victimAssets'.format(resource._request_uri)
        if asset_type is not None:
            resource._request_entity = type_entity_map.get(asset_type, 'victimAsset')
            resource._request_uri = '{}/{}'.format(
                resource._request_uri, asset_type)
            if asset_id is not None:
                resource._request_uri = '{}/{}'.format(
                    resource._request_uri, asset_id)
        return resource


    def __iter__(self):
        """Add iterator to Resource Object"""
        return self

    def __next__(self):
        """Add next interator to Resource Object"""
        if not self._paginate:
            # check to see if pagination is supported
            self._paginate = True  # reset so object can be reused
            raise StopIteration

        # some endpoints don't require a resultLimit
        self._request.add_payload('resultLimit', self._result_limit)
        if self._result_count is not None:
            # on an endpoint that support pagination the default resultStart is 0
            self._request.add_payload('resultStart', self._result_start)

        results = self.request()

        # endpoints that support pagination will set self._result_count
        if self._result_count is not None:
            self._result_start += self._result_limit
            self._paginate_count += len(results.get('data'))
            if self._paginate_count >= self._result_count:
                self._paginate = False

        else:
            self._paginate = False

        return results

    # define next after __next__ for Python 2
    next = __next__

    def __str__(self):
        """A printable string for this resource.

        Return:
            (str): A printable string with Class data.
        """
        # TODO: update to include resource specific data.
        printable_string = '\n{0!s:_^80}\n'.format('Resource')

        # body
        printable_string += '\n{0!s:40}\n'.format('Body')
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Body', self._request.body)

        # headers
        if self._request.headers:
            printable_string += '\n{0!s:40}\n'.format('Headers')
            for k, v in self._request.headers.items():
                printable_string += '  {0!s:<29}{1!s:<50}\n'.format(k, v)

        # payload
        if self._request.payload:
            printable_string += '\n{0!s:40}\n'.format('Payload')
            for k, v in self._request.payload.items():
                printable_string += '  {0!s:<29}{1!s:<50}\n'.format(k, v)

        return printable_string


#
# Batch
#


class Batch(Resource):
    """Batch Resource Class"""

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Batch, self).__init__(tcex)
        self._api_branch = 'batch'
        self._api_branch_base = self._api_branch  # only on parent
        self._api_entity = 'batchId'
        self._api_uri = self._api_branch
        self._name = 'Batch'
        self._parent = 'Batch'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._status_codes = {
            'DELETE': [200],
            'GET': [200],
            'POST': [200, 201],
            'PUT': [200]
        }
        # self._value_fields = ['summary']

    def batch_id(self, batch_id):
        """The ID of the batch job used to push data and/or retrieve status.

        Args:
            batch_id (integer): The id of the batch job.
        """
        self._request_uri = '{}/{}'.format(self._api_uri, batch_id)
        self._request_entity = 'batchStatus'

    def errors(self, batch_id):
        """Update the URI to retrieve errors for a batch job.

        Args:
            batch_id (integer): The id of the batch job.
        """
        self._request_uri = '{}/{}/errors'.format(self._api_uri, batch_id)


#
# Indicator
#


class Indicator(Resource):
    """Indicator Resource Class

    This resource class is the base for all indicators and will return
    indicators of all types.  For specific indicator types use the child
    class of the type required.  Custom indicator types are supported
    dynamically and are not defined here.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Indicator, self).__init__(tcex)
        self._api_branch = 'indicators'
        self._api_branch_base = self._api_branch  # only on parent
        self._api_entity = 'indicator'
        self._api_uri = self._api_branch
        self._name = 'Indicator'
        self._parent = 'Indicator'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._status_codes = {
            'DELETE': [200],
            'GET': [200],
            'POST': [200, 201],
            'PUT': [200]
        }
        self._value_fields = ['summary']

    def deleted(self):
        """Update the request URI to include the deleted endpoint.
        """
        self._request_uri = '{}/deleted'.format(self._request_uri)

    def entity_body(self, data):
        """Alias to :py:meth:`~tcex.tcex_resources.Indicator.indicator_body` method.

        Args:
            data (list): A list of appropriate indicators for the Indicator Type.

        Return:
            (dict): Dictionary containing the indicator part of the body.
        """
        return self.indicator_body(data)

    def false_positive(self):
        """Report indicator False Positive"""
        self._request_uri = '{}/falsePositive'.format(self._request_uri)

    def indicator(self, data):
        """Update the request URI to include the Indicator for specific indicator retrieval.

        Args:
            data (string): The indicator value
        """
        if self._name != 'Bulk' or self._name != 'Indicator':
            self._request_uri = '{}/{}'.format(
                self._api_uri, self.tcex.safe_indicator(data, 'ignore'))

    def indicator_body(self, indicators):
        """Generate the appropriate dictionary content for POST of a **single** indicator.

        For an Address indicator a list with a single IP Address and for File indicators a list of
        1 up to 3 hash values.  Custom indicators fields have to be in the correct order (e.g.
        field 1, field 2, field 3 as defined in the UI).

        Args:
            indicators (list): A list of appropriate indicators for the Indicator Type.

        Return:
            (dict): Dictionary containing the indicator part of the body.
        """
        body = {}
        for vf in self._value_fields:
            i = indicators.pop(0)
            if i:
                body[vf] = i

            if not indicators:
                break

        return body

    def indicators(self, indicator_data):
        """Generator for indicator values.

        Some indicator such as Files (hashes) and Custom Indicators can have multiple indicator
        values (e.g. md5, sha1, sha256). This method provides a generator to iterate over all
        indicator values.

        Both the **summary** field and the individual indicator fields (e.g. **md5**, **sha1**,
        **sha256**) are supported.

        For indicators that have only one value such as **ip** or **hostName** the generator will
        only return the one result.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            # the individual indicator JSON from the API
            for i in resource.indicators(indicator_data):
                print(i.get('type'))  # md5, sha1, sha256, etc
                print(i.get('value'))  # hash or custom indicator value

        .. Warning:: This method could break for custom indicators that have " : " in the value of
                     the indicator while using the summary field.

        .. Note:: For ``/v2/indicators`` and ``/v2/indicators/bulk/json`` API endpoints only one
                  hash is returned for a file Indicator even if there are multiple in the platform.
                  If all hashes are required the ``/v2/indicators/files`` or
                  ``/v2/indicators/files/<hash>`` endpoints will provide all hashes.

        Args:
            indicator_data (dict): The indicator dictionary.

        Returns:
            (dictionary): A dict containing the indicator type and value.
        """
        # indicator_list = []
        for indicator_field in self.value_fields:
            if indicator_field == 'summary':
                indicators = self.tcex.expand_indicators(indicator_data.get('summary'))
                if indicator_data.get('type') == 'File':
                    hash_patterns = {
                        'md5': re.compile(r'^([a-fA-F\d]{32})$'),
                        'sha1': re.compile(r'^([a-fA-F\d]{40})$'),
                        'sha256': re.compile(r'^([a-fA-F\d]{64})$')
                    }
                    for i in indicators:
                        if not i:
                            continue

                        i = i.strip()  # clean up badly formatted summary string
                        i_type = None
                        if hash_patterns['md5'].match(i):
                            i_type = 'md5'
                        elif hash_patterns['sha1'].match(i):
                            i_type = 'sha1'
                        elif hash_patterns['sha256'].match(i):
                            i_type = 'sha256'
                        else:
                            msg = u'Cannot determine hash type: "{}"'.format(
                                indicator_data.get('summary'))
                            self.tcex.log.warning(msg)

                        data = {
                            'type': i_type,
                            'value': i
                        }
                        yield data
                else:
                    resource = getattr(
                        self.tcex.resources, self.tcex.safe_rt(indicator_data.get('type')))(
                            self.tcex)
                    values = resource.value_fields

                    index = 0
                    for i in indicators:
                        if i is None:
                            continue

                        i = i.strip()  # clean up badly formatted summary string
                        # TODO: remove workaround for bug in indicatorTypes API endpoint
                        if len(values) - 1 < index:
                            break

                        data = {
                            'type': values[index],
                            'value': i
                        }
                        index += 1
                        yield data
            else:
                if indicator_data.get(indicator_field) is not None:
                    yield {
                        'type': indicator_field,
                        'value': indicator_data.get(indicator_field)
                    }

    def observations(self):
        """Report indicator observations"""
        self._request_entity = 'observation'
        self._request_uri = '{}/observations'.format(self._request_uri)

    def observation_count(self):
        """Retrieve indicator observation count"""
        self._request_entity = 'observationCount'
        self._request_uri = '{}/observationCount'.format(self._request_uri)

    def observed(self, date_observed=None):
        """Retrieve indicator observations count for top 10"""
        if self.name != 'Indicator':
            self.tcex.log.warning(u'Observed endpoint only available for "indicator" endpoint.')
        else:
            self._request_uri = '{}/observed'.format(self._request_uri)
            if date_observed is not None:
                self._request.add_payload('dateObserved', date_observed)

    def resource_id(self, data):
        """Alias for indicator method.

        The resource id for an indicator in this class is the indicator value and not
        the actual indicator id stored in ThreatConnect.

        Args:
            data (string): The indicator value.
        """
        self.indicator(data)

    def summary(self, indicator_data):
        """Return a summary value for any given indicator type."""
        summary = []
        for v in self._value_fields:
            summary.append(indicator_data.get(v, ''))
        return indicator_data.get('summary', ' : '.join(summary))


class Address(Indicator):
    """Address Resource Class

    This resource class will return indicators of type Address (ipv4 and/or
    ipv6). To filter on specific indicators use the **indicator** or **resource_id**
    methods provided in the parent Class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Address, self).__init__(tcex)
        self._api_branch = 'addresses'
        self._api_entity = 'address'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Address'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._value_fields = ['ip']

    def indicator(self, data):
        """Update the request URI to include the Indicator for specific indicator retrieval.

        Overload to handle formatting of ipv6 addresses

        Args:
            data (string): The indicator value
        """
        try:
            ip = ipaddress.ip_address(data)
        except ValueError:
            ip = ipaddress.ip_address(u'{}'.format(data))
        if ip.version == 6:
            data = ip.exploded
            sections = []
            # mangle perfectly good ipv6 address to match TC format
            for s in data.split(':'):
                if s == '0000':
                    s = '0'
                else:
                    s = s.lstrip('0')
                sections.append(s)
            data = ':'.join(sections)
        super(Address, self).indicator(data)


class Bulk(Indicator):
    """Bulk Resource Class

    This resource class will return bulk status or bulk indicators via the Bulk
    API endpoint.  The base URL will return a status of bulk generation (see
    example below), while the **/csv** and **/json** endpoints will return the
    indicator is the selected format.

    Base response::

        {
            "status": "Success",
            "data": {
                "bulkStatus": {
                    "name": "Acme Corp",
                    "csvEnabled": false,
                    "jsonEnabled": true,
                    "nextRun": "2016-12-07T00:00:00Z",
                    "lastRun": "2016-12-06T00:04:33Z",
                    "status": "Complete"
                }
            }
        }
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Bulk, self).__init__(tcex)
        self._api_branch = 'bulk'
        self._api_entity = 'bulkStatus'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Indicator'  # bcs - should this be bulk?
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._value_fields = ['summary']

    def csv(self, ondemand=False):
        """Update request URI to return CSV data.

        For onDemand bulk generation to work it must first be enabled in the
        ThreatConnect platform under System settings.

        Args:
            ondemand (boolean): Enable on demand bulk generation.
        """
        self._request_uri = '{}/{}'.format(self._api_uri, 'csv')
        self._stream = True
        if ondemand:
            self._request.add_payload('runNow', True)

    def json(self, ondemand=False):
        """Update request URI to return JSON data.

        For onDemand bulk generation to work it must first be enabled in the
        ThreatConnect platform under System settings.

        Args:
            ondemand (boolean): Enable on demand bulk generation.
        """
        self._request_entity = 'indicator'
        self._request_uri = '{}/{}'.format(self._api_uri, 'json')
        self._stream = True
        if ondemand:
            self._request.add_payload('runNow', True)


class EmailAddress(Indicator):
    """EmailAddress Resource Class

    This resource class will return indicators of type Email. To filter on
    specific indicators use the **indicator** or **resource_id** methods provided
    in the parent Class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(EmailAddress, self).__init__(tcex)
        self._api_branch = 'emailAddresses'
        self._api_entity = 'emailAddress'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'EmailAddress'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._value_fields = ['address']


class File(Indicator):
    """File Resource Class

    This resource class will return indicators of type File (e.g md5, sha1,
    sha256). To filter on specific indicators use the **indicator** or
    **resource_id** methods provided in the parent Class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(File, self).__init__(tcex)
        self._api_branch = 'files'
        self._api_entity = 'file'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'File'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._value_fields = ['md5', 'sha1', 'sha256']

    def file_action(self, action_name, association_resource=None):
        """File action pivot for this resource.

        **Example Endpoints URI's**

        +--------+---------------------------------------------------------------------------------+
        | Method | API Endpoint URI's                                                              |
        +========+=================================================================================+
        | {base} | /v2/indicators/files/{uniqueId}/actions/{actionName}                            |
        +--------+---------------------------------------------------------------------------------+
        | GET    | {base}/indicators                                                               |
        +--------+---------------------------------------------------------------------------------+
        | GET    | {base}/indicators/{type}                                                        |
        +--------+---------------------------------------------------------------------------------+
        | DELETE | {base}/indicators/{type}/indicator                                              |
        +--------+---------------------------------------------------------------------------------+
        | POST   | {base}/indicators/{type}/indicator                                              |
        +--------+---------------------------------------------------------------------------------+

        +-------------------+------------------+-------------------------------------+
        | Name              | API Branch       | Indicator Type Associated with File |
        +===================+==================+=====================================+
        | File Archive      | ``/archive``     | File                                |
        +-------------------+------------------+-------------------------------------+
        | File Drop         | ``/drop``        | File                                |
        +-------------------+------------------+-------------------------------------+
        | File Traffic      | ``/traffic``     | Address, Host, URL                  |
        +-------------------+------------------+-------------------------------------+
        | File Mutex        | ``/mutex``       | Mutex                               |
        +-------------------+------------------+-------------------------------------+
        | File Registry Key | ``/registryKey`` | Registry Key                        |
        +-------------------+------------------+-------------------------------------+
        | File User Agent   | ``/userAgent``   | User Agent                          |
        +-------------------+------------------+-------------------------------------+
        | File DNS Query    | ``/dnsQuery``    | Host                                |
        +-------------------+------------------+-------------------------------------+

        Args:
            action_name (string): The name of the action as defined by ThreatConnect.
            association_resource (object): An instance of Resource for an Indicator or sub type.
        """
        self.association_custom(action_name, association_resource)

    @staticmethod
    def get_first_hash(hash_string):
        """Return first non None hash from string.

        md5 : sha1 : sha256

        Args:
            hash_string: (string): The string with delimited hash values.
        """
        for hs in hash_string.split(' : '):
            if hs:
                return hs

    def indicator(self, data):
        """Update the request URI to include the Indicator for specific indicator retrieval.

        Args:
            data (string): The indicator value
        """
        # handle hashes in form md5 : sha1 : sha256
        data = self.get_first_hash(data)
        super(File, self).indicator(data)

    @staticmethod
    def indicator_body(indicators):
        """Generate the appropriate dictionary content for POST of an File indicator

        Args:
            indicators (list): A list of one or more hash value(s).
        """
        hash_patterns = {
            'md5': re.compile(r'^([a-fA-F\d]{32})$'),
            'sha1': re.compile(r'^([a-fA-F\d]{40})$'),
            'sha256': re.compile(r'^([a-fA-F\d]{64})$')
        }
        body = {}
        for indicator in indicators:
            if indicator is None:
                continue

            if hash_patterns['md5'].match(indicator):
                body['md5'] = indicator
            elif hash_patterns['sha1'].match(indicator):
                body['sha1'] = indicator
            elif hash_patterns['sha256'].match(indicator):
                body['sha256'] = indicator

        return body

    def occurrence(self, indicator=None):
        """Update the URI to retrieve file occurrences for the provided indicator.

        Args:
            indicator (string): The indicator to retrieve file occurrences.
        """
        self._request_entity = 'fileOccurrence'
        self._request_uri = '{}/fileOccurrences'.format(self._request_uri)
        if indicator is not None:
            self._request_uri = '{}/{}/fileOccurrences'.format(self._api_uri, indicator)

    def summary(self, indicator_data):
        """Return a summary value for any given indicator type."""
        summary = None
        for v in self._value_fields:
            if indicator_data.get(v) is not None:
                summary = indicator_data.get(v)
                break
        return indicator_data.get('summary', summary)


class Host(Indicator):
    """Host Resource Class

    This resource class will return indicators of type Host. To filter on
    specific indicators use the **indicator** or **resource_id** methods provided
    in the parent Class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Host, self).__init__(tcex)
        self._api_branch = 'hosts'
        self._api_entity = 'host'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Host'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._value_fields = ['hostName']

    def resolution(self, indicator=None):
        """Update the URI to retrieve host resolutions for the provided indicator.

        Args:
            indicator (string): The indicator to retrieve resolutions.
        """
        self._request_entity = 'dnsResolution'
        self._request_uri = '{}/dnsResolutions'.format(self._request_uri)
        if indicator is not None:
            self._request_uri = '{}/{}/dnsResolutions'.format(self._api_uri, indicator)


class URL(Indicator):
    """URL Resource Class

    This resource class will return indicators of type URL. To filter on
    specific indicators use the **indicator** or **resource_id** methods provided
    in the parent Class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(URL, self).__init__(tcex)
        self._api_branch = 'urls'
        self._api_entity = 'url'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'URL'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._value_fields = ['text']


#
# Group
#


class Group(Resource):
    """Group Resource Class

    This resource class is the base for all groups and will return groups of
    all types.  For specific group types use the child class of the type
    required.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Group, self).__init__(tcex)
        self._api_branch = 'groups'
        self._api_branch_base = self._api_branch
        self._api_entity = 'group'
        self._api_uri = self._api_branch
        self._name = 'Group'
        self._parent = 'Group'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._status_codes = {
            'DELETE': [200],
            'GET': [200],
            'POST': [200, 201],
            'PUT': [200, 201]
        }
        self._value_fields = ['name']

    def group_id(self, resource_id):
        """Update the request URI to include the Group ID for specific group retrieval.

        Args:
            resource_id (string): The group id.
        """
        if self._name != 'group':
            self._request_uri = '{}/{}'.format(self._api_uri, resource_id)

    def resource_id(self, resource_id):
        """Alias for group_id method

        Args:
            resource_id (string): The group id.
        """
        self.group_id(resource_id)


class Adversary(Group):
    """Adversary Resource Class

    This resource class will return groups of type Adversary. To filter on
    specific groups use the **group_id** or **resource_id** methods provided in
    the parent class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Adversary, self).__init__(tcex)
        self._api_branch = 'adversaries'
        self._api_entity = 'adversary'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Adversary'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri


class Campaign(Group):
    """Campaign Resource Class

    This resource class will return groups of type Campaign. To filter on
    specific groups use the **group_id** or **resource_id** methods provided in
    the parent class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Campaign, self).__init__(tcex)
        self._api_branch = 'campaigns'
        self._api_entity = 'campaign'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Campaign'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri


class Document(Group):
    """Document Resource Class

    This resource class will return groups of type Document. To filter on
    specific groups use the **group_id** or **resource_id** methods provided in
    the parent class.
    """

    def __init__(self, tcex):
        """Initialize default class values.

        Args:
            tcex (instance): Instance of TcEx Class.
        """
        super(Document, self).__init__(tcex)
        self._api_branch = 'documents'
        self._api_entity = 'document'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Document'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri

    def download(self, resource_id):
        """Update the request URI to download the document for this resource.

        Args:
            resource_id (integer): The group id.
        """
        self.resource_id(str(resource_id))
        self._request_uri = '{}/download'.format(self._request_uri)

    def upload(self, resource_id, data):
        """Update the request URI to upload the a document to this resource.

        Args:
            resource_id (integer): The group id.
            data (any): The raw data to upload.
        """
        self.body = data
        self.content_type = 'application/octet-stream'
        self.resource_id(str(resource_id))
        self._request_uri = '{}/upload'.format(self._request_uri)


class Email(Group):
    """Email Resource Class

    This resource class will return groups of type Email. To filter on
    specific groups use the **group_id** or **resource_id** methods provided in
    the parent class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Email, self).__init__(tcex)
        self._api_branch = 'emails'
        self._api_entity = 'email'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Email'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri


class Event(Group):
    """Event Resource Class

    This resource class will return groups of type Event. To filter on
    specific groups use the **group_id** or **resource_id** methods provided in
    the parent class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Event, self).__init__(tcex)
        self._api_branch = 'events'
        self._api_entity = 'event'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Event'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri


class Incident(Group):
    """Incident Resource Class

    This resource class will return groups of type Incident. To filter on
    specific groups use the **group_id** or **resource_id** methods provided in
    the parent class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Incident, self).__init__(tcex)
        self._api_branch = 'incidents'
        self._api_entity = 'incident'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Incident'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri

    def event_date(self, date):
        """Incident Event Date.

        .. Attention:: Not implemented at this time

        Args:
            date: The event date in ISO 8601 format.
        """
        pass


class Intrusion_Set(Group):
    """Intrusion Set Resource Class

    This resource class will return groups of type Intrusion Set. To filter on
    specific groups use the **group_id** or **resource_id** methods provided in
    the parent class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Intrusion_Set, self).__init__(tcex)
        self._api_branch = 'intrusionSets'
        self._api_entity = 'intrusionSet'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Intrusion Set'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri


class Report(Group):
    """Report Resource Class

    This resource class will return groups of type Report. To filter on
    specific groups use the **group_id** or **resource_id** methods provided in
    the parent class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Report, self).__init__(tcex)
        self._api_branch = 'reports'
        self._api_entity = 'report'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Report'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri

    def download(self, resource_id):
        """Update the request URI to download the report for this resource.

        Args:
            resource_id (integer): The group id.
        """
        self.resource_id(str(resource_id))
        self._request_uri = '{}/download'.format(self._request_uri)

    def upload(self, resource_id, data):
        """Update the request URI to upload the a report to this resource.

        Args:
            resource_id (integer): The group id.
            data (any): The raw data to upload.
        """
        self.body = data
        self.content_type = 'application/octet-stream'
        self.resource_id(str(resource_id))
        self._request_uri = '{}/upload'.format(self._request_uri)


class Signature(Group):
    """Signature Resource Class

    This resource class will return groups of type Signature. To filter on
    specific groups use the **group_id** or **resource_id** methods provided in
    the parent class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Signature, self).__init__(tcex)
        self._api_branch = 'signatures'
        self._api_entity = 'signature'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Signature'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri

    def download(self, resource_id):
        """Update the request URI to download the document for this resource.

        Args:
            resource_id (integer): The group id.
        """
        self.resource_id(str(resource_id))
        self._request_uri = '{}/download'.format(self._request_uri)


class Threat(Group):
    """Threat Resource Class

    This resource class will return groups of type Threat. To filter on
    specific groups use the **group_id** or **resource_id** methods provided in
    the parent class.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Threat, self).__init__(tcex)
        self._api_branch = 'threats'
        self._api_entity = 'threat'
        self._api_uri = '{}/{}'.format(self._api_branch_base, self._api_branch)
        self._name = 'Threat'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri


#
# Custom Metric
#


class CustomMetric(Resource):
    """Custom Metric Class

    +--------------+----------------------------------+
    | HTTP Method  | API Endpoint URI's               |
    +==============+==================================+
    | GET          | /v2/customMetrics                |
    +--------------+----------------------------------+
    | POST         | /v2/customMetrics                |
    +--------------+----------------------------------+

    .. code-block:: javascript

        {
          "name": "My Custom Metric",
          "dataType": "Sum",
          "interval": "Hourly",
          "keyedValues": true,
          "description": "A sum of all occurrences per Indicator Source"
        }

    This resource class will return or create custom metrics.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(CustomMetric, self).__init__(tcex)
        self._api_branch = 'customMetrics'
        self._api_entity = 'customMetricConfig'
        self._api_uri = self._api_branch
        self._name = 'CustomerMetric'
        self._parent = 'CustomerMetric'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._status_codes = {
            'GET': [200],
            'POST': [200, 201, 204],
            'PUT': [200]
        }
        self._value_fields = ['customMetricConfig']

    def metric_id(self, resource_id):
        """Update the request URI to include the Metric Id for specific retrieval.

        +--------------+----------------------------------+
        | HTTP Method  | API Endpoint URI's               |
        +==============+==================================+
        | GET          | /v2/customMetrics/{id}           |
        +--------------+----------------------------------+
        | PUT          | /v2/customMetrics/{id}           |
        +--------------+----------------------------------+

        Args:
            resource_id (string): The metric id.
        """
        self._request_uri = '{}/{}'.format(self._request_uri, resource_id)

    def metric_name(self, resource_name):
        """Update the request URI to include the Metric Name for specific retrieval.

        +--------------+----------------------------------+
        | HTTP Method  | API Endpoint URI's               |
        +==============+==================================+
        | GET          | /v2/customMetrics/{name}         |
        +--------------+----------------------------------+
        | PUT          | /v2/customMetrics/{name}         |
        +--------------+----------------------------------+

        Args:
            resource_name (string): The metric name.
        """
        self._request_uri = '{}/{}'.format(self._request_uri, resource_name)

    def resource_id(self, resource_id):
        """Alias for metric_id method

        Args:
            resource_id (string): The metric id.
        """
        self.metric_id(resource_id)

    def resource_name(self, resource_name):
        """Alias for metric_name method

        Args:
            resource_name (string): The metric name.
        """
        self.metric_name(resource_name)

    def data(self, resource_value, return_value=False):
        """Alias for metric_name method

        +--------------+------------------------------------+
        | HTTP Method  | API Endpoint URI's                 |
        +==============+====================================+
        | POST         | /v2/customMetrics/{id}|{name}/data |
        +--------------+------------------------------------+

        Example
        -------

        The weight value is optional.

        .. code-block:: javascript

            {
              "value": 1,
              "weight": 1,
            }

        **Keyed Example**

        The weight value is optional.

        .. code-block:: javascript

            {
              "value": 1,
              "weight": 1,
              "name": "src1"
            }

        Args:
            resource_name (string): The metric name.
        """
        if return_value:
            self._request_entity = None
            self._request.add_payload('returnValue', True)
        self._request_uri = '{}/{}/data'.format(self._request_uri, resource_value)


#
# Owner
#


class Owner(Resource):
    """Owner Class

    This resource class will return Owners.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Owner, self).__init__(tcex)
        self._api_branch = 'owners'
        self._api_entity = 'owner'
        self._api_uri = self._api_branch
        self._name = 'Owner'
        self._parent = 'Owner'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._status_codes = {
            'GET': [200]
        }
        self._value_fields = ['name']

    def owner_id(self, resource_id):
        """Update the request URI to include the Owner Id for specific retrieval.

        Args:
            resource_id (string): The owner id.
        """
        self._request_uri = '{}/{}'.format(self._request_uri, resource_id)

    def resource_id(self, resource_id):
        """Alias for owner_id method

        Args:
            resource_id (string): The owner id.
        """
        self.owner_id(resource_id)


#
# Security Label
#


class SecurityLabel(Resource):
    """Security Label Class

    This resource class will return Security Labels.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(SecurityLabel, self).__init__(tcex)
        self._api_branch = 'securityLabels'
        self._api_entity = 'securityLabel'
        self._api_uri = self._api_branch
        self._name = 'SecurityLabel'
        self._parent = 'SecurityLabel'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._status_codes = {
            'DELETE': [200],
            'GET': [200],
            'POST': [200],
            'PUT': [200]
        }
        self._value_fields = ['name']

    def label(self, resource_id):
        """Update the request URI to include the Security Label for specific retrieval.

        Args:
            resource_id (string): The security label.
        """
        self._request_uri = '{}/{}'.format(self._request_uri, resource_id)

    def resource_id(self, resource_id):
        """Alias for label method

        The resource id is the security label name.

        Args:
            resource_id (string): The security label.
        """
        self.label(resource_id)


#
# Tag
#


class Tag(Resource):
    """Tag Class

    This resource class will return Tags.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Tag, self).__init__(tcex)
        self._api_branch = 'tags'
        self._api_entity = 'tag'
        self._api_uri = self._api_branch
        self._name = 'Tag'
        self._parent = 'Tag'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._status_codes = {
            'DELETE': [200],
            'GET': [200],
            'POST': [200],
            'PUT': [200]
        }
        self._value_fields = ['name']

    def tag(self, resource_id):
        """Update the request URI to include the Tag for specific retrieval.

        Args:
            resource_id (string): The tag name.
        """
        self._request_uri = '{}/{}'.format(self._request_uri, self.tcex.safetag(resource_id))

    def resource_id(self, resource_id):
        """Alias for tag

        The resource id is the tag name.

        Args:
            resource_id (string): The tag name.
        """
        self.tag(resource_id)


#
# Task
#


class Task(Resource):
    """Task Class

    This resource class will return Tasks.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Task, self).__init__(tcex)
        self._api_branch = 'tasks'
        self._api_entity = 'task'
        self._api_uri = self._api_branch
        self._name = 'Task'
        self._parent = 'Task'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._status_codes = {
            'DELETE': [200],
            'GET': [200],
            'POST': [200, 201],
            'PUT': [200]
        }
        self._value_fields = ['name']

    def assignees(self, assignee=None, resource_id=None):
        """Add an assignee to a Task

        GET: /v2/tasks/{uniqueId}/assignees
        GET: /v2/tasks/{uniqueId}/assignees/{assigneeId}
        POST: /v2/tasks/{uniqueId}/assignees/{assigneeId}
        DELETE: /v2/tasks/{uniqueId}/assignees/{assigneeId}

        Args:
            assignee (Optional [string]): The assignee name.
            resource_id (Optional [string]): The task ID.
        """
        if resource_id is not None:
            self.resource_id(resource_id)
        self._request_uri = '{}/assignees'.format(self._request_uri)
        if assignee is not None:
            self._request_uri = '{}/{}'.format(self._request_uri, assignee)

    def escalatees(self, escalatee=None, resource_id=None):
        """Add an escalatee to a Task

        GET: /v2/tasks/{uniqueId}/escalatees
        GET: /v2/tasks/{uniqueId}/escalatees/{escalateeId}
        POST: /v2/tasks/{uniqueId}/escalatees/{escalateeId}
        DELETE: /v2/tasks/{uniqueId}/escalatees/{escalateeId}

        Args:
            escalatee (Optional [string]): The escalatee name.
            resource_id (Optional [string]): The task ID.
        """
        if resource_id is not None:
            self.resource_id(resource_id)
        self._request_uri = '{}/escalatees'.format(self._request_uri)
        if escalatee is not None:
            self._request_uri = '{}/{}'.format(self._request_uri, escalatee)

    def task_id(self, resource_id):
        """Update the request URI to include the Task Id for specific retrieval.

        Args:
            resource_id (string): The task id.
        """
        self._request_uri = '{}/{}'.format(self._request_uri, resource_id)

    def resource_id(self, resource_id):
        """Alias for task_id method

        The resource id is the task id.

        Args:
            resource_id (string): The task id.
        """
        self.task_id(resource_id)


#
# Victim
#


class Victim(Resource):
    """Victim Class

    This resource class will return Victims.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Victim, self).__init__(tcex)
        self._api_branch = 'victims'
        self._api_entity = 'victim'
        self._api_uri = self._api_branch
        self._name = 'Victim'
        self._parent = 'Victim'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._status_codes = {
            'DELETE': [200],
            'GET': [200],
            'POST': [200, 201],
            'PUT': [200]
        }
        self._value_fields = ['name']

    def victim_id(self, resource_id):
        """Update the request URI to include the Victim Id for specific retrieval.

        Args:
            resource_id (string): The victim id.
        """
        self._request_uri = '{}/{}'.format(self._request_uri, resource_id)

    def resource_id(self, resource_id):
        """Alias for victim_id method

        The resource id is the victim id.

        Args:
            resource_id (string): The victim id.
        """
        self.victim_id(resource_id)


#
# DataStore
#


class DataStore(object):
    """DataStore Class

    This resource class will return DataStore.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        self.tcex = tcex
        self._params = {}

    def _request(self, domain, type_name, search_command, db_method, body=None):
        """Make the API request for a Data Store CRUD operation

        Args:
            domain (string): One of 'local', 'organization', or 'system'.
            type_name (string): This is a free form index type name. The ThreatConnect API will use
                                this resource verbatim.
            search_command (string): Search command to pass to ES.
            db_method (string): The DB method 'DELETE', 'GET', 'POST', or 'PUT'
            body (dict): JSON body
        """
        headers = {
            'Content-Type': 'application/json',
            'DB-Method': db_method
        }
        url = '/v2/exchange/db/{}/{}/{}'.format(domain, type_name, search_command)
        r = self.tcex.session.post(url, data=body, headers=headers, params=self._params)

        data = []
        status = 'Failed'
        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            self.tcex.handle_error(350, [r.status_code, r.text])
        data = r.json()
        status = 'Success'

        return {
            'data': data,
            'response': r,
            'status': status
        }

    def add_payload(self, key, val, append=True):
        """Add a key value pair to payload for this request.

        .. Note:: For ``_search`` you can pass a search argument. (e.g. _search?summary=1.1.1.1).

        Args:
            key (string): The payload key
            val (string): The payload value
            append (bool): Indicates whether the value should be appended or overwritten.
        """
        if append:
            self._params.setdefault(key, []).append(val)
        else:
            self._params[key] = val

    def create(self, domain, type_name, search_command, body):
        """Create entry in ThreatConnect Data Store

        Args:
            domain (string): One of 'local', 'organization', or 'system'.
            type_name (string): This is a free form index type name. The ThreatConnect API will use
                this resource verbatim.
            search_command (string): Search command to pass to ES.
            body (str): JSON serialized data.
        """
        return self._request(domain, type_name, search_command, 'POST', body)

    def delete(self, domain, type_name, search_command):
        """Delete entry in ThreatConnect Data Store

        Args:
            domain (string): One of 'local', 'organization', or 'system'.
            type_name (string): This is a free form index type name. The ThreatConnect API will use
                this resource verbatim.
            search_command (string): Search command to pass to ES.
        """
        return self._request(domain, type_name, search_command, 'DELETE', None)

    def read(self, domain, type_name, search_command, body=None):
        """Read entry in ThreatConnect Data Store

        Args:
            domain (string): One of 'local', 'organization', or 'system'.
            type_name (string): This is a free form index type name. The ThreatConnect API will use
                this resource verbatim.
            search_command (string): Search command to pass to ES.
            body (str): JSON body
        """
        return self._request(domain, type_name, search_command, 'GET', body)

    def update(self, domain, type_name, search_command, body):
        """Update entry in ThreatConnect Data Store

        Args:
            domain (string): One of 'local', 'organization', or 'system'.
            type_name (string): This is a free form index type name. The ThreatConnect API will use
                this resource verbatim.
            search_command (string): Search command to pass to ES.
            body (str): JSON body
        """
        return self._request(domain, type_name, search_command, 'PUT', body)


#
# Notification
#


class Notification(Resource):
    """Custom Notification Class

    +--------------+----------------------------------+
    | HTTP Method  | API Endpoint URI's               |
    +==============+==================================+
    | POST         | /v2/notifications                |
    +--------------+----------------------------------+

    .. code-block:: javascript

        {
            "notificationType": "App Success",
            "priority": "High",
            "message": "App worked just fine.",
            "isOrganization": false,
            "recipients": "opsTeam@threatconnect.com"
        }

    This resource class will create notifications.
    """

    def __init__(self, tcex):
        """Initialize default class values."""
        super(Notification, self).__init__(tcex)
        self._api_branch = 'notifications'
        self._api_entity = 'notificationsConfig'
        self._api_uri = self._api_branch
        self._name = 'Notification'
        self._parent = 'Notification'
        self._request_entity = self._api_entity
        self._request_uri = self._api_uri
        self._status_codes = {
            'POST': [200]
        }
        self._value_fields = ['notificationsConfig']


#
# Class Factory
#


def class_factory(name, base_class, class_dict):
    """Internal method for dynamically building Custom Indicator classes."""

    def __init__(self, tcex):
        base_class.__init__(self, tcex)
        for k, v in class_dict.items():
            setattr(self, k, v)

    newclass = type(str(name), (base_class,), {"__init__": __init__})
    return newclass
