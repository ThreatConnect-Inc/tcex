"""Generate Abstract Base Class"""
# standard library
import os
from abc import ABC

# third-party
from requests import Session

# first-party
from tcex.input.field_types.sensitive import Sensitive
from tcex.sessions.tc_session import HmacAuth
from tcex.utils import Utils


# initialize Utils module
utils = Utils()


class GenerateABC(ABC):
    """Generate Abstract Base Class"""

    def __init__(self, type_: str) -> None:
        """Initialize class properties."""
        self.type_ = utils.snake_string(type_)

        # properties
        self._api_server = os.getenv('TC_API_PATH')
        self.i1 = ' ' * 4  # indent level 1
        self.i2 = ' ' * 8  # indent level 2
        self.i3 = ' ' * 12  # indent level 3
        self.requirements = {}
        self.utils = utils

    def gen_requirements(self):
        """Generate imports string."""
        _libs = []
        for from_, libs in self.requirements.items():
            if not libs:
                # continue if there are no libraries to import
                continue

            if from_ in ['first-party-forward-reference']:
                # skip forward references
                continue

            _libs.append(f'# {from_}')
            for lib in sorted(libs):
                _libs.append(lib)
            _libs.append('')  # add newline
        _libs.append('')  # add newline
        return '\n'.join(_libs)

    @property
    def session(self) -> Session:
        """Return Session configured for TC API."""
        _session = Session()
        _session.auth = HmacAuth(
            os.getenv('TC_API_ACCESS_ID'), Sensitive(os.getenv('TC_API_SECRET_KEY'))
        )
        return _session

    @property
    def tap(self):
        """Return the TcEx Api Path."""
        if self.type_.plural().lower() in [
            'owners',
            'owner_roles',
            'system_roles',
            'users',
            'user_groups',
        ]:
            return 'tcex.api.tc.v3.security'
        return 'tcex.api.tc.v3'
