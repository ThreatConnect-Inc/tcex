# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python

# import local modules for dynamic reference
module = __import__(__name__)


class TiTcRequest:
    """Common API calls to ThreatConnect"""

    def __init__(self, tcex):
        """

        Args:
            tcex:
        """
        self.tcex = tcex
        self.result_limit = 10000

    def create(self, main_type, sub_type, data, owner):
        """

        Args:
            main_type:
            sub_type:
            data:
            owner:

        Returns:

        """
        if not owner:
            pass

        # ex groups/adversary (will need to map them to the actual string value of them)
        if not sub_type:
            url = '/v2/{}'.format(main_type)
        else:
            url = '/v2/{}/{}'.format(main_type, sub_type)

        return self.tcex.session.post(url, json=data, params={'owner': owner})

    def delete(self, main_type, sub_type, unique_id, owner=None):
        """
        Deletes the Indicator/Group/Victim or Security Label
        Args:
            main_type:
            sub_type:
            unique_id:
            owner:
        """
        params = {'owner': owner} if owner else {}
        if not sub_type:
            url = '/v2/{}/{}'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}'.format(main_type, sub_type, unique_id)
        return self.tcex.session.delete(url, params=params)

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
            url = '/v2/{}/{}'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}'.format(main_type, sub_type, unique_id)
        return self.tcex.session.put(url, params=params, json=data)

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
            url = '/v2/{}/{}'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}'.format(main_type, sub_type, unique_id)

        return self.tcex.session.get(url, params=params)

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
            url = '/v2/{}'.format(main_type)
        else:
            url = '/v2/{}/{}'.format(main_type, sub_type)

        for i in self._iterate(url, params, api_entity):
            yield i

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

            data = r.json().get('data').get(api_entity)

            if len(data) < self.result_limit:
                should_iterate = False
            result_start += self.result_limit

            for result in data:
                yield result

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
            url = '/v2/{}'.format(main_type)
        else:
            url = '/v2/{}/{}'.format(main_type, sub_type)

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

        url = '/v2/{}/{}/{}/upload?updateIfExists={}'.format(
            main_type, sub_type, unique_id, update_if_exists
        )
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

        url = '/v2/{}/{}/{}/falsePositive'.format(main_type, sub_type, unique_id)

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
            url = '/v2/{}/{}/owners'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/owners'.format(main_type, sub_type, unique_id)

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

        url = '/v2/{}/{}/{}/observations'.format(main_type, sub_type, unique_id)
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
            url = '/v2/{}/{}/observationCount'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/observationCount'.format(main_type, sub_type, unique_id)

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
            url = '/v2/{}/{}/observations'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/observations'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url, json=params)

    def download(self, main_type, sub_type, unique_id):
        """

        Args:
            main_type:
            sub_type:
            unique_id:

        Return:

        """
        if not sub_type:
            url = '/v2/{}/{}/download'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/download'.format(main_type, sub_type, unique_id)

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
            url = '/v2/{}/{}/dnsResolution'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/dnsResolution'.format(main_type, sub_type, unique_id)

        return self.tcex.session.get(url, params=params)

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
            url = '/v2/{}/deleted'.format(main_type)
        else:
            url = '/v2/{}/{}/deleted'.format(main_type, sub_type)

        return self.tcex.session.get(url, params=params)

    def pivot_from_tag(self, target, tag_name, filters=None, params=None):
        """

        Args:
            filters:
            target:
            tag_name:
            params:

        Return:

        """
        sub_type = target.api_sub_type
        api_type = target.api_type
        api_entity = target.api_entity
        params = params or {}

        if filters and filters.filters:
            params['filters'] = filters.filters_string
        if sub_type:
            url = '/v2/tags/{}/{}/{}'.format(tag_name, api_type, sub_type)
        else:
            url = '/v2/tags/{}/{}/'.format(tag_name, api_type)
        for i in self._iterate(url, params, api_entity):
            yield i

    def groups_from_tag(self, group, tag_name, filters=None, params=None):
        """

        Args:
            group:
            tag_name:
            filters:
            params:

        Return:

        """
        for t in self.pivot_from_tag(group, tag_name, filters=filters, params=params):
            yield t

    def indicators_from_tag(self, indicator, tag_name, filters=None, params=None):
        """
                Args:
                    indicator:
                    tag_name:
                    filters:
                    params:

                Return:

        """
        params = params or {}

        for t in self.pivot_from_tag(indicator, tag_name, filters=filters, params=params):
            yield t

    def victims_from_tag(self, victim, tag_name, filters=None, params=None):
        """

        Args:
            victim:
            tag_name:
            filters:
            params:

        Return:

        """
        for t in self.pivot_from_tag(victim, tag_name, filters=filters, params=params):
            yield t

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
            url = '/v2/{}/{}/indicators'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/indicators'.format(main_type, sub_type, unique_id)

        for a in self._iterate(url, params, 'indicator'):
            yield a

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
            url = '/v2/{}/{}/groups'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/groups'.format(main_type, sub_type, unique_id)

        for ga in self._iterate(url, params, 'group'):
            yield ga

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
            url = '/v2/{}/{}/victimAssets/{}'.format(main_type, unique_id, branch_type)
        else:
            url = '/v2/{}/{}/{}/victimAssets/{}'.format(main_type, sub_type, unique_id, branch_type)

        for vaa in self._iterate(url, params, 'victimAsset'):
            yield vaa

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
            url = '/v2/{}/{}/indicators/{}'.format(main_type, unique_id, api_branch)
        else:
            url = '/v2/{}/{}/{}/indicators/{}'.format(main_type, sub_type, unique_id, api_branch)

        for iat in self._iterate(url, params, api_entity):
            yield iat

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

        api_branch = api_branch or target.api_sub_type
        api_entity = api_entity or target.api_entity

        if not sub_type:
            url = '/v2/{}/{}/groups/{}'.format(main_type, unique_id, api_branch)
        else:
            url = '/v2/{}/{}/{}/groups/{}'.format(main_type, sub_type, unique_id, api_branch)

        for gat in self._iterate(url, params, api_entity):
            yield gat

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
            url = '/v2/{}/{}/{}/{}'.format(main_type, unique_id, target_type, target_unique_id)
        # Typically if victim to anything else
        elif not sub_type:
            url = '/v2/{}/{}/{}/{}/{}'.format(
                main_type, unique_id, target_type, target_sub_type, target_unique_id
            )
        # If anything else to victim
        elif not target_sub_type:
            url = '/v2/{}/{}/{}/{}/{}'.format(
                main_type, sub_type, unique_id, target_type, target_unique_id
            )
        else:
            # Everything else
            url = '/v2/{}/{}/{}/{}/{}/{}'.format(
                main_type, sub_type, unique_id, target_type, target_sub_type, target_unique_id
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
        url = '/v2/victims/{}/victimAssets/phoneNumbers'.format(unique_id)
        return self.tcex.session.post(url, json={'phoneType': name})

    def add_victim_email_asset(self, unique_id, name, asset_type):
        """
        Args:
            unique_id:
            name:
            asset_type:

        Return:

        """
        url = '/v2/victims/{}/victimAssets/emailAddresses'.format(unique_id)
        return self.tcex.session.post(url, json={'address': name, 'addressType': asset_type})

    def add_victim_network_asset(self, unique_id, name, asset_type):
        """

        Args:
            unique_id:
            name:
            asset_type:

        Return:

        """
        url = '/v2/victims/{}/victimAssets/networkAccounts'.format(unique_id)
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def add_victim_social_asset(self, unique_id, name, asset_type):
        """

        Args:
            unique_id:
            name:
            asset_type:

        Return:

        """
        url = '/v2/victims/{}/victimAssets/socialNetworks'.format(unique_id)
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def add_victim_web_asset(self, unique_id, name):
        """

        Args:
            unique_id:
            name:

        Return:

        """
        url = '/v2/victims/{}/victimAssets/webSites'.format(unique_id)
        return self.tcex.session.post(url, json={'webSite': name})

    def update_victim_phone_asset(self, unique_id, asset_id, name):
        """

        Args:
            unique_id:
            asset_id:
            name:

        Return:

        """
        url = '/v2/victims/{}/victimAssets/phoneNumbers/{}'.format(unique_id, asset_id)
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
        url = '/v2/victims/{}/victimAssets/emailAddresses/{}'.format(unique_id, asset_id)
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
        url = '/v2/victims/{}/victimAssets/networkAccounts/{}'.format(unique_id, asset_id)
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
        url = '/v2/victims/{}/victimAssets/socialNetworks/{}'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def update_victim_web_asset(self, unique_id, asset_id, name):
        """

        Args:
            unique_id:
            asset_id:
            name:

        Return:

        """
        url = '/v2/victims/{}/victimAssets/webSites/{}'.format(unique_id, asset_id)
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
            url = '/v2/{}/{}/victims/{}'.format(main_type, unique_id, victim_id)
        else:
            url = '/v2/{}/{}/{}/victims/{}'.format(main_type, sub_type, unique_id, victim_id)

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
            url = '/v2/{}/{}/victims'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victims'.format(main_type, sub_type, unique_id)

        for v in self._iterate(url, params, 'victim'):
            yield v

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
            url = '/v2/{}/{}/victimAssets'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets'.format(main_type, sub_type, unique_id)

        for va in self._iterate(url, params, 'victimAssets'):
            yield va

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
            url = '/v2/{}/{}/victimAssets/emailAddresses'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/emailAddresses'.format(type, sub_type, unique_id)

        for vea in self._iterate(url, params, 'victimEmail'):
            yield vea

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
            url = '/v2/{}/{}/victimAssets/networkAccounts'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/networkAccounts'.format(main_type, sub_type, unique_id)

        for vna in self._iterate(url, params, 'victimNetwork'):
            yield vna

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
            url = '/v2/{}/{}/victimAssets/phoneNumbers'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/phoneNumbers'.format(main_type, sub_type, unique_id)

        for vpa in self._iterate(url, params, 'victimPhone'):
            yield vpa

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
            url = '/v2/{}/{}/victimAssets/socialNetworks'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/socialNetworks'.format(main_type, sub_type, unique_id)

        for vsa in self._iterate(url, params, 'victimSocial'):
            yield vsa

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
            url = '/v2/{}/{}/victimAssets/webSites'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/webSites'.format(main_type, sub_type, unique_id)

        for vwa in self._iterate(url, params, 'victimWeb'):
            yield vwa

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
            url = '/v2/{}/{}/victimAssets/emailAddresses/{}'.format(main_type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/emailAddresses/{}'.format(
                main_type, sub_type, unique_id, asset_id
            )

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
            url = '/v2/{}/{}/victimAssets/networkAccounts/{}'.format(main_type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/networkAccounts/{}'.format(
                main_type, sub_type, unique_id, asset_id
            )

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
            url = '/v2/{}/{}/victimAssets/phoneNumbers/{}'.format(main_type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/phoneNumbers/{}'.format(
                main_type, sub_type, unique_id, asset_id
            )

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
            url = '/v2/{}/{}/victimAssets/socialNetworks/{}'.format(main_type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/socialNetworks/{}'.format(
                main_type, sub_type, unique_id, asset_id
            )

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
            url = '/v2/{}/{}/victimAssets/webSites/{}'.format(main_type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/webSites/{}'.format(
                main_type, sub_type, unique_id, asset_id
            )

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
        url = '/v2/{}/{}/{}/fileOccurrences'.format(main_type, sub_type, unique_id)
        params = {}

        if owner:
            params['owner'] = owner

        for o in self._iterate(url, params, 'fileOccurrence'):
            yield o

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
        url = '/v2/{}/{}/{}/fileOccurrences/{}'.format(
            main_type, sub_type, unique_id, occurrence_id
        )
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
        url = '/v2/{}/{}/{}/fileOccurrences'.format(main_type, sub_type, unique_id)
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
            url = '/v2/{}/{}/{}/tags/{}'.format(main_type, sub_type, unique_id, quote(tag))
        else:
            url = '/v2/{}/{}/tags/{}'.format(main_type, unique_id, quote(tag))
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
            url = '/v2/{}/{}/tags'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/tags'.format(main_type, sub_type, unique_id)

        for t in self._iterate(url, params, 'tag'):
            yield t

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
            url = '/v2/{}/{}/securityLabels'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/securityLabels'.format(main_type, sub_type, unique_id)

        for l in self._iterate(url, params, 'securityLabel'):
            yield l

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
            url = '/v2/{}/{}/securityLabels/{}'.format(main_type, unique_id, quote(label))
        else:
            url = '/v2/{}/{}/{}/securityLabels/{}'.format(
                main_type, sub_type, unique_id, quote(label)
            )

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
            url = '/v2/{}/{}/attributes'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/attributes'.format(main_type, sub_type, unique_id)

        for a in self._iterate(url, params, 'attribute'):
            yield a

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
            url = '/v2/{}/{}/attributes/{}'.format(main_type, unique_id, attribute_id)
        else:
            url = '/v2/{}/{}/{}/attributes/{}'.format(main_type, sub_type, unique_id, attribute_id)

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
        self, main_type, sub_type, unique_id, attribute_type, attribute_value, owner=None
    ):
        """

        Args:
            owner:
            main_type:
            sub_type:
            unique_id:
            attribute_type:
            attribute_value:

        Return:

        """
        params = {}
        if owner:
            params['owner'] = owner
        if not sub_type:
            url = '/v2/{}/{}/attributes'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/attributes'.format(main_type, sub_type, unique_id)

        return self.tcex.session.post(
            url, json={'type': attribute_type, 'value': attribute_value}, params=params
        )

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
            url = '/v2/{}/{}/attributes/{}/securityLabels'.format(
                main_type, unique_id, attribute_id
            )
        else:
            url = '/v2/{}/{}/{}/attributes/{}/securityLabels'.format(
                main_type, sub_type, unique_id, attribute_id
            )

        for l in self._iterate(url, params, 'securityLabel'):
            yield l

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
            url = '/v2/{}/{}/attributes/{}/securityLabels/{}'.format(
                main_type, unique_id, attribute_id, quote(label)
            )
        else:
            url = '/v2/{}/{}/{}/attributes/{}/securityLabels/{}'.format(
                main_type, sub_type, unique_id, attribute_id, quote(label)
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

        url = '/v2/{}/{}/{}/adversaryAssets'.format(main_type, sub_type, unique_id)
        for aa in self._iterate(url, params, 'adversaryAsset'):
            yield aa

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

        url = '/v2/{}/{}/{}/adversaryAssets/handles'.format(main_type, sub_type, unique_id)
        for aha in self._iterate(url, params, 'adversaryHandle'):
            yield aha

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

        url = '/v2/{}/{}/{}/adversaryAssets/phoneNumbers'.format(main_type, sub_type, unique_id)
        for apa in self._iterate(url, params, 'adversaryPhone'):
            yield apa

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

        url = '/v2/{}/{}/{}/adversaryAssets/urls'.format(main_type, sub_type, unique_id)
        for aua in self._iterate(url, params, 'adversaryUrl'):
            yield aua

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

        url = '/v2/{}/{}/{}/adversaryAssets/urls/{}'.format(
            main_type, sub_type, unique_id, asset_id
        )

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
        asset_url = '/v2/{}/{}/{}/urls'.format(main_type, sub_type, unique_id)
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

        url = '/v2/{}/{}/{}/adversaryAssets/phoneNumbers/{}'.format(
            main_type, sub_type, unique_id, asset_id
        )

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
        asset_url = '/v2/{}/{}/{}/phoneNumbers'.format(main_type, sub_type, unique_id)
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

        url = '/v2/{}/{}/{}/adversaryAssets/handles/{}'.format(
            main_type, sub_type, unique_id, asset_id
        )

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
        asset_url = '/v2/{}/{}/{}/handles'.format(main_type, sub_type, unique_id)
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

        url = '/v2/{}/{}/{}/assignees'.format(main_type, sub_type, unique_id)
        for a in self._iterate(url, params, 'assignee'):
            yield a

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

        url = '/v2/{}/{}/{}/assignees/{}'.format(main_type, sub_type, unique_id, assignee_id)
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

        url = '/v2/{}/{}/{}/escalatees'.format(main_type, sub_type, unique_id)
        for e in self._iterate(url, params, 'escalatee'):
            yield e

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

        url = '/v2/{}/{}/{}/escalatees/{}'.format(main_type, sub_type, unique_id, escalatee_id)
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
