# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
# standard library
import threading
import time

# third-party
# from requests import exceptions, get
from requests import Session, exceptions
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def retry_session(retries=3, backoff_factor=0.8, status_forcelist=(500, 502, 504)):
    """Add retry to Requests Session.

    https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry
    """
    session = Session()
    retries = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    # mount all https requests
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session


class Tokens:
    """Service methods for customer Service (e.g., Triggers).

    Args:
        token_url (str): The ThreatConnect URL
        verify (bool): A boolean to enable/disable SSL verification
        logger (logging.logger): An pre-configured instance of a logger.
    """

    def __init__(self, token_url, sleep_interval, verify, logger):
        """Initialize the Class properties."""
        self.lock = threading.Lock()
        # tcex logger
        self.log = logger
        # session with retry for token renewal
        self.session = retry_session()
        # shutdown boolean
        self.shutdown = False
        # token monitor sleep interval
        self.sleep_interval = sleep_interval
        # token map for storing keys -> tokens -> threads
        self.token_map = {}
        # base url for token renewal
        self.token_url = token_url
        # amount of seconds to pad before token renewal
        self.token_window = 60
        # ssl verification setting for TC token renewal
        self.verify = verify

        # start token renewal process
        self.token_renewal()

    @property
    def key(self):
        """Return the current key"""
        key = 'MainThread'  # default Python parent thread name
        # self.log.trace(f'in key - thread_name: {self.thread_name}')
        if self.thread_name in self.token_map:
            # for Job, Playbook, and ApiService Apps the key is the thread name.
            key = self.thread_name
        else:
            # for Trigger and Webhook Apps the key is ConfigId.
            # find ConfigId using array of registered thread names.
            for k, d in self.token_map.items():
                if self.thread_name in d.get('thread_names', []):
                    key = k
                    break
            else:  # pragma: no cover
                self.log.trace(f'Thread name not found, defaulting to {key}')
        return key

    @staticmethod
    def printable_token(token):
        """Return a printable token

        Args:
            token (str): The token to print.

        Returns:
            str: The reformatted token.
        """
        if token is not None:
            token = f'{token[:10]}...{token[-10:]}'
        return token

    def register_thread(self, key, thread_name):
        """Register a thread name to a key.

        For Trigger and Webhook Apps multiple threads will share a token registered to a ConfigId.

        Args:
            key (str): The key to use to identify a token.
            thread_name (str): The thread to register to a key.
        """
        self.token_map.setdefault(key, {}).setdefault('thread_names', []).append(thread_name)
        self.log.info(f'Token thread registered -  key: {key}, thread: {thread_name}')

    def register_token(self, key, token, expires):
        """Register a token.

        Args:
            key (str): The key to use to identify a token. Typically a thread name or a config id.
            token (str): The ThreatConnect API token.
            expires (int): The token expiration timestamp.
        """
        if token is None or expires is None:  # pragma: no cover
            self.log.error(
                f'Invalid token data provided - token: {self.printable_token(token)}, '
                f'expires: {expires}.'
            )
            return

        self.token_map[key] = {'thread_names': [], 'token': token, 'token_expires': int(expires)}
        self.log.info(
            f'Token registered - key: {key}, '
            f'token: {self.printable_token(token)}, '
            f'expiration {expires}'
        )

    def renew_token(self, token):
        """Renew expired ThreatConnect Token.

        This method will renew a token and update the token_map with new token and expiration.

        Args:
            token (str): The ThreatConnect API token.
            token_expires (int): The token expiration timestamp.
        """
        api_token_data = {}
        self.log.in_token_renewal = True  # pause API logging

        # log token information
        try:
            params = {'expiredToken': token}
            url = f'{self.token_url}/appAuth'
            r = self.session.get(url, params=params, verify=self.verify)

            if not r.ok:
                err_reason = r.text or r.reason
                err_msg = (
                    f'Token Retry Error. API status code: {r.status_code}, '
                    f'API message: {err_reason}, '
                    f'Token: {self.printable_token(token)}.'
                )
                self.log.error(err_msg)
                raise RuntimeError(1042, err_msg)
        except exceptions.SSLError:  # pragma: no cover
            raise RuntimeError('Token renewal failed with an SSL Error.')

        # process response for token
        try:
            api_token_data = r.json()
        except (AttributeError, ValueError) as e:  # pragma: no cover
            raise RuntimeError(f'Token renewal failed ({e}).')
        finally:
            self.log.in_token_renewal = False

        return api_token_data

    @property
    def thread_name(self):
        """Return the current thread name."""
        return threading.current_thread().name

    @property
    def token(self):
        """Return token for current thread."""
        return self.token_map.get(self.key, {}).get('token')

    @token.setter
    def token(self, token):
        """Set token for current thread."""
        self.token_map.setdefault(self.key, {})['token'] = token

    @property
    def token_expires(self):
        """Return token_expires for current thread."""
        return self.token_map.get(self.key, {}).get('token_expires')

    @token_expires.setter
    def token_expires(self, expires):
        """Set token expires for current thread."""
        self.token_map.setdefault(self.key, {})['token_expires'] = int(expires)

    def token_renewal(self):
        """Start token renewal monitor thread."""
        self.log.debug('Token renewal monitor starting')
        t = threading.Thread(name='token-renewal', target=self.token_renewal_monitor)
        t.daemon = True  # use setter for py2
        t.start()

    def token_renewal_monitor(self):
        """Monitor token expiration and renew when required."""
        while True:
            for key, token_data in dict(self.token_map).items():
                # calculate the time left to sleep
                sleep_seconds = (
                    token_data.get('token_expires') - int(time.time()) - self.token_window
                )
                self.log.debug(
                    f'token status - key: {key}, '
                    f"token: {self.printable_token(token_data.get('token'))}, "
                    f"expires: {token_data.get('token_expires')}, "
                    f'sleep-seconds: {sleep_seconds}'
                )

                if sleep_seconds < 0:
                    # renew token data
                    with self.lock:
                        try:
                            api_token_data = self.renew_token(token_data.get('token'))
                            self.token_map[key]['token'] = api_token_data['apiToken']
                            self.token_map[key]['token_expires'] = int(
                                api_token_data['apiTokenExpires']
                            )
                            self.log.info(
                                f'Token renewed - key: {key}, '
                                f"token: {self.printable_token(api_token_data['apiToken'])}, "
                                f"expires: {api_token_data['apiTokenExpires']}"
                            )
                        except RuntimeError as e:
                            self.log.error(e)
                            try:
                                del self.token_map[key]
                                self.log.error(f'Failed token removed - key: {key}')
                            except KeyError:  # pragma: no cover
                                pass
            time.sleep(self.sleep_interval)
            if self.shutdown:
                break

    def unregister_thread(self, key, thread_name):
        """Unregister a thread name for a key.

        Args:
            key (str): The key to use to identify a token.
            thread_name (str): The thread to unregister from a key.
        """
        try:
            self.token_map[key]['thread_names'].remove(thread_name)
            self.log.info(f'Token thread unregistered -  key: {key}, thread: {thread_name}')
        except (KeyError, ValueError):  # pragma: no cover
            pass

    def unregister_token(self, key):
        """Unregister a token.

        Args:
            key (str): The key used to identify a token.
        """
        try:
            del self.token_map[key]
            self.log.info(f'Token unregistered - key: {key}')
        except KeyError:
            pass
