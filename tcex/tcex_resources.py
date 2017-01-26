""" standard """
import json
import os
import uuid

""" third party """
""" custom """


class Resource(object):
    """Common settings for All ThreatConnect API Endpoints"""

    def __init__(self, tcex):
        """Initialize default class values."""
        self._tcex = tcex

        # request
        self._r = tcex.request
        if tcex._args.tc_proxy_tc:
            self._r.proxies = tcex.proxies

        # common
        self._api_branch = None
        self._api_branch_base = None
        self._api_entity = None
        self._api_uri = None
        self._authorization_method = self._tcex.authorization
        self._http_method = 'GET'
        self._filters = []
        self._filter_or = False
        self._name = None
        self._pivot = False
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
        self._url = None
        self._value_fields = []

    def _apply_filters(self):
        """
        """
        # apply filters
        filters = []
        for f in self._filters:
            filters.append('{}{}{}'.format(f['name'], f['operator'], f['value']))
        self._tcex.log.debug('filters: {}'.format(filters))

        if len(filters) > 0:
            self._r.add_payload('filters', ','.join(filters))

    def _request_bulk(self, response):
        """
        """
        try:
            # write bulk download to disk with unique ID
            temp_file = os.path.join(self._tcex._args.tc_temp_path, '{}.json'.format(uuid.uuid4()))
            self._tcex.log.debug('temp json file: {}'.format(temp_file))
            with open(temp_file, 'wb') as fh:
                for block in response.iter_content(1024):
                    fh.write(block)
            with open(temp_file, 'r') as fh:
                data = json.load(fh)
        except IOError as e:
            err = 'Failed retrieving Bulk JSON ({}).'.format(e)
            self._tcex.log.error(err)
            raise RuntimeError(err)

        return data

    def _request_process(self, response):
        """
        """
        data = []
        status = None

        if response.status_code in self._status_codes[self._http_method]:
            # Process all JSON type responses
            if response.headers['content-type'] == 'application/json':
                data, status = self._request_process_json(response)
            elif response.headers['content-type'] == 'application/octet-stream':
                data, status = self._request_process_octet(response)
            else:
                err = 'Failed Request: {}'.format(response.text)
                self._tcex.log.error(err)
                self._tcex.message_tc(err)
        else:
            status = 'Failure'
            err = 'Failed Request {}: ({})'.format(self._name, response.text)
            self._tcex.log.error(err)

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

            if self._api_branch == 'bulk':
                data, status = self._request_process_json_bulk(response_data)
            elif response_data.get('data') is None:
                data, status = self._request_process_json_status(response_data)
            elif response_data.get('status') == 'Success':
                data, status = self._request_process_json_standard(response_data)

                """ setup pagination """
                if self._result_count is None:
                    self._result_count = response_data.get('data', {}).get('resultCount')
            else:
                self._tcex.message_tc('Failed Request: {}'.format(response.text))
                status = 'Failure'
        except KeyError as e:
            # TODO: Remove try/except block
            status = 'Failure'
            msg = 'Error: Invalid key {}. [{}] '.format(e, self.request_entity)
            self._tcex.message_tc(msg)
            self._tcex.log.error(msg)
        except ValueError as e:
            # TODO: Remove try/except block
            status = 'Failure'
            msg = 'Error: ({})'.format(e)
            self._tcex.message_tc(msg)
            self._tcex.log.error(msg)
            # bcs = raise error

        return data, status

    def _request_process_json_bulk(self, response_data):
        """Handle bulk JSON response

        Return:
            (string): The response data
            (string): The response status
        """
        status = 'Failure'
        data = response_data.get(self.request_entity, [])
        if len(data) != 0:
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
        if len(data) != 0:
            status = 'Success'

        return data, status

    def add_filter(self, name, operator, value):
        """Add ThreatConnect API Filter for this resource request.

        Internal Reference:
            https://docs.google.com/document/d/1mZx9qF9o9RqVGXd_hT6t55aqLtPyzTL2zWRVQsB3HiM

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
            (str): The **indicators** endpoint from ``/v2/indicators`` or ``/v2/indicators/addresses``.
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

    def association_custom(self, resource_api_branch, association_name):
        """Association pivot for this resource with resource value.

        .. Attention:: New untested method

        **Example Endpoints URI's**

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/indicators/{indicatorType}/{uniqueId}/associations/{associationName}/indicators                 |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/{indicatorType}/{uniqueId}/associations/{associationName}/indicators/{indicatorType} |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_api_branch (string): The resource pivot api branch.
            association_name (string): The name of the custom association as defined in the UI.
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = '{}/associations/{}/{}'.format(
            resource_api_branch, association_name, self._request_uri)

    def association_pivot(self, resource_api_branch):
        """Pivot point on association for this resource.

        This method will return all *resources* (group, indicators, task,
        victims, etc) for this resource that are associated with the provided
        resource_type and value.

        **Example Endpoints URI's**

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/groups/{pivot resourceType}/{pivot uniqueId}/{resourceType}                                     |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/groups/{pivot resourceType}/{pivot uniqueId}/{resourceType}/{uniqueId}                          |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | POST         | /v2/groups/{pivot resourceType}/{pivot uniqueId}/{resourceType}/{uniqueId}                          |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/{pivot resourceType}/{pivot uniqueId}/{resourceType}                                 |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/{pivot resourceType}/{pivot uniqueId}/{resourceType}/{uniqueId}                      |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | POST         | /v2/indicator/{pivot resourceType}/{pivot uniqueId}/{resourceType}/{uniqueId}                       |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_api_branch (string): The resource pivot api branch including resource id.
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = '{}/{}'.format(resource_api_branch, self._request_uri)
        # bcs ^ by using request_uri a user can change pivots without having to worry about the
        #       uri getting mangled, but adding id's and indicators gets overwritten.  Since
        #       the uri should get reset after the request is made is should be okay to
        #       use request_uri here.

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

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/groups/{resourceType}/{uniqueId}/attributes                                                     |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/groups/{resourceType}/{uniqueId}/attributes/{resourceId}                                        |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | DELETE       | /v2/groups/{resourceType}/{uniqueId}/attributes/{resourceId}                                        |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | POST         | /v2/groups/{resourceType}/{uniqueId}/attributes                                                     |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | PUT          | /v2/groups/{resourceType}/{uniqueId}/attributes/{resourceId}                                        |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_id (Optional [string]): The resource id (attribute id).
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = '{}/attributes'.format(self._request_uri)
        self._request_entity = 'attribute'
        if resource_id is not None:
            self._request_uri = '{}/{}'.format(self._request_uri, resource_id)

    def authorization_method(self, method):
        """Method to create authorization header for this resource request.

        Args:
            method (method): The method to use to generate the authorization header(s).
        """
        self._authorization_method = method

    @property
    def body(self):
        """The body for this resource request.

        Return:
            (any): The HTTP request body.
        """
        return self._r.body

    @body.setter
    def body(self, data):
        """The POST/PUT body content for this resource request."""
        self._r.body = data

    @property
    def content_type(self):
        """The Content-Type header value for this resource request."""
        return self._r.content_type

    @content_type.setter
    def content_type(self, data):
        """The Content-Type header for this resource request."""
        self._r.content_type = data

    def file_action(self, resource_id, action_name):
        """File action pivot for this resource.

        .. Attention:: New untested method

        .. Note:: Possible action_names are: drop, archive or traffic

        **Example Endpoints URI's**

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/indicators/files/{uniqueId}/actions/{actionName}/indicators/                                    |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/files/{uniqueId}/actions/{actionName}/indicators/{type}                              |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_id (string): The resource pivot id (file hash).
            action_name (string): The name of the action as defined by ThreatConnect.
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = '{}/{}/actions/{}/{}'.format(
            self._request_api_branch, resource_id, action_name, self._request_uri)

    def group_pivot(self, resource_type, resource_id):
        """Pivot point on groups for this resource.

        This method will return all *resources* (indicators, tasks, victims,
        etc) for this resource that are associated with the provided resource
        id (indicator value).

        **Example Endpoints URI's**

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/groups/{resourceType}/{resourceId}/indicators/{resourceType}                                    |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/groups/{resourceType}/{resourceId}/indicators/{resourceType}/{uniqueId}                         |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/groups/{resourceType}/{resourceId}/tasks/                                                       |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/groups/{resourceType}/{resourceId}/tasks/{uniqueId}                                             |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/groups/{resourceType}/{resourceId}/victims/                                                     |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/groups/{resourceType}/{resourceId}/victims/{uniqueId}                                           |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_type (string): The resource pivot resource type (indicator type).
            resource_id (integer): The resource pivot id (indicator value).
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = 'groups/{}/{}/{}'.format(
            resource_type, resource_id, self._request_uri)

    @property
    def http_method(self):
        """The HTTP Method for this resource request.

        Return:
            (string): The HTTP request method (GET, POST, etc.)
        """
        return self._r.http_method

    @http_method.setter
    def http_method(self, data):
        """The HTTP Method for this resource request."""
        data = data.upper()
        if data in ['DELETE', 'GET', 'POST', 'PUT']:
            self._r.http_method = data
            self._http_method = data

    def indicator_pivot(self, resource_type, resource_id):
        """Pivot point on indicators for this resource.

        This method will return all *resources* (groups, tasks, victims, etc)
        for this resource that are associated with the provided resource id
        (indicator value).

        **Example Endpoints URI's**

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/indicators/{resourceType}/{resourceId}/groups/{resourceType}                                    |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/{resourceType}/{resourceId}/groups/{resourceType}/{uniqueId}                         |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/{resourceType}/{resourceId}/tasks/                                                   |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/{resourceType}/{resourceId}/tasks/{uniqueId}                                         |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/{resourceType}/{resourceId}/victims/                                                 |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/{resourceType}/{resourceId}/victims/{uniqueId}                                       |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_type (string): The resource pivot resource type (indicator type).
            resource_id (integer): The resource pivot id (indicator value).
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = 'indicators/{}/{}/{}'.format(
            resource_type, resource_id, self._request_uri)

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
        return self._r.payload.get('owner')

    @owner.setter
    def owner(self, data):
        """The Owner payload value for this resource request."""
        if data is not None:
            self._r.add_payload('owner', data)
        else:
            self._tcex.log.warn('Provided owner was invalid. ({})'.format(data))

    @property
    def parent(self):
        """The parent object name for this resource.

        Return:
            (str): The API endpoint parent value (e.g. Indicator for Address or Group for Adversary.)
        """
        return self._parent

    def paginate(self):
        """Paginate results from ThreatConnect API

        .. Attention:: This method will be deprecated in a future release.

        Return:
            (dictionary): Resource Data
        """
        self._tcex.log.warning('Using deprecated method (paginate).')
        resources = []
        self._r.add_payload('resultStart', self._result_start)
        self._r.add_payload('resultLimit', self._result_limit)
        results = self.request()
        response = results.get('response')
        if results.get('status') == 'Success':
            data = response.json()['data']
            resources = data[self.request_entity]

            # set results count returned by first API call
            if data.get('resultCount') is not None:
                self._result_count = data.get('resultCount')
                # self._result_start = self._result_limit

            self._tcex.log.debug('Result Count: {}'.format(self._result_count))

            while True:
                if len(resources) >= self._result_count:
                    break
                self._result_start += self._result_limit
                self._r.add_payload('resultStart', self._result_start)
                results = self.request()
                resources.extend(results['data'])

            self._tcex.log.debug('Resource Count: {}'.format(len(resources)))

        return resources

    def request(self):
        """Send the request to the API.

        This method will send the request to the API.  It will try to handle
        all the types of responses and provide the relevant data when possible.
        Some basic error detection and handling is implemented, but not all failure
        cases will get caught.

        Return:
            (dictionary): Response/Results data.
        """
        if self._url is None:
            err = 'URL must not be None Type.'
            self._tcex.log.error(err)
            raise AttributeError(err)

        """ configure request """
        self._r.authorization_method(self._authorization_method)
        self._r.url = '{}/v2/{}'.format(self._url, self._request_uri)
        self._apply_filters()
        self._tcex.log.debug('Resource URL: ({})'.format(self._r.url))

        response = self._r.send(stream=self._stream)
        data, status = self._request_process(response)

        # bcs - to reset or not to reset?
        self._r.body = None
        # self._r.reset_headers()
        # self._r.reset_payload()
        self._pivot = False
        self._request_uri = self._api_uri
        self._request_entity = self._api_entity

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

    def security_label_pivot(self, resource_id):
        """Pivot point on security labels for this resource.

        This method will return all *resources* (group, indicators, task,
        victims, etc) for this resource that have the provided security
        label applied.

        **Example Endpoints URI's**

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/securityLabels/{resourceId}/groups/{resourceType}                                               |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/securityLabels/{resourceId}/groups/{resourceType}/{uniqueId}                                    |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/securityLabels/{resourceId}/indicators/{resourceType}                                           |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/securityLabels/{resourceId}/indicators/{resourceType}/{uniqueId}                                |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_id (string): The resource pivot id (security label name).
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = 'securityLabels/{}/{}'.format(resource_id, self._request_uri)

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

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/{resourceType}/{uniqueId}/securityLabels                                                        |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/{resourceType}/{uniqueId}/securityLabels/{resourceId}                                           |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | DELETE       | /v2/{resourceType}/{uniqueId}/securityLabels/{resourceId}                                           |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | POST         | /v2/{resourceType}/{uniqueId}/securityLabels/{resourceId}                                           |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_id (Optional [string]): The resource id (security label name).
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = '{}/securityLabels'.format(self._request_uri)
        self._request_entity = 'securityLabel'
        if resource_id is not None:
            self._request_uri = '{}/{}'.format(self._request_uri, resource_id)

    def tag_pivot(self, resource_id):
        """Pivot point on tags for this resource.

        This method will return all *resources* (group, indicators, task,
        victims, etc) for this resource that have the provided tag applied.

        **Example Endpoints URI's**

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/tags/{resourceId}/groups/{resourceType}                                                         |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/tags/{resourceId}/groups/{resourceType}/{uniqueId}                                              |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/tags/{resourceId}/indicators/{resourceType}                                                     |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/tags/{resourceId}/indicators/{resourceType}/{uniqueId}                                          |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | POST         | /v2/tags/{resourceId}/groups/{resourceType}/{uniqueId}                                              |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | POST         | /v2/tags/{resourceId}/indicators/{resourceType}/{uniqueId}                                          |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_id (string): The resource pivot id (tag name).
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = 'tags/{}/{}'.format(
            self._tcex.safetag(resource_id), self._request_uri)

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

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/groups/{resourceType}/{uniqueId}/tags                                                           |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/groups/{resourceType}/{uniqueId}/tags/{resourceId}                                              |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/{resourceType}/{uniqueId}/tags                                                       |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/indicators/{resourceType}/{uniqueId}/tags/{resourceId}                                          |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | DELETE       | /v2/groups/{resourceType}/{uniqueId}/tags/{resourceId}                                              |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | DELETE       | /v2/indicators/{resourceType}/{uniqueId}/tags/{resourceId}                                          |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | POST         | /v2/groups/{resourceType}/{uniqueId}/tags/{resourceId}                                              |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | POST         | /v2/indicators/{resourceType}/{uniqueId}/tags/{resourceId}                                          |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_id (Optional [string]): The resource id (tag name).
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = '{}/tags'.format(self._request_uri)
        self._request_entity = 'tag'
        if resource_id is not None:
            self._request_uri = '{}/{}'.format(
                self._request_uri, self._tcex.safetag(resource_id))

    def task_pivot(self, resource_id):
        """Pivot point on Tasks for this resource.

        This method will return all *resources* (group, indicators, victims,
        etc) for this resource that are associated with the provided task id.

        **Example Endpoints URI's**

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/tasks/{resourceId}/groups/{resourceType}                                                        |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/tasks/{resourceId}/groups/{resourceType}/{uniqueId}                                             |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/tasks/{resourceId}/indicators/{resourceType}                                                    |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/tasks/{resourceId}/indicators/{resourceType}/{uniqueId}                                         |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_id (integer): The resource pivot id (task id).
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = 'tasks/{}/{}'.format(
            resource_id, self._request_uri)

    @property
    def value_fields(self):
        """The value fields for this resource.

        Returns:
            (list): The fields in the response JSON that have the key value (e.g. ['md5', 'sha1', 'sha256'] or ['ip']).
        """
        return self._value_fields

    def victim_pivot(self, resource_id):
        """Pivot point on Victims for this resource.

        This method will return all *resources* (group, indicators, task,
        etc) for this resource that are associated with the provided victim id.

        **Example Endpoints URI's**

        +--------------+-----------------------------------------------------------------------------------------------------+
        | HTTP Method  | API Endpoint URI's                                                                                  |
        +==============+=====================================================================================================+
        | GET          | /v2/victims/{resourceId}/groups/{resourceType}                                                      |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/victims/{resourceId}/groups/{resourceType}/{uniqueId}                                           |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/victims/{resourceId}/indicators/{resourceType}                                                  |
        +--------------+-----------------------------------------------------------------------------------------------------+
        | GET          | /v2/victims/{resourceId}/indicators/{resourceType}/{uniqueId}                                       |
        +--------------+-----------------------------------------------------------------------------------------------------+

        Args:
            resource_id (integer): The resource pivot id (victim id).
        """
        if self._pivot:
            self._tcex.log.warn('Overriding previous pivot')

        self._pivot = True
        self._request_uri = 'victims/{}/{}'.format(
            resource_id, self._request_uri)

    @property
    def url(self):
        """The ThreatConnect URL for this resource request.

        Return:
            (str): The requested URL.
        """
        return self._url

    @url.setter
    def url(self, data):
        """The ThreatConnect URL for this resource request."""
        self._url = data

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
        self._r.add_payload('resultLimit', self._result_limit)
        if self._result_count is not None:
            # on an endpoint that support pagination the default resultStart is 0
            self._r.add_payload('resultStart', self._result_start)

        results = self.request()

        # endpoints that support pagination will set self._result_count
        if self._result_count is not None:
            self._result_start += self._result_limit
            self._paginate_count += len(results.get('data'))

            if self._paginate_count >= self._result_count:
                self._paginate = True  # reset so object can be reused
                raise StopIteration
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
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Body', self._r.body)

        # headers
        if len(self._r.headers) > 0:
            printable_string += '\n{0!s:40}\n'.format('Headers')
            for k, v in self._r.headers.items():
                printable_string += '  {0!s:<29}{1!s:<50}\n'.format(k, v)

        # payload
        if len(self._r.payload) > 0:
            printable_string += '\n{0!s:40}\n'.format('Payload')
            for k, v in self._r.payload.items():
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

    def indicator(self, data):
        """Update the request URI to include the Indicator for specific indicator retrieval.

        Args:
            data (string): The indicator value
        """
        if self._name != 'Bulk' or self._name != 'Indicator':
            self._request_uri = '{}/{}'.format(self._request_uri, data)

    def resource_id(self, data):
        """Alias for indicator method.

        The resource id for an indicator in this class is the indicator value and not
        the actual indicator id stored in ThreatConnect.

        Args:
            data (string): The indicator value.
        """
        self.indicator(data)


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
        self._api_entity = 'indicator'
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
            self._r.add_payload('runNow', True)

    def json(self, ondemand=False):
        """Update request URI to return JSON data.

        For onDemand bulk generation to work it must first be enabled in the
        ThreatConnect platform under System settings.

        Args:
            ondemand (boolean): Enable on demand bulk generation.
        """
        self._request_uri = '{}/{}'.format(self._api_uri, 'json')
        self._stream = True
        if ondemand:
            self._r.add_payload('runNow', True)


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

    def occurrence(self, indicator):
        """Update the URI to retrieve file occurrences for the provided indicator.

        Args:
            indicator (string): The indicator to retrieve file occurrences.
        """
        self._request_entity = 'fileOccurrence'
        self._request_uri = '{}/{}/fileOccurrences'.format(self._api_uri, indicator)


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

    def indicator(self, data):
        """Update the request URI to include the Indicator for specific indicator retrieval.

        Overload parent class method to ensure URL indicator is properly encoded.

        Args:
            data (string): The indicator value.
        """
        self._request_uri = '{}/{}'.format(self._api_uri, self._tcex.safeurl(data))


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
            self._request_uri = '{}/{}'.format(self._request_uri, resource_id)

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
        self._request_uri = '{}/{}'.format(self._request_uri, resource_id)


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
            'POST': [200],
            'PUT': [200]
        }
        self._value_fields = ['name']

    def resource_id(self, resource_id):
        """Update the request URI to include the Task Id for specific retrieval.

        Args:
            resource_id (string): The task id.
        """
        self._request_uri = '{}/{}'.format(self._request_uri, resource_id)


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
            'POST': [200],
            'PUT': [200]
        }
        self._value_fields = ['name']

    def resource_id(self, resource_id):
        """Update the request URI to include the Victim Id for specific retrieval.

        Args:
            resource_id (string): The victim id.
        """
        self._request_uri = '{}/{}'.format(self._request_uri, resource_id)


#
# Class Factory
#


def class_factory(name, base_class, class_dict):
    """Internal method for dynamically building Custom Indicator classes."""

    def __init__(self, tcex):
        base_class.__init__(self, tcex)
        for k, v in class_dict.items():
            setattr(self, k, v)

    newclass = type(name, (base_class,), {"__init__": __init__})
    return newclass
