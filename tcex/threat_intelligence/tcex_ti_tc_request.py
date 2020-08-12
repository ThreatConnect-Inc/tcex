# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
# standard library
import hashlib
from urllib.parse import quote

# import local modules for dynamic reference
module = __import__(__name__)


class TiTcRequest:
    """Common API calls to ThreatConnect

    Args:
        tcex ([type]): [description]
    """

    def __init__(self, tcex):
        """Initialize Class properties."""
        self.tcex = tcex
        self.result_limit = 10000

    def _delete(self, url, params=None):
        """Delete data from API."""
        params = params or {}
        params['createActivityLog'] = params.get('createActivityLog') or 'false'

        r = self.tcex.session.delete(url, params=params)
        self.tcex.log.debug(
            f'Method: ({r.request.method.upper()}), '
            f'Params: ({params}), '
            f'Status Code: {r.status_code}, '
            f'URL: ({r.url})'
        )
        if len(r.content) < 500:
            self.tcex.log.trace(f'response: {r.text}')
        if not r.ok:
            err = r.text or r.reason
            self.tcex.log.error(f'Error deleting data ({err}')
        return r

    def _get(self, url, params=None):
        """Delete data from API."""
        params = params or {}
        params['createActivityLog'] = params.get('createActivityLog') or 'false'

        r = self.tcex.session.get(url, params=params)

        self.tcex.log.debug(
            f'Method: ({r.request.method.upper()}), '
            f'Params: ({params}), '
            f'Status Code: {r.status_code}, '
            f'URL: ({r.url})'
        )
        if len(r.content) < 500:
            self.tcex.log.trace(f'response: {r.text}')
        if not r.ok:
            err = r.text or r.reason
            self.tcex.log.error(f'Error getting data ({err}')
        return r

    def _iterate(self, url, params, api_entity):
        """Iterate over API pagination."""
        params['resultLimit'] = self.result_limit

        should_iterate = True
        result_start = 0
        while should_iterate:
            params['resultStart'] = result_start
            r = self._get(url, params=params)
            if not self.success(r):
                err = r.text or r.reason
                self.tcex.handle_error(950, [r.status_code, err, r.url])
            data = r.json().get('data', {})
            if api_entity:
                data = data.get(api_entity, [])

            if len(data) < self.result_limit:
                should_iterate = False
            result_start += self.result_limit

            yield from data

    def _post(self, url, data, params=None):
        """Post data to API."""
        params = params or {}
        params['createActivityLog'] = params.get('createActivityLog') or 'false'

        r = self.tcex.session.post(url, data=data, params=params)
        self.tcex.log.debug(
            f'Method: ({r.request.method.upper()}), '
            f'Params: ({params}), '
            f'Status Code: {r.status_code}, '
            f'URL: ({r.url})'
        )
        if len(data) < 50 and not isinstance(data, bytes):
            self.tcex.log.trace(f'body: {data}')
        if len(r.content) < 500:
            self.tcex.log.trace(f'response: {r.text}')
        if not r.ok:
            err = r.text or r.reason
            self.tcex.log.error(f'Error posting data ({err}')
        return r

    def _post_json(self, url, json_data, params=None):
        """Post JSON data to API."""
        params = params or {}
        params['createActivityLog'] = params.get('createActivityLog') or 'false'

        r = self.tcex.session.post(url, json=json_data, params=params)
        self.tcex.log.debug(
            f'Method: ({r.request.method.upper()}), '
            f'Params: ({params}), '
            f'Status Code: {r.status_code}, '
            f'URL: ({r.url})'
        )
        self.tcex.log.trace(f'body: {json_data}')
        if len(r.content) < 500:
            self.tcex.log.trace(f'response: {r.text}')
        if not r.ok:
            err = r.text or r.reason
            self.tcex.log.error(f'Error posting data ({err}')
        return r

    def _put_json(self, url, json_data, params=None):
        """Post JSON data to API."""
        params = params or {}
        params['createActivityLog'] = params.get('createActivityLog') or 'false'

        r = self.tcex.session.put(url, json=json_data, params=params)
        self.tcex.log.debug(
            f'Method: ({r.request.method.upper()}), '
            f'Params: ({params}), '
            f'Status Code: {r.status_code}, '
            f'URL: ({r.url})'
        )
        if len(json_data) < 50 and not isinstance(json_data, bytes):
            self.tcex.log.trace(f'body: {json_data}')
        if len(r.content) < 500:
            self.tcex.log.trace(f'response: {r.text}')
        if not r.ok:
            err = r.text or r.reason
            self.tcex.log.error(f'Error updating data ({err}')
        return r

    def add_adversary_handle_asset(self, unique_id, value):
        """Add an asset to an Adversary.

        Args:
            unique_id (str): The unique ID of the Adversary
            value (str): The asset value

        Returns:
            requests.Response: A request Response object.
        """
        asset_url = f'/v2/groups/adversaries/{unique_id}/adversaryAssets/handles'
        asset_data = {'handle': value}
        return self._post_json(asset_url, asset_data)

    def add_adversary_phone_asset(self, unique_id, value):
        """Add an asset to an Adversary.

        Args:
            unique_id (str): The unique ID of the Adversary
            value (str): The asset value

        Returns:
            requests.Response: A request Response object.
        """
        asset_url = f'/v2/groups/adversaries/{unique_id}/adversaryAssets/phoneNumbers'
        asset_data = {'phoneNumber': value}
        return self._post_json(asset_url, asset_data)

    def add_adversary_url_asset(self, unique_id, value):
        """Add an asset to an Adversary.

        Args:
            unique_id (str): The unique ID of the Adversary
            value (str): The asset value

        Returns:
            requests.Response: A request Response object.
        """
        asset_url = f'/v2/groups/adversaries/{unique_id}/adversaryAssets/urls'
        asset_data = {'url': value}
        return self._post_json(asset_url, asset_data)

    def adversary_assets(self, unique_id, params=None):
        """Return all Adversary assets

        Args:
            unique_id (str): The unique ID of the Adversary
            params (dict, optional): The query params for the request. Defaults to None.

        Yields:
            requests.Response: A request Response object.
        """
        params = params or {}

        asset_url = f'/v2/groups/adversaries/{unique_id}/adversaryAssets'
        yield from self._iterate(asset_url, params, 'bucketAsset')

    def adversary_handle_asset(self, unique_id, asset_id, action='GET', params=None):
        """Return Adversary handle asset by ID

        Args:
            unique_id (str): The unique ID of the Adversary
            asset_id: (str) The ID of the asset.
            action: (str): The HTTP method (e.g., DELETE or GET)
            params (dict, optional): The query params for the request. Defaults to None.

        Returns:
            requests.Response: A request Response object.
        """
        params = params or {}

        asset_url = f'/v2/groups/adversaries/{unique_id}/adversaryAssets/handles/{asset_id}'

        # handle DELETE action
        if action == 'DELETE':
            return self._delete(asset_url, params=params)

        return self._get(asset_url, params=params)

    def adversary_handle_assets(self, unique_id, params=None):
        """Return all Adversary handle assets

        Args:
            unique_id (str): The unique ID of the Adversary
            params (dict, optional): The query params for the request. Defaults to None.

        Yields:
            requests.Response: A request Response object.
        """
        params = params or {}

        asset_url = f'/v2/groups/adversaries/{unique_id}/adversaryAssets/handles'
        yield from self._iterate(asset_url, params, 'adversaryHandle')

    def adversary_phone_asset(self, unique_id, asset_id, action='GET', params=None):
        """Return Adversary phone number asset by ID

        Args:
            unique_id (str): The unique ID of the Adversary
            asset_id: (str) The ID of the asset.
            action: (str): The HTTP method (e.g., DELETE or GET)
            params (dict, optional): The query params for the request. Defaults to None.

        Returns:
            requests.Response: A request Response object.
        """
        params = params or {}

        asset_url = f'/v2/groups/adversaries/{unique_id}/adversaryAssets/phoneNumbers/{asset_id}'

        # handle DELETE action
        if action == 'DELETE':
            return self._delete(asset_url, params=params)

        return self._get(asset_url, params=params)

    def adversary_phone_assets(self, unique_id, params=None):
        """Return all Adversary phone assets

        Args:
            unique_id (str): The unique ID of the Adversary
            params (dict, optional): The query params for the request. Defaults to None.

        Yields:
            requests.Response: A request Response object.
        """
        params = params or {}

        asset_url = f'/v2/groups/adversaries/{unique_id}/adversaryAssets/phoneNumbers'
        yield from self._iterate(asset_url, params, 'adversaryPhoneNumber')

    def adversary_url_asset(self, unique_id, asset_id, action='GET', params=None):
        """Return Adversary url asset by ID

        Args:
            unique_id (str): The unique ID of the Adversary
            asset_id: (str) The ID of the asset.
            action: (str): The HTTP method (e.g., DELETE or GET)
            params (dict, optional): The query params for the request. Defaults to None.

        Returns:
            requests.Response: A request Response object.
        """
        params = params or {}

        asset_url = f'/v2/groups/adversaries/{unique_id}/adversaryAssets/urls/{asset_id}'

        # handle DELETE action
        if action == 'DELETE':
            return self._delete(asset_url, params=params)

        return self._get(asset_url, params=params)

    def adversary_url_assets(self, unique_id, params=None):
        """Return all Adversary url assets

        Args:
            unique_id (str): The unique ID of the Adversary
            params (dict, optional): The query params for the request. Defaults to None.

        Yields:
            requests.Response: A request Response object.
        """
        params = params or {}

        asset_url = f'/v2/groups/adversaries/{unique_id}/adversaryAssets/urls'
        yield from self._iterate(asset_url, params, 'adversaryUrl')

    def create(self, main_type, sub_type, data, owner):
        """Create a TI object in the API.

        Args:
            main_type (str): The TI type (e.g., groups or indicators).
            sub_type (str): The TI sub type (e.g., adversaries or addresses).
            data (dict): The body for the POST.
            owner (str): The name of the TC owner.

        Returns:
            request.Response: The response from the API call.
        """
        url = f'/v2/{main_type}'
        if sub_type:
            url = f'/v2/{main_type}/{sub_type}'

        params = {}
        if owner:
            params['owner'] = owner
        return self._post_json(url, data, params)

    def delete(self, main_type, sub_type, unique_id, owner=None):
        """Delete a TI object in the API.

        Args:
            main_type (str): The TI type (e.g., groups or indicators).
            sub_type (str): The TI sub type (e.g., adversaries or addresses).
            data (dict): The body for the POST.
            owner (str): The name of the TC owner.

        Returns:
            request.Response: The response from the API call.
        """
        url = f'/v2/{main_type}/{unique_id}'
        if sub_type:
            if unique_id:
                url = f'/v2/{main_type}/{sub_type}/{unique_id}'

        params = {}
        if owner:
            params['owner'] = owner
        return self._delete(url, params)

    def delete_adversary_handle_asset(self, unique_id, asset_id):
        """Delete Adversary handle assest

        Args:
            unique_id (str): The unique ID of the Adversary.
            asset_id: (str) The ID of the asset.

        Returns:
            requests.Response: A request Response object.
        """
        return self.adversary_handle_asset(unique_id, asset_id, action='DELETE')

    def delete_adversary_phone_asset(self, unique_id, asset_id):
        """Delete Adversary phone assest

        Args:
            unique_id (str): The unique ID of the Adversary.
            asset_id: (str) The ID of the asset.

        Returns:
            requests.Response: A request Response object.
        """
        return self.adversary_phone_asset(unique_id, asset_id, action='DELETE')

    def delete_adversary_url_asset(self, unique_id, asset_id):
        """Delete Adversary URL assest

        Args:
            unique_id (str): The unique ID of the Adversary.
            asset_id: (str) The ID of the asset.

        Returns:
            requests.Response: A request Response object.
        """
        return self.adversary_url_asset(unique_id, asset_id, action='DELETE')

    def download(self, main_type, sub_type, unique_id):
        """Download a Document or Report

        Args:
            main_type (str): The TI type (e.g., groups or indicators).
            sub_type (str): The TI sub type (e.g., adversaries or addresses).
            unique_id (str): The unique ID of the Resource.

        Returns:
            requests.Response: A request Response object.
        """
        url = f'/v2/{main_type}/{unique_id}/download'
        if sub_type:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/download'
        return self._get(url)

    def get_adversary_handle_asset(self, unique_id, asset_id, params=None):
        """Get Adversary handle assest

        Args:
            unique_id (str): The unique ID of the Adversary.
            asset_id: (str) The ID of the asset.

        Returns:
            requests.Response: A request Response object.
        """
        return self.adversary_handle_asset(unique_id, asset_id, params=params)

    def get_adversary_phone_asset(self, unique_id, asset_id, params=None):
        """Get Adversary phone assest

        Args:
            unique_id (str): The unique ID of the Adversary.
            asset_id: (str) The ID of the asset.

        Returns:
            requests.Response: A request Response object.
        """
        return self.adversary_phone_asset(unique_id, asset_id, params=params)

    def get_adversary_url_asset(self, unique_id, asset_id, params=None):
        """Get Adversary URL assest

        Args:
            unique_id (str): The unique ID of the Adversary.
            asset_id: (str) The ID of the asset.

        Returns:
            requests.Response: A request Response object.
        """
        params = params or {}

        return self.adversary_url_asset(unique_id, asset_id, params=params)

    def many(self, main_type, sub_type, api_entity, owner=None, filters=None, params=None):
        """Update a TI object in the API.

        Args:
            main_type (str): The TI type (e.g., groups or indicators).
            sub_type (str): The TI sub type (e.g., adversaries or addresses).
            api_entity (str): The API entity value (e.g., address, file, etc).
            owner (str): The name of the TC owner.
            filters (Filter, optional): A filter object.
            params (dict, optional): Optional dict of query params.

        Yields:
            request.Response: The response from the API call.
        """
        params = params or {}

        # add owner
        if owner:
            params['owner'] = owner

        # add filters
        if filters and filters.filters:
            params['filters'] = filters.filters_string

        # build url
        url = f'/v2/{main_type}'
        if sub_type:
            url = f'/v2/{main_type}/{sub_type}'

        yield from self._iterate(url, params, api_entity)

    def mine(self):
        """Get owner mine data."""
        return self._get('/v2/owners/mine')

    def request(
        self, main_type, sub_type, result_limit, result_start, owner=None, filters=None, params=None
    ):
        """[summary]

        Args:
            main_type ([type]): [description]
            sub_type ([type]): [description]
            result_limit ([type]): [description]
            result_start ([type]): [description]
            owner ([type], optional): [description]. Defaults to None.
            filters ([type], optional): [description]. Defaults to None.
            params ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        params = params or {}

        # add owner
        if owner:
            params['owner'] = owner

        # add filters
        if filters and filters.filters:
            params['filters'] = filters.filters_string

        # add result limits and result start
        params['resultLimit'] = result_limit or params.get('result_limit', self.result_limit)
        params['resultStart'] = result_start or params.get('result_start', 0)

        url = f'/v2/{main_type}'
        if sub_type:
            url = f'/v2/{main_type}/{sub_type}'

        return self._get(url, params)

    def single(self, main_type, sub_type, unique_id, owner=None, filters=None, params=None):
        """Update a TI object in the API.

        Args:
            main_type (str): The TI type (e.g., groups or indicators).
            sub_type (str): The TI sub type (e.g., adversaries or addresses).
            unique_id (str): The unique ID of the TI object.
            owner (str): The name of the TC owner.
            filters (Filter, optional): A filter object.
            params (dict, optional): Optional dict of query params.

        Returns:
            request.Response: The response from the API call.
        """
        params = params or {}

        # add owner
        if owner:
            params['owner'] = owner

        # add filters
        if filters and filters.filters:
            params['filters'] = filters.filters_string

        # build url
        url = f'/v2/{main_type}/{unique_id}'
        if sub_type:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}'

        return self._get(url, params)

    def update(self, main_type, sub_type, unique_id, data, owner=None):
        """Update a TI object in the API.

        Args:
            main_type (str): The TI type (e.g., groups or indicators).
            sub_type (str): The TI sub type (e.g., adversaries or addresses).
            unique_id (str): The unique ID of the TI object.
            data (dict): The body for the POST.
            owner (str): The name of the TC owner.

        Returns:
            request.Response: The response from the API call.
        """
        url = f'/v2/{main_type}/{unique_id}'
        if sub_type:
            if unique_id:
                url = f'/v2/{main_type}/{sub_type}/{unique_id}'

        params = {}
        if owner:
            params['owner'] = owner
        return self._put_json(url, data, params)

    def upload(self, main_type, sub_type, unique_id, data, update_if_exists=True):
        """Upload a file to API.

        Args:
            main_type ([type]): [description]
            sub_type ([type]): [description]
            unique_id ([type]): [description]
            data ([type]): [description]
            update_if_exists (bool, optional): [description]. Defaults to True.

        Returns:
            [type]: [description]
        """
        if not isinstance(data, bytes):
            data = bytes(data, 'utf-8')

        params = {}
        if update_if_exists:
            params['updateIfExists'] = 'true'

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/upload'
        return self._post(url, data=data, params=params)

    def victim_add_asset(self, unique_id, asset_type, body):
        """Add a Asset to a Victim.

        Valid asset_type and optional identifier:
        + email
        + network
        + phone
        + social
        + web

        Args:
            unique_id (str): The Victims ID.
            asset_type: (str) The type of asset to be retrieved.
            body (dict): The body of the Asset.

        Returns:
            request.Response: The response from the API call.
        """
        asset_type = self.victim_asset_type_mapping.get(asset_type.lower(), asset_type)
        asset_url = f'/v2/victims/{unique_id}/victimAssets/{asset_type}'
        return self._post_json(asset_url, body)

    def victim_assets(self, main_type, sub_type, unique_id, asset_type=None, params=None):
        """Retrieve the Assets of a Victim.

        Valid asset_type and optional identifier:
        + email
        + network
        + phone
        + social
        + web

        Args:
            main_type (str): The main type of the TI object.
            sub_type (str): The sub type of the TI object.
            unique_id (str): The unique id of the TI object.
            asset_type: (str) The type of asset to be retrieved. Defaults to all of them.
            params (dict, optional): Optional dict of query params.

        Yields:
            Json: The asset being retrieved.
        """
        params = params or {}

        # This is needed because of tasks
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/victimAssets'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets'
        entity_type = 'victimAsset'
        asset_type = self.victim_asset_type_mapping.get(asset_type)
        if asset_type:
            url += f'/{asset_type}'
        return self._iterate(url, params, entity_type)

    def victim_get_asset(self, unique_id, asset_type, asset_id, params=None):
        """Retrieve a Asset from a Victim.

        Valid asset_type and optional identifier:
        + email
        + network
        + phone
        + social
        + web

        Args:
            unique_id (str): The Victims ID.
            asset_type: (str) The type of asset to be retrieved.
            asset_id (str): The Assets ID .
            params (dict, optional): Optional dict of query params.

        Returns:
            request.Response: The response from the API call.
        """
        params = params or {}
        asset_type = self.victim_asset_type_mapping.get(asset_type.lower(), asset_type)
        asset_url = f'/v2/victims/{unique_id}/victimAssets/{asset_type}/{asset_id}'
        return self._get(asset_url, params=params)

    @property
    def victim_asset_type_mapping(self):
        """Maps the asset type to the api endpoints needed."""
        return {
            'email': 'emailAddresses',
            'network': 'networkAccounts',
            'phone': 'phoneNumbers',
            'social': 'socialNetworks',
            'web': 'webSites',
        }

    def victim_delete_asset(self, unique_id, asset_type, asset_id):
        """Delete a Asset from a Victim.

        Valid asset_type and optional identifier:
        + email
        + network
        + phone
        + social
        + web

        Args:
            unique_id (str): The Victims ID.
            asset_type: (str) The type of asset to be retrieved.
            asset_id (str): The Assets ID .

        Returns:
            request.Response: The response from the API call.
        """
        asset_type = self.victim_asset_type_mapping.get(asset_type.lower(), asset_type)
        asset_url = f'/v2/victims/{unique_id}/victimAssets/{asset_type}/{asset_id}'
        return self._delete(asset_url)

    def victim_update_asset(self, unique_id, asset_type, asset_id, body):
        """Update a Asset of a Victim.

        Valid asset_type and optional identifier:
        + email
        + network
        + phone
        + social
        + web

        Args:
            unique_id (str): The Victims ID.
            asset_type: (str) The type of asset to be retrieved.
            asset_id (str): The Assets ID .
            body (dict): The body of the Asset.

        Returns:
            request.Response: The response from the API call.
        """
        asset_type = self.victim_asset_type_mapping.get(asset_type.lower(), asset_type)
        asset_url = f'/v2/victims/{unique_id}/victimAssets/{asset_type}/{asset_id}'
        return self._put_json(asset_url, body)

    #
    # -- needs updates ---
    #

    def add_false_positive(self, main_type, sub_type, unique_id, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:

        Return:

        """
        params = {'owner': owner} if owner else {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/falsePositive'

        r = self._post(url, {}, params)
        self.tcex.log.debug(f'status code: {r.status_code}')
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def owners(self, main_type, sub_type, unique_id, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:

        Return:

        """
        params = {'owner': owner} if owner else {}
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/owners'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/owners'

        r = self._get(url, params=params)
        self.tcex.log.debug(f'status code: {r.status_code}')
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def add_observations(self, main_type, sub_type, unique_id, data, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            data:

        Return:

        """

        params = {'owner': owner} if owner else {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/observations'
        r = self._post(url, data, params)
        self.tcex.log.debug(f'status code: {r.status_code}')
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def observation_count(self, main_type, sub_type, unique_id, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:

        Return:

        """
        params = {'owner': owner} if owner else {}

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/observationCount'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/observationCount'

        r = self._get(url, params)
        self.tcex.log.debug(f'status code: {r.status_code}')
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def observations(self, main_type, sub_type, unique_id, owner=None, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            owner:
            params:

        Return:

        """
        params = params or {}

        if owner:
            params['owner'] = owner

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/observations'
        else:
            url = f'/v2/{type}/{sub_type}/{unique_id}/observations'

        r = self._get(url, params)
        self.tcex.log.debug(f'status code: {r.status_code}')
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def dns_resolution(self, main_type, sub_type, unique_id, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:

        Return:

        """
        params = {'owner': owner} if owner else {}

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/dnsResolution'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/dnsResolution'

        r = self._get(url, params)
        self.tcex.log.debug(f'status code: {r.status_code}')
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def set_dns_resolution(self, main_type, sub_type, unique_id, value, owner=None):
        """

         Args:
             value:
             owner:
             main_type:
             sub_type:
             unique_id:

         Return:

         """
        params = {'owner': owner} if owner else {}

        data = {}
        if self.is_true(value) or self.is_false(value):
            data['dnsActive'] = self.is_true(value)
        else:
            self.tcex.handle_error(925, ['option', 'dns value', 'value', value])

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}'

        r = self._put_json(url, data, params)
        self.tcex.log.debug(f'status code: {r.status_code}')
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def set_whois(self, main_type, sub_type, unique_id, value, owner=None):
        """

          Args:
              value:
              owner:
              main_type:
              sub_type:
              unique_id:

          Return:

          """
        params = {'owner': owner} if owner else {}

        data = {}
        if self.is_true(value) or self.is_false(value):
            data['whoisActive'] = self.is_true(value)
        else:
            self.tcex.handle_error(925, ['option', 'whois value', 'value', value])

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}'

        r = self._put_json(url, data, params)
        self.tcex.log.debug(f'status code: {r.status_code}')
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    @staticmethod
    def is_false(value):
        """checks to see if a string is False"""
        if not value:
            return False
        value = str(value)
        return value.lower() in ['false', '0', 'f', 'n', 'no']

    @staticmethod
    def is_true(value):
        """checks to see if a string is True"""
        if not value:
            return False
        value = str(value)
        return value.lower() in ['true', '1', 't', 'y', 'yes']

    def deleted(self, main_type, sub_type, deleted_since=None, owner=None, filters=None, params=None):
        """

        Args:
            owner:
            filters:
            main_type:
            sub_type:
            deleted_since:
            params:

        Return:

        """
        params = params or {}

        if filters and filters.filters:
            params['filters'] = filters.filters_string
        if owner:
            params['owner'] = owner
        if deleted_since:
            params['deletedSince'] = deleted_since

        if not sub_type:
            url = f'/v2/{main_type}/deleted'
        else:
            url = f'/v2/{main_type}/{sub_type}/deleted'

        r = self._get(url, params)

        if not self.success(r):
            err = r.text or r.reason
            self.tcex.handle_error(950, [r.status_code, err, r.url])

        data = r.json().get('data', {}).get('indicator', [])

        yield from data

    def pivot_from_tag(self, target, tag_name, filters=None, owner=None, params=None):
        """

        Args:
            owner:
            filters:
            target:
            tag_name:
            params:

        Return:

        """
        sub_type = target.api_branch
        api_type = target.api_type
        api_entity = target.api_entity
        params = params or {}

        if owner:
            params['owner'] = owner

        if filters and filters.filters:
            params['filters'] = filters.filters_string
        if sub_type:
            url = f'/v2/tags/{tag_name}/{api_type}/{sub_type}'
        else:
            url = f'/v2/tags/{tag_name}/{api_type}/'
        return self._iterate(url, params, api_entity)

    def groups_from_tag(self, group, tag_name, filters=None, owner=None, params=None):
        """

        Args:
            owner:
            group:
            tag_name:
            filters:
            params:

        Return:

        """
        return self.pivot_from_tag(group, tag_name, filters=filters, owner=owner, params=params)

    def indicators_from_tag(self, indicator, tag_name, filters=None, owner=None, params=None):
        """
                Args:
                    owner:
                    indicator:
                    tag_name:
                    filters:
                    params:

                Return:

        """
        params = params or {}

        yield from self.pivot_from_tag(
            indicator, tag_name, filters=filters, owner=owner, params=params
        )

    def victims_from_tag(self, victim, tag_name, filters=None, owner=None, params=None):
        """

        Args:
            owner:
            victim:
            tag_name:
            filters:
            params:

        Return:

        """
        yield from self.pivot_from_tag(
            victim, tag_name, filters=filters, owner=owner, params=params
        )

    def indicator_associations(self, main_type, sub_type, unique_id, owner=None, params=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}
        if owner:
            params['owner'] = owner

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/indicators'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/indicators'

        yield from self._iterate(url, params, 'indicator')

    def group_associations(self, main_type, sub_type, unique_id, owner=None, params=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}
        if owner:
            params['owner'] = owner

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/groups'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/groups'

        yield from self._iterate(url, params, 'group')

    def victim_asset_associations(
        self, main_type, sub_type, unique_id, asset_type=None, owner=None, params=None
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            asset_type:
            params:

        Return:

        """
        params = params or {}

        if owner:
            params['owner'] = owner

        url = f'/v2/{main_type}'
        if sub_type:
            url = f'{url}/{sub_type}'
        url = f'{url}/{unique_id}/victimAssets'
        if asset_type:
            url = f'{url}/{asset_type}'

        yield from self._iterate(url, params, 'victimAsset')

    def indicator_associations_types(
        self,
        main_type,
        sub_type,
        unique_id,
        association_type,
        api_branch=None,
        api_entity=None,
        owner=None,
        params=None,
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            association_type:
            api_branch:
            api_entity:
            params:

        Return:

        """
        params = params or {}
        if owner:
            params['owner'] = owner

        api_branch = api_branch or association_type.api_branch
        api_entity = api_entity or association_type.api_entity
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/indicators/{api_branch}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/indicators/{api_branch}'

        yield from self._iterate(url, params, api_entity)

    def group_associations_types(
        self,
        main_type,
        sub_type,
        unique_id,
        target,
        api_branch=None,
        api_entity=None,
        owner=None,
        params=None,
    ):
        """
                Args:
                    owner:
                    main_type:
                    sub_type:
                    unique_id:
                    target:
                    api_branch:
                    api_entity:
                    params:

                Return:

        """
        params = params or {}
        if owner:
            params['owner'] = owner

        api_branch = api_branch or target.api_branch
        api_entity = api_entity or target.api_entity

        if target and target.is_task():
            if not sub_type:
                url = f'/v2/{main_type}/{unique_id}/tasks/{api_branch}'
            else:
                url = f'/v2/{main_type}/{sub_type}/{unique_id}/tasks'
        elif not sub_type:
            url = f'/v2/{main_type}/{unique_id}/groups/{api_branch}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/groups/{api_branch}'

        yield from self._iterate(url, params, api_entity)

    def add_association(
        self,
        main_type,
        sub_type,
        unique_id,
        target_type,
        target_sub_type,
        target_unique_id,
        owner=None,
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            target_type:
            target_sub_type:
            target_unique_id:

        Return:

        """
        return self._association(
            main_type,
            sub_type,
            unique_id,
            target_type,
            target_sub_type,
            target_unique_id,
            owner=owner,
        )

    def delete_association(
        self,
        main_type,
        sub_type,
        unique_id,
        target_type,
        target_sub_type,
        target_unique_id,
        owner=None,
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            target_type:
            target_sub_type:
            target_unique_id:

        Return:

        """
        return self._association(
            main_type,
            sub_type,
            unique_id,
            target_type,
            target_sub_type,
            target_unique_id,
            action='DELETE',
            owner=owner,
        )

    def _association(
        self,
        main_type,
        sub_type,
        unique_id,
        target_type,
        target_sub_type,
        target_unique_id,
        action='ADD',
        owner=None,
    ):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            target_type:
            target_sub_type:
            target_unique_id:
            action:

        Return:

        """
        action = action.upper()
        params = {'owner': owner} if owner else {}
        params['createActivityLog'] = False
        # Typically if victim to victim but other endpoints that are not
        # groups/indicators can exist in the future
        if not sub_type and not target_sub_type:
            url = f'/v2/{main_type}/{unique_id}/{target_type}/{target_unique_id}'
        # Typically if victim to anything else
        elif not sub_type:
            url = f'/v2/{main_type}/{unique_id}/{target_type}/{target_sub_type}/{target_unique_id}'
        # If anything else to victim
        elif not target_sub_type:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/{target_type}/{target_unique_id}'
        else:
            # Everything else
            url = (
                f'/v2/{main_type}/{sub_type}/{unique_id}/{target_type}/{target_sub_type}'
                f'/{target_unique_id}'
            )

        r = None
        params['createActivityLog'] = params.get('createActivityLog') or False
        if action == 'ADD':
            r = self._post(url, {}, params)
        elif action == 'DELETE':
            r = self._delete(url, params)
        else:
            self.tcex.log.error('associations error')

        if r is not None:
            self.tcex.log.debug(f'status code: {r.status_code}')
            self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def victim(self, main_type, sub_type, unique_id, victim_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            victim_id:
            params:

        Return:

        """
        params = params or {}
        params['createActivityLog'] = False

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/victims/{victim_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victims/{victim_id}'

        return self._get(url, params)

    def victims(self, main_type, sub_type, unique_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/victims'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victims'

        yield from self._iterate(url, params, 'victim')

    def file_occurrences(self, main_type, sub_type, unique_id, owner=None):
        """
        Yields all occurrences a File has

        Args:
            main_type:
            sub_type:
            unique_id:
            owner:
        """
        url = f'/v2/{main_type}/{sub_type}/{unique_id}/fileOccurrences'
        params = {}

        if owner:
            params['owner'] = owner

        yield from self._iterate(url, params, 'fileOccurrence')

    def get_file_hash(self, main_type, sub_type, unique_id, hash_type='sha256'):
        """ Gets the hash of a file. """
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/download'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/download'

        if hash_type == 'sha256':
            hashed_file = hashlib.sha256()  # nosec
        elif hash_type == 'sha1':
            hashed_file = hashlib.sha1()  # nosec
        else:
            hashed_file = hashlib.md5()  # nosec

        with self.tcex.session.get(url, stream=True) as r:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:  # filter out keep-alive new chunks
                    hashed_file.update(chunk)
        return hashed_file

    def get_file_occurrence(self, main_type, sub_type, unique_id, occurrence_id, owner=None):
        """
        Gets a file occurrence given a occurrence_id
        Args:
            main_type:
            sub_type:
            unique_id:
            occurrence_id:
            owner:

        Returns:

        """
        return self.file_occurrence(main_type, sub_type, unique_id, occurrence_id, owner)

    def delete_file_action(self, main_type, sub_type, unique_id, action, target, owner=None):
        """Deletes a file action given a target"""
        url = (
            f'/v2/{main_type}/{sub_type}/{unique_id}/actions/{action}'
            f'/{target.api_type}/{target.api_branch}/{target.unique_id}'
        )
        params = {}

        if owner:
            params['owner'] = owner

        return self._delete(url, params)

    def add_file_action(self, main_type, sub_type, unique_id, action, target, owner=None):
        """Creates a file action given a target"""
        url = (
            f'/v2/{main_type}/{sub_type}/{unique_id}/actions/{action}'
            f'/{target.api_type}/{target.api_branch}/{target.unique_id}'
        )
        params = {}

        if owner:
            params['owner'] = owner

        return self._post(url, {}, params=params)

    def get_file_actions(self, main_type, sub_type, unique_id, action, target, owner=None):
        """Yields a file action given a file action and a target"""
        url = f'/v2/{main_type}/{sub_type}/{unique_id}/actions/{action}/{target.api_type}'

        if target.api_sub_type:
            url = f'{url}/{target.api_branch}'

        params = {}

        if owner:
            params['owner'] = owner

        yield from self._iterate(url, params, target.api_entity)

    def delete_file_occurrence(self, main_type, sub_type, unique_id, occurrence_id, owner=None):
        """
        Deletes a file occurrence given a occurrence_id
        Args:
            main_type:
            sub_type:
            unique_id:
            occurrence_id:
            owner:

        Returns:

        """
        return self.file_occurrence(main_type, sub_type, unique_id, occurrence_id, owner, 'DELETE')

    def file_occurrence(
        self, main_type, sub_type, unique_id, occurrence_id, owner=None, action='GET'
    ):
        """
        Gets a file occurrence given a occurrence_id
        Args:
            main_type:
            sub_type:
            unique_id:
            occurrence_id:
            owner:
            action:

        Returns:

        """
        url = f'/v2/{main_type}/{sub_type}/{unique_id}/fileOccurrences/{occurrence_id}'
        params = {}

        if owner:
            params['owner'] = owner

        if action == 'GET':
            return self._get(url, params)

        if action == 'DELETE':
            return self._delete(url, params)

        return None

    def add_file_occurrence(self, main_type, sub_type, unique_id, name, date, path, owner=None):
        """
        Adds a file occurrence to a File
        Args:
            main_type:
            sub_type:
            unique_id:
            name:
            date:
            path:
            owner:

        Returns:

        """
        url = f'/v2/{main_type}/{sub_type}/{unique_id}/fileOccurrences'
        params = {}
        if owner:
            params['owner'] = owner
        return self._post_json(url, {'fileName': name, 'path': path, 'date': date})

    def tag(self, main_type, sub_type, unique_id, tag, action='GET', owner=None, params=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            tag:
            action:
            params:

        Return:

        """
        params = params or {}

        if owner:
            params['owner'] = owner

        action = action.upper()
        if sub_type:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/tags/{quote(tag)}'
        else:
            url = f'/v2/{main_type}/{unique_id}/tags/{quote(tag)}'
        response = None
        if action == 'ADD':
            response = self._post(url, {}, params)
        elif action == 'DELETE':
            response = self._delete(url, params)
        elif action == 'GET':
            response = self._get(url, params)
        else:
            self.tcex.log.error('_tags error')
        return response

    def add_tag(self, main_type, sub_type, unique_id, tag, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            tag:

        Return:

        """
        return self.tag(main_type, sub_type, unique_id, tag, action='ADD', owner=owner)

    def delete_tag(self, main_type, sub_type, unique_id, tag, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            tag:

        Return:

        """
        return self.tag(main_type, sub_type, unique_id, tag, action='DELETE', owner=owner)

    def get_tag(self, main_type, sub_type, unique_id, tag, owner=None, params=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            tag:
            params:

        Return:

        """
        params = params or {}

        return self.tag(main_type, sub_type, unique_id, tag, owner=owner, params=params)

    def tags(self, main_type, sub_type, unique_id, owner=None, filters=None, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            owner:
            filters:
            params:

        Return:

        """
        params = params or {}

        if owner:
            params['owner'] = owner
        if filters and filters.filters:
            params['filters'] = filters.filters_string
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/tags'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/tags'

        yield from self._iterate(url, params, 'tag')

    def labels(self, main_type, sub_type, unique_id, owner=None, filters=None, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            owner:
            filters:
            params:

        Return:

        """
        params = params or {}

        if owner:
            params['owner'] = owner
        if filters and filters.filters:
            params['filters'] = filters.filters_string
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/securityLabels'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/securityLabels'

        yield from self._iterate(url, params, 'securityLabel')

    def add_label(self, main_type, sub_type, unique_id, label, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            label:

        Return:

        """
        return self.label(main_type, sub_type, unique_id, label, action='ADD', owner=owner)

    def get_label(self, main_type, sub_type, unique_id, label, owner=None, params=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            label:
            params:

        Return:

        """
        params = params or {}

        return self.label(
            main_type, sub_type, unique_id, label, action='GET', owner=owner, params=params
        )

    def delete_label(self, main_type, sub_type, unique_id, label, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            label:

        Return:

        """
        return self.label(main_type, sub_type, unique_id, label, action='DELETE', owner=owner)

    def label(self, main_type, sub_type, unique_id, label, action='ADD', owner=None, params=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            label:
            action:
            params:

        Return:

        """
        params = params or {}

        if owner:
            params['owner'] = owner

        action = action.upper()

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/securityLabels/{quote(label)}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/securityLabels/{quote(label)}'

        if action == 'ADD':
            return self._post(url, {}, params)

        if action == 'DELETE':
            return self._delete(url, params)

        if action == 'GET':
            return self._get(url, params)

        return None

    def attributes(self, main_type, sub_type, unique_id, owner=None, params=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """

        params = params or {}

        if owner:
            params['owner'] = owner

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/attributes'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/attributes'

        yield from self._iterate(url, params, 'attribute')

    def attribute(
        self, main_type, sub_type, unique_id, attribute_id, action='GET', owner=None, params=None
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_id:
            action:
            params:

        Return:

        """
        params = params or {}
        if owner:
            params['owner'] = owner
        action = action.upper()
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/attributes/{attribute_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/attributes/{attribute_id}'

        if action == 'GET':
            return self._get(url, params)

        if action == 'DELETE':
            return self._delete(url, params)

        return None

    def get_attribute(self, main_type, sub_type, unique_id, attribute_id, owner=None, params=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_id:
            params:

        Return:

        """
        return self.attribute(
            main_type, sub_type, unique_id, attribute_id, action='GET', owner=owner, params=params
        )

    def delete_attribute(self, main_type, sub_type, unique_id, attribute_id, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_id:

        Return:

        """
        return self.attribute(
            main_type, sub_type, unique_id, attribute_id, action='DELETE', owner=owner
        )

    def add_attribute(
        self,
        main_type,
        sub_type,
        unique_id,
        attribute_type,
        attribute_value,
        source=None,
        displayed=None,
        owner=None,
        params=None,
    ):
        """

        Args:
            displayed:
            source:
            params:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_type:
            attribute_value:

        Return:

        """
        if params is None:
            params = {}
        if owner:
            params['owner'] = owner
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/attributes'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/attributes'

        json = {'type': attribute_type, 'value': attribute_value}

        if source:
            json['source'] = source

        if displayed:
            json['displayed'] = displayed

        return self._post_json(url, json, params)

    def update_attribute(
        self,
        main_type,
        sub_type,
        unique_id,
        attribute_value,
        attribute_id,
        source=None,
        displayed=None,
        owner=None,
        params=None,
    ):
        """

        Args:
            displayed:
            source:
            params:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_type:
            attribute_value:

        Return:

        """
        if params is None:
            params = {}
        if owner:
            params['owner'] = owner
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/attributes/{attribute_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/attributes/{attribute_id}'

        json = {'value': attribute_value}

        if source:
            json['source'] = source

        if displayed:
            json['displayed'] = displayed

        return self._put_json(url, json, params)

    def attribute_labels(
        self, main_type, sub_type, unique_id, attribute_id, owner=None, params=None
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_id:
            params:

        Return:

        """
        params = params or {}
        if owner:
            params['owner'] = owner

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/attributes/{attribute_id}/securityLabels'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/attributes/{attribute_id}/securityLabels'

        yield from self._iterate(url, params, 'securityLabel')

    def attribute_label(
        self,
        main_type,
        sub_type,
        unique_id,
        attribute_id,
        label,
        action='GET',
        owner=None,
        params=None,
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_id:
            label:
            action:
            params:

        Return:

        """
        params = params or {}
        if owner:
            params['owner'] = owner
        action = action.upper()

        if not sub_type:
            url = (
                f'/v2/{main_type}/{unique_id}/attributes/{attribute_id}/securityLabels/'
                f'{quote(label)}'
            )
        else:
            url = (
                f'/v2/{main_type}/{sub_type}/{unique_id}/attributes/{attribute_id}/securityLabels/'
                f'{quote(label)}'
            )
        if action == 'ADD':
            return self._post(url, {}, params)

        if action == 'DELETE':
            return self._delete(url, params)

        if action == 'GET':
            return self._get(url, params)

        return None

    def get_attribute_label(
        self, main_type, sub_type, unique_id, attribute_id, label, owner=None, params=None
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_id:
            label:
            params:

        Return:

        """
        return self.attribute_label(
            main_type, sub_type, unique_id, attribute_id, label, owner=owner, params=params
        )

    def delete_attribute_label(
        self, main_type, sub_type, unique_id, attribute_id, label, owner=None
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_id:
            label:

        Return:

        """
        return self.attribute_label(
            main_type, sub_type, unique_id, attribute_id, label, action='DELETE', owner=owner
        )

    def add_attribute_label(self, main_type, sub_type, unique_id, attribute_id, label, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_id:
            label:

        Return:

        """
        return self.attribute_label(
            main_type, sub_type, unique_id, attribute_id, label, action='ADD', owner=owner
        )

    def assignees(self, main_type, unique_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{unique_id}/assignees'
        yield from self._iterate(url, params, 'user')

    def assignee(self, main_type, unique_id, assignee_id, action='ADD', params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            assignee_id:
            action:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{unique_id}/assignees/{assignee_id}'
        if action == 'ADD':
            return self._post(url, {}, params)
        if action == 'GET':
            return self._get(url, params=params)
        if action == 'DELETE':
            return self._delete(url, params)
        return None

    def get_assignee(self, main_type, sub_type, unique_id, assignee_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            assignee_id:
            params:

        Return:

        """
        params = params or {}

        return self.assignee(main_type, sub_type, unique_id, assignee_id, params=params)

    def delete_assignee(self, main_type, sub_type, unique_id, assignee_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            assignee_id:

        Return:

        """
        return self.assignee(main_type, sub_type, unique_id, assignee_id, 'DELETE')

    def add_assignee(self, main_type, sub_type, unique_id, assignee_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            assignee_id:

        Return:

        """
        return self.assignee(main_type, sub_type, unique_id, assignee_id, 'ADD')

    def escalatees(self, main_type, unique_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{unique_id}/escalatees'
        yield from self._iterate(url, params, 'user')

    def escalatee(self, main_type, unique_id, escalatee_id, action='GET', params=None):
        """

        Args:
            main_type:
            unique_id:
            escalatee_id:
            action:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{unique_id}/escalatees/{escalatee_id}'
        if action == 'ADD':
            return self._post(url, {}, params)
        if action == 'GET':
            return self._get(url=url, params=params)
        if action == 'DELETE':
            return self._delete(url=url)
        return None

    def get_escalatee(self, main_type, sub_type, unique_id, escalatee_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            escalatee_id:
            params:

        Return:

        """
        params = params or {}

        return self.escalatee(main_type, sub_type, unique_id, escalatee_id, params=params)

    def delete_escalatee(self, main_type, sub_type, unique_id, escalatee_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            escalatee_id:

        Return:

        """
        return self.escalatee(main_type, sub_type, unique_id, escalatee_id, 'DELETE')

    def add_escalatee(self, main_type, sub_type, unique_id, escalatee_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            escalatee_id:

        Return:

        """
        return self.escalatee(main_type, sub_type, unique_id, escalatee_id, 'ADD')

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
