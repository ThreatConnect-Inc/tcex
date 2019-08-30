# -*- coding: utf-8 -*-
"""ThreatConnect Token Module."""
import os
from requests import Session
from tcex.sessions.tc_session import HmacAuth


class TcToken(object):
    """ThreatConnect Token App"""

    def __init__(self):
        """Initialize class properties."""

        # properties
        api_access_id = os.getenv('API_ACCESS_ID')
        api_secret_key = os.getenv('API_SECRET_KEY')
        self.tc_api_path = os.getenv('TC_API_PATH')
        self.tc_token_url = os.getenv('TC_TOKEN_URL')
        self.tc_token_svc_id = os.getenv('TC_TOKEN_SVC_ID')

        # get a requests session and set hmac auth to use in retrieving tokens.
        self.session = Session()
        self.session.auth = HmacAuth(api_access_id, api_secret_key)

    @property
    def api_token(self):
        """Get a valid TC api token."""
        r = self.session.post('{}{}api'.format(self.tc_api_path, self.tc_token_url), verify=False)
        if r.status_code != 200:
            raise RuntimeError('This feature requires ThreatConnect 6.0 or higher.')
        return r.json().get('data')

    @property
    def service_token(self):
        """Get a valid TC service token.

        TC_TOKEN_SVC_ID is the ID field from the appcatalogitem table for a service App.
        TC_TOKEN_URL is the API endpoint to get a TOKEN.
        """
        data = {'serviceId': os.getenv('TC_TOKEN_SVC_ID')}
        r = self.session.post(
            '{}{}svc'.format(self.tc_api_path, self.tc_token_url), json=data, verify=False
        )
        if r.status_code != 200:
            raise RuntimeError('This feature requires ThreatConnect 6.0 or higher.')
        return r.json().get('data')
