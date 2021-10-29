"""Generate Abstract Base Class"""
# standard library
import os
from abc import ABC

# third-party
import typer
from requests import Session
from requests.exceptions import ProxyError

# first-party
from tcex.backports import cached_property
from tcex.input.field_types.sensitive import Sensitive
from tcex.sessions.tc_session import HmacAuth
from tcex.utils import Utils


class GenerateABC(ABC):
    """Generate Abstract Base Class"""

    def __init__(self, type_: str) -> None:
        """Initialize class properties."""
        self.type_ = type_

        # properties
        self._api_server = os.getenv('TC_API_PATH')
        self.api_url = None
        self.i1 = ' ' * 4  # indent level 1
        self.i2 = ' ' * 8  # indent level 2
        self.i3 = ' ' * 12  # indent level 3
        self.i4 = ' ' * 16  # indent level 3
        self.requirements = {}
        self.utils = Utils()

    @cached_property
    def _type_properties(self) -> dict:
        """Return defined API properties for the current object.

        Response:
        artifacts": {
            "data": [
                {
                    "description": "a list of Artifacts corresponding to the Case",
                    "max_size": 1000,
                    "required": false,
                    "type": "Artifact"
                }
            ]
        },
        "assignee": {
            "description": "the user or group Assignee object for the Case",
            "required": false,
            "type": "Assignee"
        },
        "attributes": {
            "data": {
                "description": "a list of Attributes corresponding to the Case",
                "required": false,
                "type": "CaseAttributeData"
            }
        },
        "createdBy": {
            "read-only": true,
            "type": "User"
        }
        """
        _properties = {}
        try:
            r = self.session.options(self.api_url, params={'show': 'readOnly'})
            # print(r.request.method, r.request.url, r.text)
            if r.ok:
                _properties = r.json()
                if 'id' not in _properties:
                    _properties['id'] = {
                        'required': False,
                        'type': 'Integer',
                        'description': 'The id of the **Object**',
                        'read-only': True,
                    }
        except (ConnectionError, ProxyError) as ex:
            typer.secho(f'Failed getting types properties ({ex}).', fg=typer.colors.RED)
            typer.Exit(1)

        # print('status', r.status_code)
        # print(r.text)
        return _properties

    def gen_requirements(self):
        """Generate imports string."""
        # add additional imports when required
        if self.requirements.get('type-checking'):
            self.requirements['standard library'].append('from typing import TYPE_CHECKING')

        indent = ''
        _libs = []
        for from_, libs in self.requirements.items():
            if not libs:
                # continue if there are no libraries to import
                continue

            if from_ in ['first-party-forward-reference']:
                # skip forward references
                continue

            if from_ == 'type-checking':
                _libs.append('if TYPE_CHECKING:  # pragma: no cover')
                indent = self.i1
                # this should be fine?
                from_ = 'first-party'

            _libs.append(f'{indent}# {from_}')

            # manage imports as string and dicts
            _imports = []  # temp store for imports so they can be sorted
            for lib in libs:
                if isinstance(lib, dict):
                    imports = ', '.join(sorted(lib.get('imports')))
                    _imports.append(f'''{indent}from {lib.get('module')} import {imports}''')
                elif isinstance(lib, str):
                    _imports.append(f'{indent}{lib}')
            _libs.extend(sorted(_imports))  # add imports sorted

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

    def tap(self, type_: str):
        """Return the TcEx Api Path."""
        type_ = self.utils.snake_string(type_)
        if type_.plural().lower() in [
            'owners',
            'owner_roles',
            'system_roles',
            'users',
            'user_groups',
        ]:
            return 'tcex.api.tc.v3.security'
        return 'tcex.api.tc.v3'
