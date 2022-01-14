"""TcEx Framework Service module"""
# standard library
import threading
import time
from typing import Optional

# third-party
from requests import Session, exceptions
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils import Utils


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
    """Service methods for customer Service (e.g., Triggers)."""

    def __init__(
        self,
        token_url: str,
        sleep_interval: int,
        verify: bool,
        logger: object,
        proxies: Optional[dict],
    ):
        """Initialize the Class properties.

        Args:
            token_url: The ThreatConnect URL for token renewal.
            sleep_interval: Token monitor sleep interval.
            verify: A boolean to enable/disable SSL verification.
            logger: An pre-configured instance of a logger.
            proxies: Optional proxy settings.
        """
        self.token_url = token_url
        self.sleep_interval = sleep_interval
        self.log = logger
        self.verify = verify

        # properties
        self.lock = threading.Lock()
        # session with retry for token renewal
        self.session: Session = retry_session()
        # add proxies
        self.session.proxies = proxies
        # shutdown boolean
        self.shutdown = False
        # token map for storing keys -> tokens -> threads
        self.token_map = {}
        # amount of seconds to pad before token renewal
        self.token_window = 600
        self.utils = Utils

        # start token renewal process
        self.token_renewal()

    @property
    def key(self) -> str:
        """Return the current key"""
        key = 'MainThread'  # default Python parent thread name
        if self.thread_name in self.token_map:
            # for Job, Playbook, and ApiService Apps the key is the thread name.
            key: str = self.thread_name
        elif self.trigger_id in self.token_map:
            key: str = self.trigger_id
        return key

    def register_token(self, key: str, token: str, expires: int) -> None:
        """Register a token.

        Args:
            key: The key to use to identify a token. Typically a thread name or a config id.
            token: The ThreatConnect API token.
            expires: The token expiration timestamp.
        """
        if token is None or expires is None:  # pragma: no cover
            self.log.error(
                'feature=token, event=invalid-token-data, '
                f'token="{self.utils.printable_cred(token, 10)}", '
                f'expires={expires}.'
            )
            return

        self.token_map[key] = {'token': token, 'token_expires': int(expires)}
        self.log.info(
            f'feature=token, action=token-register, key={key}, '
            f'token="{self.utils.printable_cred(token, 10)}", '
            f'expiration={expires}'
        )

    def renew_token(self, token: str) -> None:
        """Renew expired ThreatConnect Token.

        This method will renew a token and update the token_map with new token and expiration.

        Args:
            token: The ThreatConnect API token.
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
                    f'feature=token, event=token-retry-error, status_code={r.status_code}, '
                    f'api-message={err_reason}, '
                    f'token="{self.utils.printable_cred(token, 10)}".'
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
    def thread_name(self) -> str:
        """Return the current thread name."""
        return threading.current_thread().name

    @property
    def token(self) -> Optional[str]:
        """Return token for current thread."""
        return self.token_map.get(self.key, {}).get('token')

    @token.setter
    def token(self, token: str) -> None:
        """Set token for current thread."""
        self.token_map.setdefault(self.key, {})['token'] = token

    @property
    def token_expires(self) -> Optional[int]:
        """Return token_expires for current thread."""
        return self.token_map.get(self.key, {}).get('token_expires')

    @token_expires.setter
    def token_expires(self, expires) -> None:
        """Set token expires for current thread."""
        self.token_map.setdefault(self.key, {})['token_expires'] = int(expires)

    def token_renewal(self) -> None:
        """Start token renewal monitor thread."""
        t = threading.Thread(name='token-renewal', target=self.token_renewal_monitor, daemon=True)
        t.start()

    def token_renewal_monitor(self) -> None:
        """Monitor token expiration and renew when required."""
        self.log.debug('feature=token, event=renewal-monitor-started')
        while True:
            for key, token_data in dict(self.token_map).items():
                # calculate the time left to sleep
                sleep_seconds = (
                    token_data.get('token_expires') - int(time.time()) - self.token_window
                )
                self.log.debug(
                    '''feature=token, '''
                    f'''event=token-status, key={key}, '''
                    f'''token="{self.utils.printable_cred(token_data.get('token'), 10)}", '''
                    f'''expires={token_data.get('token_expires')}, '''
                    f'''sleep-seconds={sleep_seconds}'''
                )

                if sleep_seconds > 0:
                    continue

                # renew token data
                with self.lock:
                    try:
                        api_token_data = self.renew_token(token_data.get('token'))
                        self.token_map[key]['token'] = api_token_data['apiToken']
                        self.token_map[key]['token_expires'] = int(
                            api_token_data['apiTokenExpires']
                        )
                        self.log.info(
                            f'''feature=token, action=token-renewed, key={key}, token='''
                            f'''"{self.utils.printable_cred(api_token_data['apiToken'], 10)}", '''
                            f'''expires={api_token_data['apiTokenExpires']}'''
                        )
                    except RuntimeError as e:
                        self.log.error(e)
                        try:
                            del self.token_map[key]
                            self.log.error(f'feature=token, event=token-removal-failure, key={key}')
                        except KeyError:  # pragma: no cover
                            pass
            time.sleep(self.sleep_interval)
            if self.shutdown:
                break

    @property
    def trigger_id(self) -> Optional[int]:
        """Return the current trigger_id."""
        trigger_id = None
        if hasattr(threading.current_thread(), 'trigger_id'):
            trigger_id = threading.current_thread().trigger_id
        if trigger_id is not None:
            trigger_id = int(trigger_id)
        return trigger_id

    def unregister_token(self, key: str) -> None:
        """Unregister a token.

        Args:
            key (str): The key used to identify a token.
        """
        try:
            del self.token_map[key]
            self.log.info(f'feature=token, action=token-unregister, key={key}')
        except KeyError:
            pass
