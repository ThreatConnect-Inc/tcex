# -*- coding: utf-8 -*-
"""TcEx testing profile Class."""
import base64
import pickle
import zlib

import colorama as c
from requests.sessions import Session

# autoreset colorama
c.init(autoreset=True, strip=False)


class SessionManager:
    """Class for profile Session recording."""

    def __init__(self, profile):
        """Initialize Class properties."""
        self.profile = profile

    def init(self):
        """Initialize session recording/playback.

        Configured ON with the --record_session test flag, forcibly disabled with the
        --ignore_session test flag. The profile field options.session.enabled can be
        true to enable session recording/playback.

        The profile field options.session.blur may be a list of fields to blur to force
        matching (ie, date/times, passwords, etc)
        """
        ignore_session = self.profile.pytest_args.get('ignore_session')
        record_session = self.profile.pytest_args.get('record_session')

        if ignore_session:
            return

        session_options = self.profile.options.get('session', {})
        session_enabled = session_options.get('enabled', False)

        if 'session' in self.profile.stage and not session_enabled:
            session_enabled = True
            session_options['enabled'] = True
            self.profile.options['session'] = session_options
            self.update_profile(force=True)  # add option to profile

        if record_session:
            session_enabled = True
            session_options['enabled'] = session_enabled
            self.profile.options['session'] = session_options

            # save session data in stage.session
            self.profile.stage['session'] = {'_record': True}

        if not session_enabled:
            return

        # if stage.session doesn't exist, but session_enabled is true, implicitly turn
        # on session recording (someone zapped the data out of the profile)
        if 'session' not in self.profile.stage:
            session_data = {'_record': True}
            self.profile.stage['session'] = session_data
        else:
            session_data = self.profile.stage.get('session')

        blur = ['password']
        blur_options = session_options.get('blur', [])
        # if options.session.blur is not a list, make it a tuple
        if not isinstance(blur_options, list):
            blur_options = (blur_options,)
        blur.extend(blur_options)

        self.profile.stage['session'] = session_data

        _request = getattr(Session, 'request')

        session_profile = self

        # Monkeypatch method for requests.sessions.Session.request
        def request(self, method, url, *args, **kwargs):
            """Intercept method for Session.request."""
            params = kwargs.get('params', {})
            parmlist = []
            params_keys = sorted(params.keys())
            for key in params_keys:
                if key in blur:
                    value = '***'
                else:
                    value = params.get(key)
                parmlist.append((key, value))

            # The key for this request e.g. GET https://... ('foo':'bla')
            request_key = f'{method} {url} {parmlist}'

            # if not recording, we must be playing back
            if not session_data.get('_record', False):
                result_data = session_data.get(request_key, None)
                if result_data is None:
                    raise KeyError('No stage.session value found for key {}'.format(request_key))
                return session_profile.unpickle_result(result_data)

            result = _request(self, method, url, *args, **kwargs)
            pickled_result = session_profile.pickle_result(result)
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
        return pickle.loads(zlib.decompress(base64.b64decode(result.encode('utf-8'))))

    def update_profile(self, force=False):
        """Write back the profile *if* we recorded session data"""
        profile_data = self.profile.contents
        stage = profile_data.get('stage', {})
        session = stage.get('session', {})
        _record = session.get('_record', False)

        if not _record and not force:
            return

        if '_record' in session:
            del session['_record']  # don't record _record!

        profile_data['stage']['session'] = session
        options = profile_data.get('options', {})
        profile_data['options'] = options
        options['session'] = profile_data.get('options').get('session')

        self.profile.write(profile_data)
