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

    def __init__(self, tcex):
        self.tcex = tcex

    def create(self, type, sub_type, data, owner):
        if not owner:
            pass

        # ex groups/adversary (will need to map them to the actual string value of them)
        if not sub_type:
            url = '/v2/{}'.format(type)
        else:
            url = '/v2/{}/{}'.format(type, sub_type)

        return self.tcex.session.post(url, json=data, params={'owner': owner})

    def delete(self, type, sub_type, unique_id):
        unique_id = quote_plus(unique_id)
        if not sub_type:
            url = '/v2/{}/{}'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}'.format(type, sub_type, unique_id)
        return self.tcex.session.delete(url)

    def update(self, type, sub_type, unique_id, data):
        unique_id = quote_plus(unique_id)
        if not sub_type:
            url = '/v2/{}/{}'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}'.format(type, sub_type, unique_id)
        return self.tcex.session.put(url, json=data)

    def single(self, type, sub_type, unique_id, **kwargs):
        params = self.construct_params(kwargs.items())
        if not sub_type:
            url = '/v2/{}/{}'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}'.format(type, sub_type, unique_id)
        return self.tcex.session.get(url, params=params)

    def many(self, type, sub_type, **kwargs):
        params = self.construct_params(kwargs.items())
        if not sub_type:
            url = '/v2/{}'.format(type)
        else:
            url = '/v2/{}/{}'.format(type, sub_type)
        return self.tcex.session.get(url, params=params)

    def upload(self, type, sub_type, unique_id, data, update_if_exists=True):
        update_if_exists = data.get('update_if_exists', update_if_exists)
        url = '/v2/{}/{}/{}/upload?updateIfExists={}'.format(type, sub_type, unique_id, update_if_exists)
        return self.tcex.session.post(url)

    def add_false_positive(self, type, sub_type, unique_id):
        unique_id = quote_plus(unique_id)
        url = '/v2/{}/{}/{}/falsePositive'.format(type, sub_type, unique_id)

        return self.tcex.session.post(url)

    def owners(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/owners'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/owners'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def add_observations(self, type, sub_type, unique_id, data):
        url = '/v2/{}/{}/{}/observations'.format(type, sub_type, unique_id)
        return self.tcex.session.post(url, json=data)

    def observation_count(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/observationCount'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/observationCount'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def observations(self, type, sub_type, unique_id, owner):
        params = {'owner': owner}
        if not sub_type:
            url = '/v2/{}/{}/observations'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/observations'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url, json=params)

    def download(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/download'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/download'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def dns_resolution(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/dnsResolution'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/dnsResolution'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def deleted(self, type, sub_type, deleted_since):
        params = {'deletedSince': deleted_since}

        if not sub_type:
            url = '/v2/{}/deleted'.format(type)
        else:
            url = '/v2/{}/{}/deleted'.format(type, sub_type)

        return self.tcex.session.get(url, params=params)

    def indicator_associations(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/indicators'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/indicators'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def group_associations(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/groups'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/groups'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def victim_asset_associations(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def add_association(self, type, sub_type, unique_id, target_type, target_sub_type, target_unique_id):
        return self._association(type, sub_type, unique_id, target_type, target_sub_type, target_unique_id)

    def delete_association(self, type, sub_type, unique_id, target_type, target_sub_type, target_unique_id):
        return self._association(type, sub_type, unique_id, target_type, target_sub_type, target_unique_id, action='DELETE')

    def _association(self, type, sub_type, unique_id, target_type, target_sub_type, target_unique_id, action='ADD'):
        action = action.upper()
        # Typically if victim to victim but other endpoints that arnt groups/indicators can exist in the future
        if not sub_type and not target_sub_type:
            url = '/v2/{}/{}/{}/{}'.format(type, unique_id, target_type, target_unique_id)
        # Typically if victim to anything else
        elif not sub_type:
            url = '/v2/{}/{}/{}/{}/{}'.format(type, unique_id, target_type, target_sub_type, target_unique_id)
        # If anything else to victim
        elif not target_sub_type:
            url = '/v2/{}/{}/{}/{}/{}'.format(type, sub_type, unique_id, target_type, target_unique_id)
        else:
        # Everything else
            url = '/v2/{}/{}/{}/{}/{}/{}'.format(type, sub_type, unique_id, target_type, target_sub_type,
                                                 target_unique_id)

        if action == 'ADD':
            return self.tcex.session.post(url)
        elif action == 'DELETE':
            return self.tcex.session.delete(url)
        else:
            self.tcex.log.error('associations error')
            return

    def add_victim_phone_asset(self, unique_id, name):
        url = '/v2/victims/{}/victimAssets/phoneNumbers'.format(unique_id)
        return self.tcex.session.post(url, json={'phoneType': name})

    def add_victim_email_asset(self, unique_id, name, type):
        url = '/v2/victims/{}/victimAssets/emailAddresses'.format(unique_id)
        return self.tcex.session.post(url, json={'address': name, 'addressType': type})

    def add_victim_network_asset(self, unique_id, name, type):
        url = '/v2/victims/{}/victimAssets/networkAccounts'.format(unique_id)
        return self.tcex.session.post(url, json={'account': name, 'network': type})

    def add_victim_social_asset(self, unique_id, name, type):
        url = '/v2/victims/{}/victimAssets/socialNetworks'.format(unique_id)
        return self.tcex.session.post(url, json={'account': name, 'network': type})

    def add_victim_web_asset(self, unique_id, name):
        url = '/v2/victims/{}/victimAssets/webSites'.format(unique_id)
        return self.tcex.session.post(url, json={'webSite': name})

    def update_victim_phone_asset(self, unique_id, asset_id, name):
        url = '/v2/victims/{}/victimAssets/phoneNumbers/{}'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'phoneType': name})

    def update_victim_email_asset(self, unique_id, asset_id, name, type):
        url = '/v2/victims/{}/victimAssets/emailAddresses/{}'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'address': name, 'addressType': type})

    def update_victim_network_asset(self, unique_id, asset_id, name, type):
        url = '/v2/victims/{}/victimAssets/networkAccounts/{}'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'account': name, 'network': type})

    def update_victim_social_asset(self, unique_id, asset_id, name, type):
        url = '/v2/victims/{}/victimAssets/socialNetworks/asset_id'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'account': name, 'network': type})

    def update_victim_web_asset(self, unique_id, asset_id, name):
        url = '/v2/victims/{}/victimAssets/webSites/{}'.format(unique_id, asset_id)
        return self.tcex.session.post(url, json={'webSite': name})

    def victim(self, type, sub_type, unique_id, victim_id):
        if not sub_type:
            url = '/v2/{}/{}/victims/{}'.format(type, unique_id, victim_id)
        else:
            url = '/v2/{}/{}/{}/victims/{}'.format(type, sub_type, unique_id, victim_id)

        return self.tcex.session.get(url)

    def victims(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/victims'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victims'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def victim_assets(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def victim_email_assets(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/emailAddresses'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/emailAddresses'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def victim_network_assets(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/networkAccounts'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/networkAccounts'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def victim_phone_assets(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/phoneNumbers'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/phoneNumbers'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def victim_social_assets(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/socialNetworks'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/socialNetworks'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def victim_web_assets(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/webSites'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/webSites'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def victim_email_asset(self, type, sub_type, unique_id, asset_id, action='GET'):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/emailAddresses/{}'.format(type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/emailAddresses/{}'.format(type, sub_type, unique_id, asset_id)

        if action == 'GET':
            return self.tcex.session.get(url)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        return None

    def victim_network_asset(self, type, sub_type, unique_id, asset_id, action='GET'):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/networkAccounts/{}'.format(type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/networkAccounts/{}'.format(type, sub_type, unique_id, asset_id)

        if action == 'GET':
            return self.tcex.session.get(url)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        return None

    def victim_phone_asset(self, type, sub_type, unique_id, asset_id, action='GET'):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/phoneNumbers/{}'.format(type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/phoneNumbers/{}'.format(type, sub_type, unique_id, asset_id)

        if action == 'GET':
            return self.tcex.session.get(url)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        return None

    def victim_social_asset(self, type, sub_type, unique_id, asset_id, action='GET'):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/socialNetworks/{}'.format(type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/socialNetworks/{}'.format(type, sub_type, unique_id, asset_id)

        if action == 'GET':
            return self.tcex.session.get(url)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        return None

    def victim_web_asset(self, type, sub_type, unique_id, asset_id, action='GET'):
        if not sub_type:
            url = '/v2/{}/{}/victimAssets/webSites/{}'.format(type, unique_id, asset_id)
        else:
            url = '/v2/{}/{}/{}/victimAssets/webSites/{}'.format(type, sub_type, unique_id, asset_id)

        if action == 'GET':
            return self.tcex.session.get(url)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        return None

    def get_victim_email_asset(self, type, sub_type, unique_id, asset_id):
        return self.victim_email_asset(type, sub_type, unique_id, asset_id)

    def get_victim_network_asset(self, type, sub_type, unique_id, asset_id):
        return self.victim_network_asset(type, sub_type, unique_id, asset_id)

    def get_victim_phone_asset(self, type, sub_type, unique_id, asset_id):
        return self.victim_phone_asset(type, sub_type, unique_id, asset_id)

    def get_victim_social_asset(self, type, sub_type, unique_id, asset_id):
        return self.victim_social_asset(type, sub_type, unique_id, asset_id)

    def get_victim_web_asset(self, type, sub_type, unique_id, asset_id):
        return self.victim_web_asset(type, sub_type, unique_id, asset_id)

    def delete_victim_email_asset(self, type, sub_type, unique_id, asset_id):
        return self.victim_email_asset(type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_network_asset(self, type, sub_type, unique_id, asset_id):
        return self.victim_network_asset(type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_phone_asset(self, type, sub_type, unique_id, asset_id):
        return self.victim_phone_asset(type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_social_asset(self, type, sub_type, unique_id, asset_id):
        return self.victim_social_asset(type, sub_type, unique_id, asset_id, action='DELETE')

    def delete_victim_web_asset(self, type, sub_type, unique_id, asset_id):
        return self.victim_web_asset(type, sub_type, unique_id, asset_id, action='DELETE')

    def tag(self, type, sub_type, unique_id, tag, action='GET'):
        action = action.upper()
        tag_url = '/v2/{}/{}/{}/tags/{}'.format(type, sub_type, unique_id, quote(tag))
        if action == 'ADD':
            return self.tcex.session.post(tag_url)
        elif action == 'DELETE':
            return self.tcex.session.delete(tag_url)
        elif action == 'GET':
            return self.tcex.session.get(tag_url)
        else:
            self.tcex.log.error('_tags error')
        return

    def add_tag(self, type, sub_type, unique_id, tag):
        return self.tag(type, sub_type, unique_id, tag, action='ADD')

    def delete_tag(self, type, sub_type, unique_id, tag):
        return self.tag(type, sub_type, unique_id, tag, action='DELETE')

    def get_tag(self, type, sub_type, unique_id, tag):
        return self.tag(type, sub_type, unique_id, tag)

    def tags(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/tags'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/tags'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def labels(self, type, sub_type, unique_id):
        if not sub_type:
            url = '/v2/{}/{}/securityLabels'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/securityLabels'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url)

    def add_label(self, type, sub_type, unique_id, label):
        return self.label(type, sub_type, unique_id, label, action='ADD')

    def get_label(self, type, sub_type, unique_id, label):
        return self.label(type, sub_type, unique_id, label, action='GET')

    def delete_label(self, type, sub_type, unique_id, label):
        return self.label(type, sub_type, unique_id, label, action='DELETE')

    def label(self, type, sub_type, unique_id, label, action='ADD'):
        action = action.upper()

        if not sub_type:
            url = '/v2/{}/{}/securityLabels/{}'.format(type, unique_id, quote(label))
        else:
            url = '/v2/{}/{}/{}/securityLabels/{}'.format(type, sub_type, unique_id, quote(label))

        if action == 'ADD':
            return self.tcex.session.post(url)

        if action == 'DELETE':
            return self.tcex.session.delete(url)

        if action == 'GET':
            return self.tcex.session.get(url)

        return None

    def attributes(self, type, sub_type, unique_id, includes=None, include_additional=False):
        params = {}
        if includes:
            params['includes'] = includes.join(',')
        if include_additional:
            params['includeAdditional'] = include_additional

        if not sub_type:
            url = '/v2/{}/{}/attributes'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/attributes'.format(type, sub_type, unique_id)

        return self.tcex.session.get(url, params=params)

    def attribute(self, type, sub_type, unique_id, attribute_id, action='GET'):
        action = action.upper()
        if not sub_type:
            url = '/v2/{}/{}/attributes/{}'.format(type, unique_id, attribute_id)
        else:
            url = '/v2/{}/{}/{}/attributes/{}'.format(type, sub_type, unique_id, attribute_id)

        if action == 'GET':
            return self.tcex.session.get(url)

        if action == 'DELETE':
            return self.tcex.session.delete(url)

        return None

    def get_attribute(self, type, sub_type, unique_id, attribute_id):
        return self.attribute(type, sub_type, unique_id, attribute_id)

    def delete_attribute(self, type, sub_type, unique_id, attribute_id):
        return self.attribute(type, sub_type, unique_id, attribute_id, action='DELETE')

    def add_attribute(self, type, sub_type, unique_id, attribute_type, attribute_value):
        if not sub_type:
            url = '/v2/{}/{}/attributes'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}/attributes'.format(type, sub_type, unique_id)

        return self.tcex.session.post(url, json={'type': attribute_type, 'value': attribute_value})

    def attribute_labels(self, type, sub_type, unique_id, attribute_id):
        if not sub_type:
            url = '/v2/{}/{}/attributes/{}/securityLabels'.format(type, unique_id, attribute_id)
        else:
            url = '/v2/{}/{}/{}/attributes/{}/securityLabels'.format(type, sub_type, unique_id, attribute_id)

        return self.tcex.session.get(url)

    def attribute_label(self, type, sub_type, unique_id, attribute_id, label, action='GET'):
        action = action.upper()

        if not sub_type:
            url = '/v2/{}/{}/attributes/{}/securityLabels/{}'.format(type, unique_id, attribute_id, quote(label))
        else:
            url = '/v2/{}/{}/{}/attributes/{}/securityLabels/{}'.format(type, sub_type, unique_id, attribute_id,
                                                                        quote(label))
        if action == 'ADD':
            return self.tcex.session.post(url)

        if action == 'DELETE':
            return self.tcex.session.delete(url)

        if action == 'GET':
            return self.tcex.session.get(url)

        return None

    def get_attribute_label(self, type, sub_type, unique_id, attribute_id, label):
        return self.attribute_label(type, sub_type, unique_id, attribute_id, label)

    def delete_attribute_label(self, type, sub_type, unique_id, attribute_id, label):
        return self.attribute_label(type, sub_type, unique_id, attribute_id, label, action='DELETE')

    def add_attribute_label(self, type, sub_type, unique_id, attribute_id, label):
        return self.attribute_label(type, sub_type, unique_id, attribute_id, label, action='ADD')

    def adversary_assets(self, type, sub_type, unique_id):
        url = '/v2/{}/{}/{}/adversaryAssets'.format(type, sub_type, unique_id)
        return self.tcex.session.get(url)

    def adversary_handle_assets(self, type, sub_type, unique_id):
        url = '/v2/{}/{}/{}/adversaryAssets/handles'.format(type, sub_type, unique_id)
        return self.tcex.session.get(url)

    def adversary_phone_assets(self, type, sub_type, unique_id):
        url = '/v2/{}/{}/{}/adversaryAssets/phoneNumbers'.format(type, sub_type, unique_id)
        return self.tcex.session.get(url)

    def adversary_url_assets(self, type, sub_type, unique_id):
        url = '/v2/{}/{}/{}/adversaryAssets/urls'.format(type, sub_type, unique_id)
        return self.tcex.session.get(url)

    def adversary_url_asset(self, type, sub_type, unique_id, asset_id, action='GET'):
        url = '/v2/{}/{}/{}/adversaryAssets/urls/{}'.format(type, sub_type, unique_id, asset_id)

        if action == 'GET':
            return self.tcex.session.get(url)
        if action == 'DELETE':
            return self.tcex.session.delete(url)

    def get_adversary_url_asset(self, type, sub_type, unique_id, asset_id):
        return self.adversary_url_asset(type, sub_type, unique_id, asset_id)

    def delete_adversary_url_asset(self, type, sub_type, unique_id, asset_id):
        return self.adversary_url_asset(type, sub_type, unique_id, asset_id, action='DELETE')

    def add_adversary_url_asset(self, type, sub_type, unique_id, name):
        asset_url = '/v2/{}/{}/{}/urls'.format(type, sub_type, unique_id)
        asset = {'url': name}
        return self.tcex.session.post(asset_url, json=asset)

    def adversary_phone_asset(self, type, sub_type, unique_id, asset_id, action='GET'):
        url = '/v2/{}/{}/{}/adversaryAssets/phoneNumbers/{}'.format(type, sub_type, unique_id, asset_id)

        if action == 'GET':
            return self.tcex.session.get(url)
        if action == 'DELETE':
            return self.tcex.session.delete(url)

    def get_adversary_phone_asset(self, type, sub_type, unique_id, asset_id):
        return self.adversary_phone_asset(type, sub_type, unique_id, asset_id)

    def delete_adversary_phone_asset(self, type, sub_type, unique_id, asset_id):
        return self.adversary_phone_asset(type, sub_type, unique_id, asset_id, action='DELETE')

    def add_adversary_phone_asset(self, type, sub_type, unique_id, name):
        asset_url = '/v2/{}/{}/{}/phoneNumbers'.format(type, sub_type, unique_id)
        asset = {'phoneNumber': name}
        return self.tcex.session.post(asset_url, json=asset)

    def adversary_handler_asset(self, type, sub_type, unique_id, asset_id, action='GET'):
        url = '/v2/{}/{}/{}/adversaryAssets/handles/{}'.format(type, sub_type, unique_id, asset_id)

        if action == 'GET':
            return self.tcex.session.get(url)
        if action == 'DELETE':
            return self.tcex.session.delete(url)

    def get_adversary_handler_asset(self, type, sub_type, unique_id, asset_id):
        return self.adversary_handler_asset(type, sub_type, unique_id, asset_id)

    def delete_adversary_handler_asset(self, type, sub_type, unique_id, asset_id):
        return self.adversary_handler_asset(type, sub_type, unique_id, asset_id, action='DELETE')

    def add_adversary_handler_asset(self, type, sub_type, unique_id, name):
        asset_url = '/v2/{}/{}/{}/handles'.format(type, sub_type, unique_id)
        asset = {'handle': name}
        return self.tcex.session.post(asset_url, json=asset)

    def assignees(self, type, sub_type, unique_id):
        url = '/v2/{}/{}/{}/assignees'.format(type, sub_type, unique_id)
        return self.tcex.session.get(url)

    def assignee(self, type, sub_type, unique_id, assignee_id, action='GET'):
        url = '/v2/{}/{}/{}/assignees/{}'.format(type, sub_type, unique_id, assignee_id)
        if action == 'GET':
            return self.tcex.session.get(url)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        if action == 'ADD':
            return self.tcex.session.get(url)

    def get_assignee(self, type, sub_type, unique_id, assignee_id):
        return self.assignee(type, sub_type, unique_id, assignee_id)

    def delete_assignee(self, type, sub_type, unique_id, assignee_id):
        return self.assignee(type, sub_type, unique_id, assignee_id, action='DELETE')

    def add_assignee(self, type, sub_type, unique_id, assignee_id):
        return self.assignee(type, sub_type, unique_id, assignee_id, action='ADD')

    def escalatees(self, type, sub_type, unique_id):
        url = '/v2/{}/{}/{}/escalatees'.format(type, sub_type, unique_id)
        return self.tcex.session.get(url)

    def escalatee(self, type, sub_type, unique_id, escalatee_id, action='GET'):
        url = '/v2/{}/{}/{}/escalatees/{}'.format(type, sub_type, unique_id, escalatee_id)
        if action == 'GET':
            return self.tcex.session.get(url)
        if action == 'DELETE':
            return self.tcex.session.get(url)
        if action == 'ADD':
            return self.tcex.session.get(url)

    def get_escalatee(self, type, sub_type, unique_id, escalatee_id):
        return self.escalatee(type, sub_type, unique_id, escalatee_id)

    def delete_escalatee(self, type, sub_type, unique_id, escalatee_id):
        return self.escalatee(type, sub_type, unique_id, escalatee_id, action='DELETE')

    def add_escalatee(self, type, sub_type, unique_id, escalatee_id):
        return self.escalatee(type, sub_type, unique_id, escalatee_id, action='ADD')

    @staticmethod
    def construct_params(items):
        params = {}
        for arg, value in items:
            params[arg] = value

        return params

    @staticmethod
    def success(r):
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
