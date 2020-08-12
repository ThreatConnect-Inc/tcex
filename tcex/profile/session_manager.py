# -*- coding: utf-8 -*-
"""TcEx testing profile Class."""
# standard library
import base64
import pickle  # nosec
import zlib

# third-party
import colorama as c
from requests.sessions import Session

# autoreset colorama
c.init(autoreset=True, strip=False)


class SessionManager:
    """Class for profile Session recording."""

    def __init__(self, profile):
        """Initialize Class properties."""
        self.profile = profile

        # properties
        self.profile_data = self.profile.contents
        self.record = False

    def init(self):
        """Initialize session recording/playback.

        Configured ON with the --record_session test flag, forcibly disabled with the
        --ignore_session test flag. The profile field options.session.enabled can be
        true to enable session recording/playback.

        The profile field options.session.blur may be a list of fields to blur to force
        matching (ie, date/times, passwords, etc)
        """
        if self.profile.pytest_args.get('ignore_session'):
            # return if cli arg passed
            return

        # ensure a profile has all required sections
        self.profile_data.setdefault('stage', {})
        self.profile_data.setdefault('options', {})
        self.profile_data['options'].setdefault('session', {})
        self.profile_data['options']['session'].setdefault('enabled', False)
        self.profile_data['options']['session'].setdefault('blur', [])

        session_options = self.profile_data['options']['session']
        session_enabled = session_options['enabled']

        if 'session' in self.profile_data.get('stage', {}) and not session_enabled:
            # session in staging mean enabled should be true?
            session_enabled = True

        if self.profile.pytest_args.get('record_session'):
            session_enabled = True
            self.profile_data['stage'].setdefault('session', {})
            self.record = True

        self.profile.log.data(
            'session', 'Session Manager', f'session recording enabled: {session_enabled}', 'info',
        )
        if not session_enabled:
            # no setting that would enable recording found so stop here
            return

        # if stage.session doesn't exist, but session_enabled is true, implicitly turn
        # on session recording (someone zapped the data out of the profile)
        if 'session' not in self.profile_data['stage']:
            self.profile_data['stage']['session'] = {}
            self.record = True

        # default blur value
        blur = ['password']
        blur.extend(session_options['blur'])
        self.profile.log.data(
            'session', 'Session Manager', f'bluring params {blur}', 'info',
        )

        # get requests Session attr for monkeypatch
        _request = getattr(Session, 'request')

        # local variable scope for class method/properties to be used in monkeypatch
        session_data = self.profile_data['stage']['session']
        session_manager = self

        # log record value
        self.profile.log.data(
            'session', 'Session Manager', f'record enabled: {self.record}', 'info',
        )

        # Monkeypatch method for requests.sessions.Session.request
        def request(self, method, url, *args, **kwargs):
            """Intercept method for Session.request."""
            params = kwargs.get('params') or {}
            parm_list = []
            params_keys = sorted(params.keys())
            for key in params_keys:
                if key in blur:
                    value = '***'
                else:
                    value = params.get(key)
                parm_list.append((key, value))

            # The key for this request e.g. GET https://... ('foo':'bla')
            request_key = f'{method} {url} {parm_list}'

            # if not recording, we must be playing back
            if not session_manager.record:
                result_data = session_data.get(request_key, None)
                if result_data is None:
                    raise KeyError('No stage.session value found for key {}'.format(request_key))
                return session_manager.unpickle_result(result_data)

            result = _request(self, method, url, *args, **kwargs)
            pickled_result = session_manager.pickle_result(result)
            session_data[request_key] = pickled_result
            return result

        # Add the intercept
        self.profile.monkeypatch.setattr(Session, 'request', request)

    @staticmethod
    def pickle_result(result):
        """Pickled the result object so we can reconstruct it later"""
        return base64.b64encode(zlib.compress(pickle.dumps(result))).decode('utf-8')

    @staticmethod
    def unpickle_result(result):
        """Reverse the pickle operation"""
        return pickle.loads(zlib.decompress(base64.b64decode(result.encode('utf-8'))))  # nosec

    def update_profile(self):
        """Write back the profile *if* we recorded session data"""
        # only record if _record set to true in init method
        if not self.record:
            return

        # get stage and session data
        stage = self.profile_data.get('stage', {})
        session = stage.get('session', {})

        # update data
        self.profile_data['stage']['session'] = session
        options = self.profile_data.get('options', {})
        self.profile_data['options'] = options
        options['session'] = self.profile_data.get('options').get('session')

        self.profile.write(self.profile_data, 'session_manager')
