# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
import threading
import time
from requests import exceptions, get


class Tokens(object):
    """Service methods for customer Service (e.g., Triggers).

    Args:
        token (str): The ThreatConnect API token
        token_expires (int): The API token expiration timestamp
        token_url (str): The ThreatConnect URL
        verify (bool): A boolean to enable/disable SSL verification
        logger (logging.logger): An pre-configured instance of a logger.
    """

    def __init__(self, token, token_expires, token_url, verify, logger):
        """Initialize the Class properties."""
        self.default_token = token
        self.default_token_expires = token_expires
        self.lock = threading.Lock()
        self.log = logger
        self.token_map = {'MainThread': {'token': token, 'token_expires': token_expires}}
        self.token_url = token_url
        self.token_window = 60  # amount of seconds to pad before token renewal
        self.verify = verify

    def _renew_token(self, retry=True):
        """Renew expired ThreatConnect Token.

        This method will renew a token an update the token_map with new token and expiration.

        Args:
            retry (bool, optional): If True the renewal will be retried. Defaults to True.
        """
        self.log.in_token_renewal = True

        # log token information
        current_token = self.token_map.get(self.key, {}).get('token')
        self.log.info('Renewing ThreatConnect Token')
        self.log.debug(
            'token: {}, token_expires: {}'.format(
                self.printable_token(current_token), self.token_expires
            )
        )

        try:
            # get token directly from token map
            params = {'expiredToken': current_token}
            url = '{}/appAuth'.format(self.token_url)
            r = get(url, params=params, verify=self.verify)

            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                if retry:
                    time.sleep(5)
                    self._renew_token(False)
                else:
                    err_reason = r.text or r.reason
                    err_msg = 'Token Retry Error. API status code: {}, API message: {}.'.format(
                        r.status_code, err_reason
                    )
                    self.log.error(err_msg)
                    raise RuntimeError(1042, err_msg)
        except exceptions.SSLError:  # pragma: no cover
            raise RuntimeError('Token renewal failed with an SSL Error.')

        # process response for token
        try:
            data = r.json()
            self.token = data['apiToken']  # cause exception if not available
            self.token_expires = int(data['apiTokenExpires'])
            self.log.info(
                'New token data - token: {}, token_expires: {}'.format(
                    self.printable_token(data['apiToken']), data['apiTokenExpires']
                )
            )
        except (AttributeError, ValueError) as e:  # pragma: no cover
            self.log.warning('Token renewal failed: {}'.format(e))
            if retry:
                # retry token renewal
                time.sleep(5)
                self._renew_token(False)
        finally:
            if retry:
                self.log.in_token_renewal = False

    @property
    def key(self):
        """Return the current key"""
        key = 'MainThread'  # default for non threaded Apps
        self.log.trace('in key - thread_name: {}'.format(self.thread_name))
        if self.thread_name in self.token_map:
            # for non-threaded Apps and ApiService Apps the key is the thread name.
            key = self.thread_name
        else:
            # for TriggerService and WebhookTriggerService check for thread name in dict
            for k, d in self.token_map.items():
                if self.thread_name in d.get('thread_names', []):
                    key = k
                    break
            else:  # pragma: no cover
                self.log.warning('Thread name not found, defaulting to {}'.format(key))
        return key

    @staticmethod
    def printable_token(token):
        """Return a printable token"""
        return '{}...{}'.format(token[:10], token[-10:])

    def register_thread(self, key, thread_name):
        """Register a thread name to a key.

        Args:
            key (str): The key to use to identify a token.
            thread_name (str): The thread to register to a key.
        """
        self.token_map.setdefault(key, {}).setdefault('thread_names', []).append(thread_name)
        self.log.debug('token thread {} registered for key {}'.format(thread_name, key))

    def register_token(self, key, token, expires):
        """Register a token.

        Args:
            key (str): The key to use to identify a token.
            token (str): The ThreatConnect API token.
            expires (int): The token expiration timestamp.
        """
        if token is None or expires is None:
            raise RuntimeError('Invalid token data provided.')  # pragma: no cover

        self.token_map[key] = {'thread_names': [], 'token': token, 'token_expires': expires}
        self.log.debug(
            'token {} registered for key {} with expiration of {}'.format(
                self.printable_token(token), key, expires
            )
        )

    @property
    def thread_name(self):
        """Return the current thread name."""
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
        return self.token_map.get(self.key, {}).get('token_expires')

    @token_expires.setter
    def token_expires(self, expires):
        """Set token expires for current thread."""
        self.token_map.setdefault(self.key, {})['token_expires'] = expires

    def unregister_thread(self, key, thread_name):
        """Unregister a thread name for a key.

        Args:
            key (str): The key to use to identify a token.
            thread_name (str): The thread to unregister from a key.
        """
        try:
            self.token_map[key]['thread_names'].remove(thread_name)
            self.log.debug('token thread {} unregistered for key {}'.format(thread_name, key))
        except (KeyError, ValueError):  # pragma: no cover
            pass

    def unregister_token(self, key):
        """Unregister a token.

        Args:
            key (str): The key to use to identify a token.
        """
        try:
            del self.token_map[key]
            self.log.debug('token unregistered for key {}'.format(key))
        except KeyError:
            pass
