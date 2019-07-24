# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
import threading
import time
from requests import exceptions, get


class Token(object):
    """Service methods for customer Service (e.g., Triggers)."""

    def __init__(self, token, token_expires, token_url, verify, logger):
        """Initialize the Class properties."""
        self.default_token = token
        self.default_token_expires = token_expires
        self.lock = threading.Lock()
        self.log = logger
        self.token_map = {
            'MainThread': {'renewing': False, 'token': token, 'token_expires': token_expires}
        }
        self.token_url = token_url
        self.token_window = 60  # amount of seconds to pad before token renewal
        self.renewing = False
        self.verify = verify

    def _renew_token(self, retry=True):
        """Renew expired ThreatConnect Token."""
        self.log.in_token_renew = True
        self.renewing = True

        # log token information
        self.log.info('Renewing ThreatConnect Token')
        self.log.info('Current Token Expiration: {}'.format(self.token_expires))

        try:
            # get token directly from token map
            params = {'expiredToken': self.token_map.get(threading.get_ident(), {}).get('token')}
            url = '{}/appAuth'.format(self.token_url)
            r = get(url, params=params, verify=self.verify)

            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                self._renew_token_handle_error(r, retry)

            # process response for token
            data = r.json()
            if retry and (data.get('apiToken') is None or data.get('apiTokenExpires') is None):
                # add retry logic to handle case if the token renewal doesn't return valid data
                warn_msg = 'Token Retry Error: no values for apiToken or apiTokenExpires ({}).'
                self.log.warning(warn_msg.format(r.text))
                self._renew_token(False)
            else:
                self.token = data.get('apiToken')
                self.token_expires = int(data.get('apiTokenExpires'))
                self.log.info('New Token Expiration: {}'.format(self.token_expires))
            self.renewing = False
        except exceptions.SSLError:
            self.log.error('SSL Error during token renewal.')
            self.renewing = False
        finally:
            self.log.in_token_renew = False

    def _renew_token_handle_error(self, r, retry):
        """Handle errors during token renewal."""
        # TODO: Update this logic
        if (  # pylint: disable=no-else-raise
            r.status_code == 401
            and 'application/json' in r.headers.get('content-type', '')
            and 'Retry token is invalid' in r.json().get('message')
        ):
            # log failure
            err_reason = r.text or r.reason
            err_msg = 'Token Retry Error. API status code: {}, API message: {}.'
            raise RuntimeError(1042, err_msg.format(r.status_code, err_reason))
        elif retry:
            warn_msg = 'Token Retry Error. API status code: {}, API message: {}.'
            self.log.warning(warn_msg.format(r.status_code, r.text))
            # delay and retry token renewal
            time.sleep(15)
            self._renew_token(False)
        else:
            err_reason = r.text or r.reason
            err_msg = 'Token Retry Error. API status code: {}, API message: {}.'
            raise RuntimeError(1042, err_msg.format(r.status_code, err_reason))

    @property
    def key(self):
        """Return the current key."""
        for key, data in self.token_map.items():
            if self.thread_name in data.get('thread_names', []):
                return key
        return 'MainThread'  # return the key from the cli args

    def register_thread(self, key, thread_name):
        """Register a thread name to a key."""
        self.token_map.setdefault(key, {}).setdefault('thread_names', []).append(thread_name)

    def register_token(self, key, token, expires):
        """Register a token for a thread."""
        self.log.trace('thread - token: {}, expires: {}'.format(token, expires))
        self.token_map[key] = {
            'renewing': False,
            'thread_names': [],
            'token': token,
            'token_expires': expires,
        }

    @property
    def renewing(self):
        """Return renewing bool for current thread."""
        # TODO: add lock.acquire / lock.release
        return self.token_map.get(self.key, {}).get('renewing', False)

    @renewing.setter
    def renewing(self, renewing):
        """Set renewing bool for current thread."""
        self.token_map.setdefault(self.key, {})['renewing'] = renewing

    @property
    def thread_name(self):
        """Return a uuid4 session id."""
        return threading.current_thread().name

    @property
    def token(self):
        """Return token for current thread."""
        # handle token renewal
        if self.token_expires is not None and self.token_expires < (
            int(time.time()) + self.token_window
        ):
            self._renew_token()

        return self.token_map.get(self.key, {}).get('token')

    @token.setter
    def token(self, token):
        """Set token for current thread."""
        # TODO: add lock.acquire / lock.release
        self.token_map.setdefault(self.key, {})['token'] = token

    @property
    def token_expires(self):
        """Return token_expires for current thread."""
        # TODO: add lock.acquire / lock.release
        return self.token_map.get(self.key, {}).get('token_expires', int(time.time()) + 3600)

    @token_expires.setter
    def token_expires(self, expires):
        """Set token expires for current thread."""
        self.token_map.setdefault(self.key, {})['token_expires'] = expires

    def unregister_thread(self, key, thread_name):
        """Register a thread name to a key."""
        try:
            self.token_map[key]['thread_names'].remove(thread_name)
        except (KeyError, ValueError):
            pass

    def unregister_thread_token(self, key):
        """Remove a registered token for a thread."""
        try:
            del self.token_map[key]
        except KeyError:
            pass
