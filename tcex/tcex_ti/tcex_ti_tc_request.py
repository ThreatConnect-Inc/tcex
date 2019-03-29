# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
try:
    from urllib import quote  # Python 2
    from urllib import quote_plus  # Python 2
except ImportError:
    from urllib.parse import quote  # Python
    from urllib.parse import quote_plus  # Python

# import local modules for dynamic reference
module = __import__(__name__)


class TiTcRequest:
    """Common API calls to ThreatConnect"""

    def __init__(self, tcex):
        """

        :param tcex:
        """
        self.tcex = tcex
        self.result_limit = 10000

    def create(self, main_type, sub_type, data, owner):
        """

        :param main_type:
        :param sub_type:
        :param data:
        :param owner:
        :return:
        """
        if not owner:
            pass

        # ex groups/adversary (will need to map them to the actual string value of them)
        if not sub_type:
            url = '/v2/{}'.format(main_type)
        else:
            url = '/v2/{}/{}'.format(main_type, sub_type)

        return self.tcex.session.post(url, json=data, params={'owner': owner})

    def delete(self, main_type, sub_type, unique_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :return:
        """
        unique_id = quote_plus(unique_id)
        if not sub_type:
            url = '/v2/{}/{}'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}'.format(main_type, sub_type, unique_id)
        return self.tcex.session.delete(url)

    def update(self, main_type, sub_type, unique_id, data):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param data:
        :return:
        """
        unique_id = quote_plus(unique_id)
        if not sub_type:
            url = '/v2/{}/{}'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}'.format(main_type, sub_type, unique_id)
        return self.tcex.session.put(url, json=data)

    def single(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :return:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}'.format(main_type, sub_type, unique_id)
        return self.tcex.session.get(url, params=params)

    def many(self, main_type, sub_type, api_entity, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param api_entity:
        """
        if params is None:
            params = {}

        if not sub_type:
            url = '/v2/{}'.format(main_type)
        else:
            url = '/v2/{}/{}'.format(main_type, sub_type)

        yield from self._iterate(url, params, api_entity)

    def _iterate(self, url, params, api_entity):
        """

        :param url:
        :param params:
        :param api_entity:
        """
        params['resultLimit'] = self.result_limit
        should_iterate = True
        result_offset = 0
        while should_iterate:
            params['resultOffset'] = result_offset
            response = self.tcex.session.get(url, params=params)
            if not self.success(response):
                # STILL NEED TO HANDLE THIS
                should_iterate = False
            data = response.json().get('data').get(api_entity)

            if len(data) < self.result_limit:
                should_iterate = False
            result_offset += self.result_limit

            for result in data:
                yield result

    def request(self, main_type, sub_type, result_limit, result_offset, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param result_limit:
        :param result_offset:
        :return:
        """
        if params is None:
            params = {}
        params['resultLimit'] = result_limit or params.get('result_limit', self.result_limit)
        params['resultOffset'] = result_offset or params.get('result_offset', 0)
        if not sub_type:
            url = '/v2/{}'.format(main_type)
        else:
            url = '/v2/{}/{}'.format(main_type, sub_type)

        return self.tcex.session.get(url, params=params)

    def upload(self, main_type, sub_type, unique_id, data, update_if_exists=True):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param data:
        :param update_if_exists:
        :return:
        """
        update_if_exists = data.get('update_if_exists', update_if_exists)
        url = '/v2/{}/{}/{}/upload?updateIfExists={}'.format(
            main_type, sub_type, unique_id, update_if_exists
        )
        return self.tcex.session.post(url)

    def add_false_positive(self, main_type, sub_type, unique_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :return:
        """
        unique_id = quote_plus(unique_id)
        url = '/v2/{}/{}/{}/falsePositive'.format(main_type, sub_type, unique_id)

        return self.tcex.session.post(url)

    def owners(self, main_type, sub_type, unique_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :return:
        """
        if not sub_type:
            url = '/v2/{}/{}/owners'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/owners'.format(main_type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def add_observations(self, main_type, sub_type, unique_id, data):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param data:
        :return:
        """
        url = '/v2/{}/{}/{}/observations'.format(main_type, sub_type, unique_id)
        return self.tcex.session.post(url, json=data)

    def observation_count(self, main_type, sub_type, unique_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :return:
        """
        if not sub_type:
            url = '/v2/{}/{}/observationCount'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/observationCount'.format(main_type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def observations(self, main_type, sub_type, unique_id, owner, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param owner:
        :return:
        """
        if params is None:
            params = {}
        params['owner'] = owner or params.get('owner', None)
        if not sub_type:
            url = '/v2/{}/{}/observations'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/observations'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url, json=params)

    def download(self, main_type, sub_type, unique_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :return:
        """
        if not sub_type:
            url = '/v2/{}/{}/download'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/download'.format(main_type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def dns_resolution(self, main_type, sub_type, unique_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :return:
        """
        if not sub_type:
            url = '/v2/{}/{}/dnsResolution'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/dnsResolution'.format(main_type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def deleted(self, main_type, sub_type, deleted_since, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param deleted_since:
        :return:
        """
        if params is None:
            params = {}
        params['deleteSince'] = deleted_since or params.get(deleted_since, None)

        if not sub_type:
            url = '/v2/{}/deleted'.format(main_type)
        else:
            url = '/v2/{}/{}/deleted'.format(main_type, sub_type)

        return self.tcex.session.get(url, params=params)

    def pivot_from_tag(self, target, tag_name, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param tag_name:
        """
        main_type = target.type
        sub_type = target.api_sub_type
        api_type = target.api_type
        api_entity = target.api_entity
        if params is None:
            params = {}
        if sub_type:
            url = '/v2/tags/{}/{}/{}'.format(tag_name, api_type, sub_type)
        else:
            url = '/v2/tags/{}/{}/'.format(tag_name, api_type)
        print(url)
        yield from self._iterate(url, params, api_entity)

    def groups_from_tag(self, group, tag_name, params=None):
        """

        :param params:
        :param group_type:
        :param tag_name:
        """
        if params is None:
            params = {}
        yield from self.pivot_from_tag(group, tag_name, params=params)

    def indicators_from_tag(self, indicator, tag_name, params=None):
        """
        :param params:
        :param indicator_type:
        :param tag_name:
        """
        if params is None:
            params = {}
        yield from self.pivot_from_tag(indicator, tag_name, params=params)

    def victims_from_tag(self, tag_name, params=None):
        """

        :param params:
        :param tag_name:
        """
        if params is None:
            params = {}
        yield from self.pivot_from_tag('victims', None, tag_name, params=params)

    def indicator_associations(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/indicators'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/indicators'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'indicator')

    def group_associations(self, main_type, sub_type, unique_id, params=None):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param params:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/groups'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/groups'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'group')

    def victim_asset_associations(self, main_type, sub_type, unique_id, branch_type, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param branch_type:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/{}'.format(main_type, unique_id, branch_type)
        else:
            url = '/v2/{}/{}/{}/victimAssets/{}'.format(main_type, sub_type, unique_id, branch_type)

        yield from self._iterate(url, params, 'victimAsset')

    def indicator_associations_types(
            self, main_type, sub_type, unique_id, association_type, api_branch=None,
            api_entity=None, params=None
    ):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param association_type:
        :param api_branch:
        :param api_entity:
        """
        if params is None:
            params = {}
        api_branch = api_branch or association_type.api_sub_type
        api_entity = api_entity or association_type.api_entity
        if not sub_type:
            url = '/v2/{}/{}/indicators/{}'.format(main_type, unique_id, api_branch)
        else:
            url = '/v2/{}/{}/{}/indicators/{}'.format(main_type, sub_type, unique_id, api_branch)

        yield from self._iterate(url, params, api_entity)

    def group_associations_types(
            self, main_type, sub_type, unique_id, target, api_branch=None,
            api_entity=None, params=None
    ):
        """
        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param target:
        :param api_branch:
        :param api_entity:
        """
        if params is None:
            params = {}
        api_branch = api_branch or target.api_sub_type
        api_entity = api_entity or target.api_entity

        if not sub_type:
            url = '/v2/{}/{}/groups/{}'.format(main_type, unique_id, api_branch)
        else:
            url = '/v2/{}/{}/{}/groups/{}'.format(main_type, sub_type, unique_id, api_branch)

        yield from self._iterate(url, params, api_entity)

    def add_association(
            self, main_type, sub_type, unique_id, target_type, target_sub_type, target_unique_id
    ):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param target_type:
        :param target_sub_type:
        :param target_unique_id:
        :return:
        """
        return self._association(
            main_type, sub_type, unique_id, target_type, target_sub_type, target_unique_id
        )

    def delete_association(
            self, main_type, sub_type, unique_id, target_type, target_sub_type, target_unique_id
    ):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param target_type:
        :param target_sub_type:
        :param target_unique_id:
        :return:
        """
        return self._association(
            main_type,
            sub_type,
            unique_id,
            target_type,
            target_sub_type,
            target_unique_id,
            action='DELETE',
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
    ):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param target_type:
        :param target_sub_type:
        :param target_unique_id:
        :param action:
        :return:
        """
        action = action.upper()
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
            response = self.tcex.session.post(url)
        elif action == 'DELETE':
            response = self.tcex.session.delete(url)
        else:
            self.tcex.log.error('associations error')
        return response

    def add_victim_phone_asset(self, unique_id, name):
        """

        :param unique_id:
        :param name:
        :return:
        """
        url = '/v2/victims/{}/victimAssets/phoneNumbers'.format(unique_id)
        return self.tcex.session.post(url, json={'phoneType': name})

    def add_victim_email_asset(self, unique_id, name, asset_type):
        """

        :param unique_id:
        :param name:
        :param asset_type:
        :return:
        """
        url = '/v2/victims/{}/victimAssets/emailAddresses'.format(unique_id)
        return self.tcex.session.post(url, json={'address': name, 'addressType': asset_type})

    def add_victim_network_asset(self, unique_id, name, asset_type):
        """

        :param unique_id:
        :param name:
        :param asset_type:
        :return:
        """
        url = '/v2/victims/{}/victimAssets/networkAccounts'.format(unique_id)
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def add_victim_social_asset(self, unique_id, name, asset_type):
        """

        :param unique_id:
        :param name:
        :param asset_type:
        :return:
        """
        url = '/v2/victims/{}/victimAssets/socialNetworks'.format(unique_id)
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def add_victim_web_asset(self, unique_id, name):
        """

        :param unique_id:
        :param name:
        :return:
        """
        url = '/v2/victims/{}/victimAssets/webSites'.format(unique_id)
        return self.tcex.session.post(url, json={'webSite': name})

    def update_victim_phone_asset(self, unique_id, asset_id, name):
        """

        :param unique_id:
        :param asset_id:
        :param name:
        :return:
        """
        url = '/v2/victims/{}/victimAssets/phoneNumbers/{}'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'phoneType': name})

    def update_victim_email_asset(self, unique_id, asset_id, name, asset_type):
        """

        :param unique_id:
        :param asset_id:
        :param name:
        :param asset_type:
        :return:
        """
        url = '/v2/victims/{}/victimAssets/emailAddresses/{}'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'address': name, 'addressType': asset_type})

    def update_victim_network_asset(self, unique_id, asset_id, name, asset_type):
        """

        :param unique_id:
        :param asset_id:
        :param name:
        :param asset_type:
        :return:
        """
        url = '/v2/victims/{}/victimAssets/networkAccounts/{}'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def update_victim_social_asset(self, unique_id, asset_id, name, asset_type):
        """

        :param unique_id:
        :param asset_id:
        :param name:
        :param asset_type:
        :return:
        """
        url = '/v2/victims/{}/victimAssets/socialNetworks/{}'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'account': name, 'network': asset_type})

    def update_victim_web_asset(self, unique_id, asset_id, name):
        """

        :param unique_id:
        :param asset_id:
        :param name:
        :return:
        """
        url = '/v2/victims/{}/victimAssets/webSites/{}'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'webSite': name})

    def victim(self, main_type, sub_type, unique_id, victim_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param victim_id:
        :return:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/victims/{}'.format(main_type, unique_id, victim_id)
        else:
            url = '/v2/{}/{}/{}/victims/{}'.format(main_type, sub_type, unique_id, victim_id)

        return self.tcex.session.get(url, params=params)

    def victims(self, main_type, sub_type, unique_id, params=None):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param params:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/victims'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victims'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'victim')

    def victim_assets(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/victimAssets'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'victimAssets')

    def victim_email_assets(self, main_type, sub_type, unique_id, params=None):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param params:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/emailAddresses'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/emailAddresses'.format(type, sub_type, unique_id)

        yield from self._iterate(url, params, 'victimEmail')

    def victim_network_assets(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/networkAccounts'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/networkAccounts'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'victimNetwork')

    def victim_phone_assets(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/phoneNumbers'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/phoneNumbers'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'victimPhone')

    def victim_social_assets(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/socialNetworks'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/socialNetworks'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'victimSocial')

    def victim_web_assets(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/webSites'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/webSites'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'victimWeb')

    def victim_email_asset(self, main_type, sub_type, unique_id, asset_id,
                           action='GET', params=None):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :param action:
        :param params:
        :return:
        """
        if params is None:
            params = {}
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

    def victim_network_asset(self, main_type, sub_type, unique_id, asset_id,
                             action='GET', params=None):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :param action:
        :param params:
        :return:
        """
        if params is None:
            params = {}
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

    def victim_phone_asset(self, main_type, sub_type, unique_id, asset_id,
                           action='GET', params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :param action:
        :return:
        """
        if params is None:
            params = {}
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

    def victim_social_asset(self, main_type, sub_type, unique_id, asset_id,
                            action='GET', params=None):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :param action:
        :param params:
        :return:
        """
        if params is None:
            params = {}
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

    def victim_web_asset(self, main_type, sub_type, unique_id, asset_id,
                         action='GET', params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :param action:
        :return:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/webSites/{}'.format(main_type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/webSites/{}'.format(
                main_type, sub_type, unique_id, asset_id
            )

        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        return None

    def get_victim_email_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        if params is None:
            params = {}
        return self.victim_email_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def get_victim_network_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        if params is None:
            params = {}
        return self.victim_network_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def get_victim_phone_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        return self.victim_phone_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def get_victim_social_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        if params is None:
            params = {}
        return self.victim_social_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def get_victim_web_asset(self, main_type, sub_type, unique_id, asset_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        if params is None:
            params = {}
        return self.victim_web_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def delete_victim_email_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        return self.victim_email_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_network_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        return self.victim_network_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_phone_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        return self.victim_phone_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_social_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        return self.victim_social_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_web_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        return self.victim_web_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def tag(self, main_type, sub_type, unique_id, tag, action='GET', params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param tag:
        :param action:
        :return:
        """
        if params is None:
            params = {}
        action = action.upper()
        tag_url = '/v2/{}/{}/{}/tags/{}'.format(main_type, sub_type, unique_id, quote(tag))
        response = None
        if action == 'ADD':
            response = self.tcex.session.post(tag_url)
        elif action == 'DELETE':
            response = self.tcex.session.delete(tag_url)
        elif action == 'GET':
            response = self.tcex.session.get(tag_url, params=params)
        else:
            self.tcex.log.error('_tags error')
        return response

    def add_tag(self, main_type, sub_type, unique_id, tag):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param tag:
        :return:
        """
        return self.tag(main_type, sub_type, unique_id, tag, action='ADD')

    def delete_tag(self, main_type, sub_type, unique_id, tag):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param tag:
        :return:
        """
        return self.tag(main_type, sub_type, unique_id, tag, action='DELETE')

    def get_tag(self, main_type, sub_type, unique_id, tag, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param tag:
        :return:
        """
        if params is None:
            params = {}
        return self.tag(main_type, sub_type, unique_id, tag, params=params)

    def tags(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/tags'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/tags'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'tag')

    def labels(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/securityLabels'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/securityLabels'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'securityLabel', )

    def add_label(self, main_type, sub_type, unique_id, label):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param label:
        :return:
        """
        return self.label(main_type, sub_type, unique_id, label, action='ADD')

    def get_label(self, main_type, sub_type, unique_id, label, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param label:
        :return:
        """
        if params is None:
            params = {}
        return self.label(main_type, sub_type, unique_id, label, action='GET', params=params)

    def delete_label(self, main_type, sub_type, unique_id, label):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param label:
        :return:
        """
        return self.label(main_type, sub_type, unique_id, label, action='DELETE')

    def label(self, main_type, sub_type, unique_id, label, action='ADD', params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param label:
        :param action:
        :return:
        """
        if params is None:
            params = {}
        action = action.upper()

        if not sub_type:
            url = '/v2/{}/{}/securityLabels/{}'.format(main_type, unique_id, quote(label))
        else:
            url = '/v2/{}/{}/{}/securityLabels/{}'.format(
                main_type, sub_type, unique_id, quote(label)
            )

        if action == 'ADD':
            return self.tcex.session.post(url)

        if action == 'DELETE':
            return self.tcex.session.delete(url)

        if action == 'GET':
            return self.tcex.session.get(url, params=params)

        return None

    def attributes(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """

        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/attributes'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/attributes'.format(main_type, sub_type, unique_id)

        yield from self._iterate(url, params, 'attribute')

    def attribute(self, main_type, sub_type, unique_id, attribute_id, action='GET', params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param attribute_id:
        :param action:
        :return:
        """
        if params is None:
            params = {}
        action = action.upper()
        if not sub_type:
            url = '/v2/{}/{}/attributes/{}'.format(main_type, unique_id, attribute_id)
        else:
            url = '/v2/{}/{}/{}/attributes/{}'.format(main_type, sub_type, unique_id, attribute_id)

        if action == 'GET':
            return self.tcex.session.get(url, params=params)

        if action == 'DELETE':
            return self.tcex.session.delete(url)

        return None

    def get_attribute(self, main_type, sub_type, unique_id, attribute_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param attribute_id:
        :return:
        """
        if params is None:
            params = {}
        return self.attribute(main_type, sub_type, unique_id, attribute_id, params=params)

    def delete_attribute(self, main_type, sub_type, unique_id, attribute_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param attribute_id:
        :return:
        """
        return self.attribute(main_type, sub_type, unique_id, attribute_id, action='DELETE')

    def add_attribute(self, main_type, sub_type, unique_id, attribute_type, attribute_value):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param attribute_type:
        :param attribute_value:
        :return:
        """
        if not sub_type:
            url = '/v2/{}/{}/attributes'.format(main_type, unique_id)
        else:
            url = '/v2/{}/{}/{}/attributes'.format(main_type, sub_type, unique_id)

        return self.tcex.session.post(url, json={'type': attribute_type, 'value': attribute_value})

    def attribute_labels(self, main_type, sub_type, unique_id, attribute_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param attribute_id:
        """
        if params is None:
            params = {}
        if not sub_type:
            url = '/v2/{}/{}/attributes/{}/securityLabels'.format(
                main_type, unique_id, attribute_id
            )
        else:
            url = '/v2/{}/{}/{}/attributes/{}/securityLabels'.format(
                main_type, sub_type, unique_id, attribute_id
            )

        yield from self._iterate(url, params, 'securityLabel')

    def attribute_label(self, main_type, sub_type, unique_id, attribute_id, label, action='GET',
                        params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param attribute_id:
        :param label:
        :param action:
        :return:
        """
        if params is None:
            params = {}
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
            return self.tcex.session.post(url)

        if action == 'DELETE':
            return self.tcex.session.delete(url)

        if action == 'GET':
            return self.tcex.session.get(url, params=params)

        return None

    def get_attribute_label(self, main_type, sub_type, unique_id, attribute_id, label, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param attribute_id:
        :param label:
        :return:
        """
        if params is None:
            params = {}
        return self.attribute_label(main_type, sub_type, unique_id, attribute_id, label,
                                    params=params)

    def delete_attribute_label(self, main_type, sub_type, unique_id, attribute_id, label):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param attribute_id:
        :param label:
        :return:
        """
        return self.attribute_label(
            main_type, sub_type, unique_id, attribute_id, label, action='DELETE'
        )

    def add_attribute_label(self, main_type, sub_type, unique_id, attribute_id, label):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param attribute_id:
        :param label:
        :return:
        """
        return self.attribute_label(
            main_type, sub_type, unique_id, attribute_id, label, action='ADD'
        )

    def adversary_assets(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        url = '/v2/{}/{}/{}/adversaryAssets'.format(main_type, sub_type, unique_id)
        yield from self._iterate(url, params, 'adversaryAsset')

    def adversary_handle_assets(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        url = '/v2/{}/{}/{}/adversaryAssets/handles'.format(main_type, sub_type, unique_id)
        yield from self._iterate(url, params, 'adversaryHandle')

    def adversary_phone_assets(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        url = '/v2/{}/{}/{}/adversaryAssets/phoneNumbers'.format(main_type, sub_type, unique_id)
        yield from self._iterate(url, params, 'adversaryPhone')

    def adversary_url_assets(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        url = '/v2/{}/{}/{}/adversaryAssets/urls'.format(main_type, sub_type, unique_id)
        yield from self._iterate(url, params, 'adversaryUrl')

    def adversary_url_asset(self, main_type, sub_type, unique_id, asset_id,
                            action='GET', params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :param action:
        :return:
        """
        if params is None:
            params = {}
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

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        if params is None:
            params = {}
        return self.adversary_url_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def delete_adversary_url_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        return self.adversary_url_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def add_adversary_url_asset(self, main_type, sub_type, unique_id, name):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param name:
        :return:
        """
        asset_url = '/v2/{}/{}/{}/urls'.format(main_type, sub_type, unique_id)
        asset = {'url': name}
        return self.tcex.session.post(asset_url, json=asset)

    def adversary_phone_asset(self, main_type, sub_type, unique_id, asset_id,
                              action='GET', params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :param action:
        :return:
        """
        if params is None:
            params = {}
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

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        if params is None:
            params = {}
        return self.adversary_phone_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def delete_adversary_phone_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        return self.adversary_phone_asset(main_type, sub_type, unique_id, asset_id, action='DELETE')

    def add_adversary_phone_asset(self, main_type, sub_type, unique_id, name):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param name:
        :return:
        """
        asset_url = '/v2/{}/{}/{}/phoneNumbers'.format(main_type, sub_type, unique_id)
        asset = {'phoneNumber': name}
        return self.tcex.session.post(asset_url, json=asset)

    def adversary_handler_asset(self, main_type, sub_type, unique_id, asset_id,
                                action='GET', params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :param action:
        :return:
        """
        if params is None:
            params = {}
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

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        if params is None:
            params = {}
        return self.adversary_handler_asset(main_type, sub_type, unique_id, asset_id, params=params)

    def delete_adversary_handler_asset(self, main_type, sub_type, unique_id, asset_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param asset_id:
        :return:
        """
        return self.adversary_handler_asset(
            main_type, sub_type, unique_id, asset_id, action='DELETE'
        )

    def add_adversary_handler_asset(self, main_type, sub_type, unique_id, name):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param name:
        :return:
        """
        asset_url = '/v2/{}/{}/{}/handles'.format(main_type, sub_type, unique_id)
        asset = {'handle': name}
        return self.tcex.session.post(asset_url, json=asset)

    def assignees(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        url = '/v2/{}/{}/{}/assignees'.format(main_type, sub_type, unique_id)
        yield from self._iterate(url, params, 'assignee')

    def assignee(self, main_type, sub_type, unique_id, assignee_id, action='GET', params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param assignee_id:
        :param action:
        :return:
        """
        if params is None:
            params = {}
        url = '/v2/{}/{}/{}/assignees/{}'.format(main_type, sub_type, unique_id, assignee_id)
        if action == 'GET':
            return self.tcex.session.get(url, params=params)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        if action == 'ADD':
            return self.tcex.session.get(url)
        return None

    def get_assignee(self, main_type, sub_type, unique_id, assignee_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param assignee_id:
        :return:
        """
        if params is None:
            params = {}
        return self.assignee(main_type, sub_type, unique_id, assignee_id, params=params)

    def delete_assignee(self, main_type, sub_type, unique_id, assignee_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param assignee_id:
        :return:
        """
        return self.assignee(main_type, sub_type, unique_id, assignee_id, action='DELETE')

    def add_assignee(self, main_type, sub_type, unique_id, assignee_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param assignee_id:
        :return:
        """
        return self.assignee(main_type, sub_type, unique_id, assignee_id, action='ADD')

    def escalatees(self, main_type, sub_type, unique_id, params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        """
        if params is None:
            params = {}
        url = '/v2/{}/{}/{}/escalatees'.format(main_type, sub_type, unique_id)
        yield from self._iterate(url, params, 'escalatee')

    def escalatee(self, main_type, sub_type, unique_id, escalatee_id, action='GET', params=None):
        """

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param escalatee_id:
        :param action:
        :return:
        """
        if params is None:
            params = {}
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

        :param params:
        :param main_type:
        :param sub_type:
        :param unique_id:
        :param escalatee_id:
        :return:
        """
        if params is None:
            params = {}
        return self.escalatee(main_type, sub_type, unique_id, escalatee_id, params=params)

    def delete_escalatee(self, main_type, sub_type, unique_id, escalatee_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param escalatee_id:
        :return:
        """
        return self.escalatee(main_type, sub_type, unique_id, escalatee_id, action='DELETE')

    def add_escalatee(self, main_type, sub_type, unique_id, escalatee_id):
        """

        :param main_type:
        :param sub_type:
        :param unique_id:
        :param escalatee_id:
        :return:
        """
        return self.escalatee(main_type, sub_type, unique_id, escalatee_id, action='ADD')

    @staticmethod
    def success(r):
        """

        :param r:
        :return:
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
