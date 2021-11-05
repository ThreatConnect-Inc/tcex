"""Generate Abstract Base Class"""
# standard library
import os
from abc import ABC
<<<<<<< HEAD
from typing import Any
=======

# third-party
from typing import Any, Dict
>>>>>>> e55bdd28 (APP-2294 - worked on indicator/groups)

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

    def __init__(self, type_: Any) -> None:
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

    def _type_map(self, type_):
        """Return modified type."""
        # special handling of attributes
        if type_ == 'attributes' and self.type_ == 'cases':
            type_ = 'case_attributes'
        elif type_ == 'attributes' and self.type_ == 'groups':
            type_ = 'group_attributes'
        elif type_ == 'attributes' and self.type_ == 'indicators':
            type_ = 'indicator_attributes'
        return self.utils.snake_string(type_)

    def _module_data(self, type_: str) -> Dict:
        """Return the model module map data."""
        type_ = self._type_map(type_)

        _base_path = f'{self.tap(type_)}.{type_}'
        return {
            'filter_module': f'{_base_path}.{type_.singular()}_filter',
            'filter_class': f'{type_.pascal_case()}Filter',
            'model_module': f'{_base_path}.{type_.singular()}_model',
            'model_class': f'{type_.singular().pascal_case()}Model',
            'model_collection_class': f'{type_.plural().pascal_case()}Model',
            'object_module': f'{_base_path}.{type_.singular()}',
            'object_class': f'{type_.singular().pascal_case()}',
            'object_collection_class': f'{type_.plural().pascal_case()}',
        }

    # def _model_module_map(self, type_: str) -> Dict:
    #     """Return the model module map data."""
    #     type_ = self.utils.snake_string(type_)
    #     _modules = {
    #         'adversary_assets': {
    #             'model_module': 'tcex.api.tc.v3.adversary_assets.adversary_asset_model',
    #             'model_class': 'AdversaryAssetModel',
    #         },
    #         'artifacts': {
    #             'model_module': 'tcex.api.tc.v3.artifacts.artifact_model',
    #             'model_class': 'ArtifactModel',
    #         },
    #         'artifact_types': {
    #             'model_module': 'tcex.api.tc.v3.artifact_types.artifact_type_model',
    #             'model_class': 'ArtifactTypeModel',
    #         },
    #         'attributes': {
    #             'model_module': 'tcex.api.tc.v3.case_attributes.case_attribute_model',
    #             'model_class': 'CaseAttributesModel',
    #         },
    #         'case_attributes': {
    #             'model_module': 'tcex.api.tc.v3.case_attributes.case_attribute_model',
    #             'model_class': 'CaseAttributesModel',
    #         },
    #         'cases': {
    #             'model_module': 'tcex.api.tc.v3.cases.case_model',
    #             'model_class': 'CaseModel',
    #         },
    #         'group_attributes': {
    #             'model_module': 'tcex.api.tc.v3.group_attributes.group_attribute_model',
    #             'model_class': 'GroupAttributesModel',
    #         },
    #         'groups': {
    #             'model_module': 'tcex.api.tc.v3.groups.group_model',
    #             'model_class': 'GroupModel',
    #         },
    #         'indicator_attributes': {
    #             # 'model_module': 'tcex.api.tc.v3.indicator_attributes.indicator_attribute_model',
    #             # 'model_class': 'IndicatorAttributesModel',
    #             'model_module': f'{self.tap(type_)}.{type_}.{type_.singular()}_model',
    #             'model_class': f'{type_.pascal_case()}Model',
    #             'object_class': f'{type_.singular().pascal_case()}',
    #         },
    #         'indicators': {
    #             'model_module': 'tcex.api.tc.v3.indicators.indicator_model',
    #             'model_class': 'IndicatorModel',
    #         },
    #         'notes': {
    #             'model_module': 'tcex.api.tc.v3.notes.note_model',
    #             'model_class': 'NoteModel',
    #         },
    #         'owner_roles': {
    #             'model_module': 'tcex.api.tc.v3.security.owner_roles.owner_role_model',
    #             'model_class': 'OwnerRoleModel',
    #         },
    #         'owners': {
    #             'model_module': 'tcex.api.tc.v3.security.owners.owner_model',
    #             'model_class': 'OwnerModel',
    #         },
    #         'security_labels': {
    #             'model_module': 'tcex.api.tc.v3.security_labels.security_label_model',
    #             'model_class': 'SecurityLabelModel',
    #         },
    #         'system_roles': {
    #             'model_module': 'tcex.api.tc.v3.security.system_roles.system_role_model',
    #             'model_class': 'SystemRoleModel',
    #         },
    #         'tags': {
    #             'model_module': 'tcex.api.tc.v3.tags.tag_model',
    #             'model_class': 'TagModel',
    #         },
    #         'tasks': {
    #             'model_module': 'tcex.api.tc.v3.tasks.task_model',
    #             'model_class': 'TaskModel',
    #         },
    #         'users': {
    #             'model_module': 'tcex.api.tc.v3.security.users.user_model',
    #             'model_class': 'UserModel',
    #         },
    #         'user_groups': {
    #             'model_module': 'tcex.api.tc.v3.security.user_groups.user_group_model',
    #             'model_class': 'UserGroupModel',
    #         },
    #         'victims': {
    #             'model_module': 'tcex.api.tc.v3.victims.victim_model',
    #             'model_class': 'VictimModel',
    #         },
    #         'victim_assets': {
    #             'model_module': 'tcex.api.tc.v3.victim_assets.victim_asset_model',
    #             'model_class': 'VictimAssetModel',
    #         },
    #         'workflow_events': {
    #             'model_module': 'tcex.api.tc.v3.workflow_events.workflow_event_model',
    #             'model_class': 'WorkflowEventModel',
    #         },
    #         'workflow_templates': {
    #             'model_module': 'tcex.api.tc.v3.workflow_templates.workflow_template_model',
    #             'model_class': 'WorkflowTemplateModel',
    #         },
    #     }
    #     print(_modules.get(type_))
    #     return _modules.get(type_)

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
