# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
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
        """Initialize Class properites."""
        self.tcex = tcex
        self.result_limit = 10000

    def create(self, main_type, sub_type, data, owner):
        """[summary]

        Args:
            main_type ([type]): [description]
            sub_type ([type]): [description]
            data (dict): The body for the POST.
            owner (str): The name of the TC owner.

        Returns:
            request.Response: The response from the API call.
        """
        if not owner:
            pass

        # ex groups/adversary (will need to map them to the actual string value of them)
        url = f'/v2/{main_type}'
        if sub_type:
            url = f'/v2/{main_type}/{sub_type}'

        r = self.tcex.session.post(url, json=data, params={'owner': owner})
        self.tcex.log.trace(f'body: {data}')
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def delete(self, main_type, sub_type, unique_id, owner=None):
        """Delete the Indicator/Group/Victim or Security Label

        Args:
            main_type:
            sub_type:
            unique_id:
            owner:
        """
        params = {'owner': owner} if owner else {}
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}'
        r = self.tcex.session.delete(url, params=params)
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def update(self, main_type, sub_type, unique_id, data, owner=None):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            data:

        Returns:

        """
        params = {'owner': owner} if owner else {}
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}'

        r = self.tcex.session.put(url, params=params, json=data)
        self.tcex.log.trace(f'body: {data}')
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def mine(self):
        """
        Get My owners
        Returns:

        """
        url = '/v2/owners/mine'
        return self.tcex.session.get(url)

    def single(self, main_type, sub_type, unique_id, owner=None, filters=None, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            owner:
            filters:
            params:

        Returns:

        """
        params = params or {}

        if owner:
            params['owner'] = owner
        if filters and filters.filters:
            params['filters'] = filters.filters_string
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}'

        r = self.tcex.session.get(url, params=params)
        self.tcex.log.trace(f'url: {r.request.url}')
        return r

    def many(self, main_type, sub_type, api_entity, owner=None, filters=None, params=None):
        """

        Args:
            main_type:
            sub_type:
            api_entity:
            filters:
            owner:
            params:

        Returns:

        """
        params = params or {}

        if owner:
            params['owner'] = owner
        if filters and filters.filters:
            params['filters'] = filters.filters_string
        if not sub_type:
            url = f'/v2/{main_type}'
        else:
            url = f'/v2/{main_type}/{sub_type}'

        yield from self._iterate(url, params, api_entity)

    def _iterate(self, url, params, api_entity):
        """
        Args:
            url:
            params:
            api_entity:

        Return:
        """
        params['resultLimit'] = self.result_limit
        should_iterate = True
        result_start = 0
        while should_iterate:
            # params['resultOffset'] = result_offset
            params['resultStart'] = result_start
            r = self.tcex.session.get(url, params=params)
            if not self.success(r):
                err = r.text or r.reason
                self.tcex.handle_error(950, [r.status_code, err, r.url])

            data = r.json().get('data', {}).get(api_entity, [])

            if len(data) < self.result_limit:
                should_iterate = False
            result_start += self.result_limit

            yield from data

    def request(
        self, main_type, sub_type, result_limit, result_start, owner=None, filters=None, params=None
    ):
        """

        Args:
            main_type:
            sub_type:
            result_limit:
            result_start:
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
        params['resultLimit'] = result_limit or params.get('result_limit', self.result_limit)
        params['resultStart'] = result_start or params.get('result_start', 0)
        if not sub_type:
            url = f'/v2/{main_type}'
        else:
            url = f'/v2/{main_type}/{sub_type}'

        return self.tcex.session.get(url, params=params)

    def upload(self, main_type, sub_type, unique_id, data, update_if_exists=True):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            data:
            update_if_exists:

        Return:

        """
        if not isinstance(data, bytes):
            data = bytes(data, 'utf-8')

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/upload?updateIfExists={update_if_exists}'
        return self.tcex.session.post(url, data=data)

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

        return self.tcex.session.post(url, params=params)

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

        return self.tcex.session.get(url, params=params)

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
        return self.tcex.session.post(url, json=data, params=params)

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

        return self.tcex.session.get(url, params=params)

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

        return self.tcex.session.get(url, json=params)

    def get_file_hash(self, main_type, sub_type, unique_id, hash_type='sha256'):
        """

        Args:
            main_type:
            sub_type:
            unique_id:

        Return:

        """
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/download'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/download'

        if hash_type == 'sha256':
            hashed_file = hashlib.sha256()
        elif hash_type == 'sha1':
            hashed_file = hashlib.sha1()
        else:
            hashed_file = hashlib.md5()

        with self.tcex.session.get(url, stream=True) as r:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:  # filter out keep-alive new chunks
                    hashed_file.update(chunk)
        return hashed_file

    def download(self, main_type, sub_type, unique_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:

        Return:

        """
        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/download'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/download'

        return self.tcex.session.get(url)

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

        return self.tcex.session.get(url, params=params)

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

        return self.tcex.session.put(url, params=params, json=data)

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

        return self.tcex.session.put(url, params=params, json=data)

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

    def deleted(self, main_type, sub_type, deleted_since, owner=None, filters=None, params=None):
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
            params['deleteSince'] = deleted_since

        if not sub_type:
            url = f'/v2/{main_type}/deleted'
        else:
            url = f'/v2/{main_type}/{sub_type}/deleted'

        r = self.tcex.session.get(url, params=params)

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
        yield from self._iterate(url, params, api_entity)

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
        yield from self.pivot_from_tag(group, tag_name, filters=filters, owner=owner, params=params)

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
        self, main_type, sub_type, unique_id, branch_type, owner=None, params=None
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            branch_type:
            params:

        Return:

        """
        params = params or {}

        if owner:
            params['owner'] = owner

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/victimAssets/{branch_type}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets/{branch_type}'

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

        api_branch = api_branch or association_type.api_sub_type
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

        response = None
        if action == 'ADD':
            response = self.tcex.session.post(url, params=params)
        elif action == 'DELETE':
            response = self.tcex.session.delete(url, params=params)
        else:
            self.tcex.log.error('associations error')
        return response

    def add_victim_phone_asset(self, unique_id, name):
        """

        Args:
            unique_id:
            name:

        Return:

        """
        url = f'/v2/victims/{unique_id}/victimAssets/phoneNumbers'
        return self.tcex.session.post(url, json={'phoneType': name})

    def add_victim_email_asset(self, unique_id, name, asset_type):
        """
        Args:
            unique_id:
            name:
            asset_type:

        Return:

        """
        url = f'/v2/victims/{unique_id}/victimAssets/emailAddresses'
        return self.tcex.session.post(url, json={'address': name, 'addressType': asset_type})

    def add_victim_network_asset(self, unique_id, name, asset_type):
        """

        Args:
            unique_id:
            name:
            asset_type:

        Return:

        """
        url = f'/v2/victims/{unique_id}/victimAssets/networkAccounts'
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def add_victim_social_asset(self, unique_id, name, asset_type):
        """

        Args:
            unique_id:
            name:
            asset_type:

        Return:

        """
        url = f'/v2/victims/{unique_id}/victimAssets/socialNetworks'
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def add_victim_web_asset(self, unique_id, name):
        """

        Args:
            unique_id:
            name:

        Return:

        """
        url = f'/v2/victims/{unique_id}/victimAssets/webSites'
        return self.tcex.session.post(url, json={'webSite': name})

    def update_victim_phone_asset(self, unique_id, asset_id, name):
        """

        Args:
            unique_id:
            asset_id:
            name:

        Return:

        """
        url = f'/v2/victims/{unique_id}/victimAssets/phoneNumbers/{asset_id}'
        return self.tcex.session.post(url, json={'phoneType': name})

    def update_victim_email_asset(self, unique_id, asset_id, name, asset_type):
        """

        Args:
            unique_id:
            asset_id:
            name:
            asset_type:

        Return:

        """
        url = f'/v2/victims/{unique_id}/victimAssets/emailAddresses/{asset_id}'
        return self.tcex.session.post(url, json={'address': name, 'addressType': asset_type})

    def update_victim_network_asset(self, unique_id, asset_id, name, asset_type):
        """

        Args:
            unique_id:
            asset_id:
            name:
            asset_type:

        Return:

        """
        url = f'/v2/victims/{unique_id}/victimAssets/networkAccounts/{asset_id}'
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def update_victim_social_asset(self, unique_id, asset_id, name, asset_type):
        """

        Args:
            unique_id:
            asset_id:
            name:
            asset_type:

        Return:

        """
        url = f'/v2/victims/{unique_id}/victimAssets/socialNetworks/{asset_id}'
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def update_victim_web_asset(self, unique_id, asset_id, name):
        """

        Args:
            unique_id:
            asset_id:
            name:

        Return:

        """
        url = f'/v2/victims/{unique_id}/victimAssets/webSites/{asset_id}'
        return self.tcex.session.post(url, json={'webSite': name})

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

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/victims/{victim_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victims/{victim_id}'

        return self.tcex.session.get(url, params=params)

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

    def victim_assets(self, main_type, sub_type, unique_id, params=None):
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
            url = f'/v2/{main_type}/{unique_id}/victimAssets'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets'

        yield from self._iterate(url, params, 'victimAssets')

    def victim_email_assets(self, main_type, sub_type, unique_id, params=None):
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
            url = f'/v2/{main_type}/{unique_id}/victimAssets/emailAddresses'
        else:
            url = f'/v2/{type}/{sub_type}/{unique_id}/victimAssets/emailAddresses'

        yield from self._iterate(url, params, 'victimEmail')

    def victim_network_assets(self, main_type, sub_type, unique_id, params=None):
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
            url = f'/v2/{main_type}/{unique_id}/victimAssets/networkAccounts'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets/networkAccounts'

        yield from self._iterate(url, params, 'victimNetwork')

    def victim_phone_assets(self, main_type, sub_type, unique_id, params=None):
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
            url = f'/v2/{main_type}/{unique_id}/victimAssets/phoneNumbers'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets/phoneNumbers'

        yield from self._iterate(url, params, 'victimPhone')

    def victim_social_assets(self, main_type, sub_type, unique_id, params=None):
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
            url = f'/v2/{main_type}/{unique_id}/victimAssets/socialNetworks'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets/socialNetworks'

        yield from self._iterate(url, params, 'victimSocial')

    def victim_web_assets(self, main_type, sub_type, unique_id, params=None):
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
            url = f'/v2/{main_type}/{unique_id}/victimAssets/webSites'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets/webSites'

        yield from self._iterate(url, params, 'victimWeb')

    def victim_email_asset(
        self, main_type, sub_type, unique_id, asset_id, action='GET', params=None
    ):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            action:
            params:

        Return:

        """
        params = params or {}

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/victimAssets/emailAddresses/{asset_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets/emailAddresses/{asset_id}'

        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        return None

    def victim_network_asset(
        self, main_type, sub_type, unique_id, asset_id, action='GET', params=None
    ):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            action:
            params:

        Return:

        """
        params = params or {}

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/victimAssets/networkAccounts/{asset_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets/networkAccounts/{asset_id}'

        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        return None

    def victim_phone_asset(
        self, main_type, sub_type, unique_id, asset_id, action='GET', params=None
    ):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            action:
            params:

        Return:

        """
        params = params or {}

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/victimAssets/phoneNumbers/{asset_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets/phoneNumbers/{asset_id}'

        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        return None

    def victim_social_asset(
        self, main_type, sub_type, unique_id, asset_id, action='GET', params=None
    ):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            action:
            params:

        Return:

        """
        params = params or {}

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/victimAssets/socialNetworks/{asset_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets/socialNetworks/{asset_id}'

        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        return None

    def victim_web_asset(self, main_type, sub_type, unique_id, asset_id, action='GET', params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            action:
            params:

        Return:

        """
        params = params or {}

        if not sub_type:
            url = f'/v2/{main_type}/{unique_id}/victimAssets/webSites/{asset_id}'
        else:
            url = f'/v2/{main_type}/{sub_type}/{unique_id}/victimAssets/webSites/{asset_id}'

        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.delete(url)
        return None

    def get_victim_email_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            params:

        Return:

        """
        params = params or {}

        return self.victim_email_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def get_victim_network_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            params:

        Return:

        """
        params = params or {}

        return self.victim_network_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def get_victim_phone_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            params:

        Return:

        """
        params = params or {}

        return self.victim_phone_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def get_victim_social_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            params:

        Return:

        """
        params = params or {}

        return self.victim_social_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def get_victim_web_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            params:

        Return:

        """
        params = params or {}

        return self.victim_web_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def delete_victim_email_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:

        Return:

        """
        return self.victim_email_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_network_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:

        Return:

        """
        return self.victim_network_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_phone_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:

        Return:

        """
        return self.victim_phone_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

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
            return self.tcex.session.get(url, params=params)

        if action == 'DELETE':
            return self.tcex.session.delete(url, params=params)

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
        return self.tcex.session.post(url, json={'fileName': name, 'path': path, 'date': date})

    def delete_victim_social_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:

        Return:

        """
        return self.victim_social_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_web_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:

        Return:

        """
        return self.victim_web_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

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
            response = self.tcex.session.post(url, params=params)
        elif action == 'DELETE':
            response = self.tcex.session.delete(url, params=params)
        elif action == 'GET':
            response = self.tcex.session.get(url, params=params)
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
            return self.tcex.session.post(url, params=params)

        if action == 'DELETE':
            return self.tcex.session.delete(url, params=params)

        if action == 'GET':
            return self.tcex.session.get(url, params=params)

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
            return self.tcex.session.get(url, params=params)

        if action == 'DELETE':
            return self.tcex.session.delete(url, params=params)

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

        return self.tcex.session.post(url, json=json, params=params)

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

        return self.tcex.session.put(url, json=json, params=params)

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
            return self.tcex.session.post(url, params=params)

        if action == 'DELETE':
            return self.tcex.session.delete(url, params=params)

        if action == 'GET':
            return self.tcex.session.get(url, params=params)

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

    def adversary_assets(self, main_type, sub_type, unique_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/adversaryAssets'
        yield from self._iterate(url, params, 'adversaryAsset')

    def adversary_handle_assets(self, main_type, sub_type, unique_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/adversaryAssets/handles'
        yield from self._iterate(url, params, 'adversaryHandle')

    def adversary_phone_assets(self, main_type, sub_type, unique_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/adversaryAssets/phoneNumbers'
        yield from self._iterate(url, params, 'adversaryPhone')

    def adversary_url_assets(self, main_type, sub_type, unique_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/adversaryAssets/urls'
        yield from self._iterate(url, params, 'adversaryUrl')

    def adversary_url_asset(
        self, main_type, sub_type, unique_id, asset_id, action='GET', params=None
    ):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            action:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/adversaryAssets/urls/{asset_id}'

        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.delete(url)
        return None

    def get_adversary_url_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            params:

        Return:

        """
        params = params or {}

        return self.adversary_url_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def delete_adversary_url_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:

        Return:

        """
        return self.adversary_url_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def add_adversary_url_asset(self, main_type, sub_type, unique_id, name):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            name:

        Return:

        """
        asset_url = f'/v2/{main_type}/{sub_type}/{unique_id}/urls'
        asset = {'url': name}
        return self.tcex.session.post(asset_url, json=asset)

    def adversary_phone_asset(
        self, main_type, sub_type, unique_id, asset_id, action='GET', params=None
    ):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            action:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/adversaryAssets/phoneNumbers/{asset_id}'

        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.delete(url)
        return None

    def get_adversary_phone_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            params:

        Return:

        """
        return self.adversary_phone_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def delete_adversary_phone_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:

        Return:

        """
        return self.adversary_phone_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def add_adversary_phone_asset(self, main_type, sub_type, unique_id, name):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            name:

        Return:

        """
        asset_url = f'/v2/{main_type}/{sub_type}/{unique_id}/phoneNumbers'
        asset = {'phoneNumber': name}
        return self.tcex.session.post(asset_url, json=asset)

    def adversary_handler_asset(
        self, main_type, sub_type, unique_id, asset_id, action='GET', params=None
    ):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            action:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/adversaryAssets/handles/{asset_id}'

        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.delete(url)
        return None

    def get_adversary_handler_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:
            params:

        Return:

        """
        return self.adversary_handler_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def delete_adversary_handler_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            asset_id:

        Return:

        """
        return self.adversary_handler_asset(
            main_type, sub_type, unique_id, asset_id, action='DELETE'
        )

    def add_adversary_handler_asset(self, main_type, sub_type, unique_id, name):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            name:

        Return:

        """
        asset_url = f'/v2/{main_type}/{sub_type}/{unique_id}/handles'
        asset = {'handle': name}
        return self.tcex.session.post(asset_url, json=asset)

    def assignees(self, main_type, sub_type, unique_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/assignees'
        yield from self._iterate(url, params, 'assignee')

    def assignee(self, main_type, sub_type, unique_id, assignee_id, action='ADD', params=None):
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

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/assignees/{assignee_id}'
        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.delete(url)
        if action == 'ADD':
            return self.tcex.session.post(url)
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
        return self.assignee(main_type, sub_type, unique_id, assignee_id, action='DELETE')

    def add_assignee(self, main_type, sub_type, unique_id, assignee_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            assignee_id:

        Return:

        """
        return self.assignee(main_type, sub_type, unique_id, assignee_id, action='ADD')

    def escalatees(self, main_type, sub_type, unique_id, params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/escalatees'
        yield from self._iterate(url, params, 'escalatee')

    def escalatee(self, main_type, sub_type, unique_id, escalatee_id, action='GET', params=None):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            escalatee_id:
            action:
            params:

        Return:

        """
        params = params or {}

        url = f'/v2/{main_type}/{sub_type}/{unique_id}/escalatees/{escalatee_id}'
        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.delete(url)
        if action == 'ADD':
            return self.tcex.session.post(url)
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
        return self.escalatee(main_type, sub_type, unique_id, escalatee_id, action='DELETE')

    def add_escalatee(self, main_type, sub_type, unique_id, escalatee_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:
            escalatee_id:

        Return:

        """
        return self.escalatee(main_type, sub_type, unique_id, escalatee_id, action='ADD')

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
