"""TcEx Framework Module"""

# standard library
import logging
import os
import threading
import time

# third-party
from requests import Session, exceptions
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# first-party
from tcex.input.field_type.sensitive import Sensitive
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property
from tcex.pleb.exception_thread import ExceptionThread

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


def retry_session(retries=3, backoff_factor=0.8, status_forcelist=(500, 502, 504)):
    """Add retry to Requests Session.

    https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry
    """
    session = Session()
    retries = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,  # type: ignore
        status_forcelist=status_forcelist,
    )
    # mount all https requests
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session


class Token:
    """TcEx Module"""

    def __init__(
        self,
        token_url: str,
        verify: bool = True,
        proxies: dict | None = None,
    ):
        """Initialize the Class properties.

        Args:
            token_url: The ThreatConnect URL for token renewal.
            verify: A boolean to enable/disable SSL verification.
            proxies: A dictionary of proxy settings.
        """
        self.proxies = proxies
        self.token_url = token_url
        self.verify = verify

        # validation for singleton
        if not token_url:  # pragma: no cover
            raise ValueError('A value for token_url is required.')

        # properties
        self._shutdown = False

        # Threading event that is used as a barrier that determines whether a token can be retrieved
        # from this module or not (via the token property). The barrier only blocks access to the
        # token property whenever token renewal is taking place in order to keep from returning
        # stale tokens.
        self._barrier = threading.Event()
        # Setting barrier event to True disables barrier, which makes the token property
        # accessible (default behavior)
        self._barrier.set()
        # threading event that denotes whether renewal monitor should sleep after a renewal cycle
        self._monitor_sleep_interval = threading.Event()
        self.log = _logger
        self.monitor_thread: ExceptionThread
        # session with retry for token renewal
        self.sleep_interval = int(os.getenv('TC_TOKEN_SLEEP_INTERVAL', '150'))
        # token map for storing keys -> tokens -> threads
        self.token_map = {}
        # amount of time to wait before starting renewal process (after enabling barrier)
        # buffer allows any other threads using a token to possibly finish their work
        self.token_renewal_buffer_time = 5
        self.token_window = 600  # seconds to pad before token renewal

        # start token renewal process
        self.token_renewal()

    def get_token(self) -> Sensitive | None:
        """Return token for current thread."""
        # wait until renewal barrier is set to True (meaning no renewal
        # is in progress). If already true, then simply proceed.

        # perform three attempts - safety net in case of heavily overloaded monitor. If
        # we cannot retrieve a token after three attempts, there must be an issue
        for i in range(3):
            if self._barrier.wait(timeout=self.token_renewal_buffer_time + 10):
                return self.token_map.get(self.key, {}).get('token')

            self.log.debug(
                'Timeout expired while waiting for token renewal barrier to be disabled. '
                f'Attempts: {i + 1}'
            )

            if not self.monitor_thread.is_alive():
                break

        self.log.error(
            'Could not retrieve TC token. Token renewal monitor did not disable token barrier. '
            f'Token renewal monitor thread alive: {self.monitor_thread.is_alive()}'
        )

        # timeout expired, monitor likely offline
        exc = RuntimeError(
            'Timeout expired while waiting for renewal thread to disable token barrier.'
        )
        if self.monitor_thread.exception is not None:
            raise exc from self.monitor_thread.exception

        raise exc  # pragma: no cover

    @property
    def key(self) -> str:
        """Return the current key"""
        key = 'MainThread'  # default Python parent thread name
        if self.thread_name in self.token_map:
            # for Job, Playbook, and ApiService Apps the key is the thread name.
            key = self.thread_name
        elif self.trigger_id is not None and self.trigger_id in self.token_map:
            key = str(self.trigger_id)
        return key

    def register_token(self, key: str, token: Sensitive | str | None, expires: int | None):
        """Register a token.

        Args:
            key: The key to use to identify a token. Typically a thread name or a config id.
            token: The ThreatConnect API token.
            expires: The token expiration timestamp.
        """
        if token is None or expires is None:  # pragma: no cover
            self.log.error(
                'feature=token, event=invalid-token-data, ' f'token="{token}", expires={expires}.'
            )
            return

        self.token_map[key] = {'token': Sensitive(token), 'token_expires': int(expires)}
        self.log.debug(
            f'feature=token, action=token-register, key={key}, '
            f'token={token}, expiration={expires}'
        )

    def renew_token(self, token: Sensitive):
        """Renew expired ThreatConnect Token.

        This method will renew a token and update the token_map with new token and expiration.

        Args:
            token: The ThreatConnect API token.
        """
        api_token_data = {}
        # pause API logging
        self.log.in_token_renewal = True  # type: ignore

        # log token information
        try:
            params = {'expiredToken': token.value}
            url = f'{self.token_url}/appAuth'
            r = self.session.get(url, params=params, verify=self.verify)

            if not r.ok:
                err_reason = r.text or r.reason
                err_msg = (
                    f'feature=token, event=token-retry-error, status_code={r.status_code}, '
                    f'api-message={err_reason}, token={token}.'
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
            self.log.in_token_renewal = False  # type: ignore

        return api_token_data

    @cached_property
    def session(self) -> Session:
        """Return the session."""
        session = retry_session()
        if self.proxies:
            session.proxies = self.proxies
        return session

    @property
    def shutdown(self) -> bool:
        """Retrieve shutdown property"""
        return self._shutdown

    @shutdown.setter
    def shutdown(self, value: bool):
        """Set shutdown property.

        If new value is True, set the monitor_sleep Event so that renewal monitor knows to shut
        down immediately (or after its current renewal cycle).
        """
        if value is True:
            self._monitor_sleep_interval.set()

        self._shutdown = value

    @property
    def thread_name(self) -> str:
        """Return the current thread name."""
        return threading.current_thread().name

    @property
    def token(self) -> Sensitive | None:
        """Return token for current thread."""
        return self.get_token()

    @token.setter
    def token(self, token: Sensitive | str):
        """Set token for current thread."""
        self.token_map.setdefault(self.key, {})['token'] = Sensitive(token)

    @property
    def token_expires(self) -> int | None:
        """Return token_expires for current thread."""
        return self.token_map.get(self.key, {}).get('token_expires')

    @token_expires.setter
    def token_expires(self, expires):
        """Set token expires for current thread."""
        self.token_map.setdefault(self.key, {})['token_expires'] = int(expires)

    def token_renewal(self):
        """Start token renewal monitor thread."""
        self.monitor_thread = ExceptionThread(
            name='token-renewal', target=self.token_renewal_monitor, daemon=True
        )
        self.monitor_thread.start()

    def token_renewal_monitor(self):
        """Monitor token expiration and renew when required."""
        self.log.debug('feature=token, event=renewal-monitor-started')
        self._barrier.set()
        self._monitor_sleep_interval.wait(self.sleep_interval)
        while True:
            # Clear renewal barrier (setting it to False), which
            # blocks access to token via # the token property.
            self._barrier.clear()
            self.log.debug('Token renewal barrier enabled.')
            self._monitor_sleep_interval.wait(self.token_renewal_buffer_time)
            for key, token_data in dict(self.token_map).items():
                # calculate the time left to sleep
                sleep_seconds = (
                    token_data.get('token_expires') - int(time.time()) - self.token_window
                )
                self.log.trace(
                    '''feature=token, '''
                    f'''event=token-status, key={key}, '''
                    f'''token={token_data.get('token')}, '''
                    f'''expires={token_data.get('token_expires')}, '''
                    f'''sleep-seconds={sleep_seconds}'''
                )

                if sleep_seconds > 0:
                    continue

                # renew token data
                try:
                    api_token_data = self.renew_token(token_data.get('token'))
                    self.token_map[key]['token'] = Sensitive(api_token_data['apiToken'])
                    self.token_map[key]['token_expires'] = int(api_token_data['apiTokenExpires'])
                    self.log.info(
                        f'''feature=token, action=token-renewed, key={key}, '''
                        f'''token={api_token_data['apiToken']}, '''
                        f'''expires={api_token_data['apiTokenExpires']}'''
                    )
                except RuntimeError as e:
                    self.log.error(e)
                    try:
                        del self.token_map[key]
                        self.log.error(f'feature=token, event=token-removal-failure, key={key}')
                    except KeyError:  # pragma: no cover
                        pass

            # renewal loop is finished, grant access to token via token property once again
            self._barrier.set()
            self.log.debug('Token renewal barrier disabled.')

            # if monitor has not been shutdown, renewal monitor will sleep for sleep_interval
            # seconds. If monitor has been shutdown, monitor does not sleep and proceeds to
            # the shutdown logic within the if statement below. If the monitor is already
            # sleeping, the monitor wakes up and proceeds to the shutdown logic.
            self._monitor_sleep_interval.wait(self.sleep_interval)
            if self.shutdown is True:  # pragma: no cover
                self.log.debug('Token renewal monitor shutdown signal received')
                break

    @property
    def trigger_id(self) -> int | None:
        """Return the current trigger_id."""
        trigger_id = None
        if hasattr(threading.current_thread(), 'trigger_id'):
            trigger_id = threading.current_thread().trigger_id  # type: ignore
        if trigger_id is not None:
            trigger_id = int(trigger_id)
        return trigger_id

    def unregister_token(self, key: str):
        """Unregister a token.

        Args:
            key: The key used to identify a token.
        """
        try:
            del self.token_map[key]
            self.log.debug(f'feature=token, action=token-unregister, key={key}')
        except KeyError:
            pass
