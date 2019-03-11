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

        print('url: [{}]'.format(url))
        print('data: [{}]'.format(data))

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
        print('url: {}'.format(url))
        print('data: {}'.format(data))
        return self.tcex.session.put(url, json=data)

    def get(self, type, sub_type, unique_id, **kwargs):
        params = self.construct_params(kwargs.items())
        if not sub_type:
            url = '/v2/{}/{}'.format(type, unique_id)
        else:
            url = '/v2/{}/{}/{}'.format(type, sub_type, unique_id)
        return self.tcex.session.get(url, params=params)

    def tag(self, type, sub_type, unique_id, tag, action='CREATE'):
        action = action.upper()

        tag_url = '/v2/{}/{}/{}/tags/{}'.format(type, sub_type, unique_id, quote(tag))
        if action == 'CREATE':
            return self.tcex.session.post(tag_url)
        elif action == 'DELETE':
            return self.tcex.session.delete(tag_url)
        else:
            self.tcex.log.error('_tags error')
        return

    def adversary_asset(self, type, sub_type, unique_id, asset_type, asset_name, asset_id=None, action='CREATE'):
        action = action.upper()
        asset_type = asset_type.upper()

        asset_url = ''
        asset = {}

        if asset_type == 'HANDLER':
            asset_url = '/v2/{}/{}/{}/handlers'.format(type, sub_type, unique_id)
            asset = {'handle': asset_name}
        elif asset_type == 'PHONE':
            asset_url = '/v2/{}/{}/{}/phoneNumbers'.format(type, sub_type, unique_id)
            asset = {'phoneNumber': asset_name}
        elif asset_type == 'URL':
            asset_url = '/v2/{}/{}/{}/urls'.format(type, sub_type, unique_id)
            asset = {'url': asset_name}
        else:
            print('Invalid type')
            return

        if action == 'CREATE':
            return self.tcex.session.post(asset_url, json=asset)
        elif action == 'UPDATE':
            asset_url += '/{}'.format(asset_id)
            return self.tcex.session.put(asset_url, json=asset)
        elif action == 'DELETE':
            asset_url += '/{}'.format(asset_id)
            return self.tcex.session.delete(asset_url)
        else:
            self.tcex.log.error('invalid action error')
            return

    def adversary_assets(self, type, sub_type, unique_id, asset_type, **kwargs):
        params = self.construct_params(kwargs.items())

        if not asset_type:
            url = '/v2/{}/{}/{}/adversaryAssets'.format(type, sub_type, unique_id)
        elif asset_type == 'PHONE':
            url = '/v2/{}/{}/{}/adversaryAssets/phoneNumbers'.format(type, sub_type, unique_id)
        elif asset_type == 'HANDLER':
            url = '/v2/{}/{}/{}/adversaryAssets/handles'.format(type, sub_type, unique_id)
        elif asset_type == 'URL':
            url = '/v2/{}/{}/{}/adversaryAssets/urls'.format(type, sub_type, unique_id)
        else:
            print('invalid adversary asset type')
            return

        return self.tcex.session.get(url, params=params)

    @staticmethod
    def _victim_asset_base_url(unique_id, asset_type):
        asset_type = asset_type.upper()
        if asset_type == 'PHONE':
            return '/v2/victims/{}/victimAssets/phoneNumbers'.format(unique_id)
        elif asset_type == 'WEBSITE':
            return '/v2/victims/{}/victimAssets/webSites'.format(unique_id)
        elif asset_type == 'NETWORK':
            return '/v2/victims/{}/victimAssets/networkAccounts'.format(unique_id)
        elif asset_type == 'EMAIL':
            return '/v2/victims/{}/victimAssets/emailAddresses'.format(unique_id)
        elif asset_type == 'SOCIAL':
            return '/v2/victims/{}/victimAssets/socialNetworks'.format(unique_id)

        return ''

    def victim_asset(self, unique_id, asset_type, name, type=None, id=None, action='CREATE'):
        url = self._victim_asset_base_url(type, unique_id, asset_type)
        action = action.upper()
        asset = {}
        if asset_type == 'PHONE':
            asset = {'phoneType': name}
        elif asset_type == 'WEBSITE':
            asset = {'webSite': name}
        elif asset_type == 'NETWORK':
            asset = {'account': name, 'network': type}
        elif asset_type == 'EMAIL':
            asset = {'address': name, 'addressType': type}
        elif asset_type == 'SOCIAL':
            asset = {'account': name, 'network': type}
        else:
            print('invalid asset_type for victim_asset')
            return

        if action == 'CREATE':
            return self.tcex.session.post(url, json=asset)
        elif action == 'UPDATE':
            url += '/{}'.format(id)
            return self.tcex.session.put(url, json=asset)
        elif action == 'DELETE':
            url += '/{}'.format(id)
            return self.tcex.session.delete(url)
        else:
            print('invalid action for victim_phone_asset')
            return

    def attribute(self, type, sub_type, unique_id, attribute_type, value, attribute_id=None, action='CREATE'):
        action = action.upper()

        if action == 'CREATE':
            if not sub_type:
                url = '/v2/{}/{}/attributes'.format(type, unique_id)
            else:
                url = '/v2/{}/{}/{}/attributes'.format(type, sub_type, unique_id)
            print(url)
            return self.tcex.session.post(url, json={'type': attribute_type, 'value': value})
        elif action == 'DELETE':
            if not sub_type:
                url = '/v2/{}/{}/attributes/{}'.format(type, unique_id, attribute_id)
            else:
                url = '/v2/{}/{}/{}/attributes/{}'.format(type, sub_type, unique_id, attribute_id)
            return self.tcex.session.delete(url)
        else:
            self.tcex.log.error('_attribute error')

    def attribute_label(self, type, sub_type, unique_id, attribute_id, label, action='CREATE'):
        action = action.upper()

        if not sub_type:
            url = '/v2/{}/{}/attributes/{}/securityLabels/{}'.format(type, unique_id, attribute_id, quote(label))
        else:
            url = '/v2/{}/{}/{}/attributes/{}/securityLabels/{}'.format(type, sub_type, unique_id, attribute_id,
                                                                        quote(label))
        print(url)

        if action == 'CREATE':
            return self.tcex.session.post(url)

        if action == 'DELETE':
            return self.tcex.session.delete(url)

        return None

    def label(self, type, sub_type, unique_id, label, action='CREATE'):
        action = action.upper()

        if not sub_type:
            url = '/v2/{}/{}/securityLabels/{}'.format(type, unique_id, quote(label))
        else:
            url = '/v2/{}/{}/{}/securityLabels/{}'.format(type, sub_type, unique_id, quote(label))

        print(url)
        if action == 'CREATE':
            return self.tcex.session.post(url)

        if action == 'DELETE':
            return self.tcex.session.delete(url)

        return None

    def upload(self, type, sub_type, unique_id, data, update_if_exists=True):
        update_if_exists = data.get('update_if_exists', update_if_exists)
        url = '/v2/{}/{}/{}/upload?updateIfExists={}'.format(type, sub_type, unique_id, update_if_exists)
        return self.tcex.session.post(url)

    def observations(self, type, sub_type, unique_id, data):
        url = '/v2/{}/{}/{}/observations'.format(type, sub_type, unique_id)
        return self.tcex.session.post(url, json=data)

    def create_false_positive(self, type, sub_type, unique_id):
        unique_id = quote_plus(unique_id)
        url = '/v2/{}/{}/{}/falsePositive'.format(type, sub_type, unique_id)

        return self.tcex.session.post(url)

    def association(self, type, sub_type, unique_id, target_type, target_sub_type, target_unique_id, action='CREATE'):
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

        if action == 'CREATE':
            return self.tcex.session.post(url)
        elif action == 'DELETE':
            return self.tcex.session.delete(url)
        else:
            self.tcex.log.error('associations error')
            return

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
