"""Gen Code App Input Map"""
# standard library
from typing import List

# first-party
from tcex.app_config.install_json import InstallJson


class SpecToolAppInputStatic:
    """Generate App Config File"""

    def __init__(self):
        """Initialize class properties."""

        # class properties
        self.i1 = ' ' * 4
        self.i2 = ' ' * 8
        self.ij = InstallJson()

    @property
    def template_app_inputs_class(self) -> list:
        """Return app_inputs.py AppInput class."""
        app_model = 'AppBaseModel'
        if self.ij.model.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            app_model = 'ServiceConfigModel'

        return [
            '''class AppInputs:''',
            f'''{self.i1}"""App Inputs"""''',
            '',
            f'''{self.i1}def __init__(self, inputs: 'BaseModel'):''',
            f'''{self.i2}"""Initialize class properties."""''',
            f'''{self.i2}self.inputs = inputs''',
            '',
            f'''{self.i1}def update_inputs(self):''',
            f'''{self.i2}"""Add custom App models to inputs.''',
            '',
            f'''{self.i2}Input will be validate when the model is added an any exceptions will''',
            f'''{self.i2}cause the App to exit with a status code of 1.''',
            f'''{self.i2}"""''',
            f'''{self.i2}self.inputs.add_model({app_model})''',
            '',
            '',
        ]

    @property
    def app_base_model_class_comment(self) -> str:
        """Return Service Config Model class."""
        return f'{self.i1}"""Base model for the App containing any common inputs."""'

    @property
    def service_config_model_class_comment(self) -> str:
        """Return Service Config Model class."""
        return '\n'.join(
            [
                f'''{self.i1}"""Base model for the App containing any common inputs.''',
                '',
                f'''{self.i1}Trigger Service App inputs do not take playbookDataType.''',
                '',
                f'''{self.i1}This is the configuration input that is sent to the Service''',
                f'''{self.i1}on startup. The inputs that are configured in the Service''',
                f'''{self.i1}configuration in the Platform with serviceConfig: true''',
                f'''{self.i1}"""''',
                '',
                '',
            ]
        )

    @property
    def trigger_config_model_class_comment(self) -> str:
        """Return Trigger Config Model class."""
        return '\n'.join(
            [
                f'''{self.i1}"""Base model for Trigger (playbook) config.''',
                '',
                f'''{self.i1}Trigger Playbook inputs do not take playbookDataType.''',
                '',
                f'''{self.i1}This is the configuration input that gets sent to the service''',
                f'''{self.i1}when a Playbook is enabled (createConfig).''',
                f'''{self.i1}"""''',
                '',
                '',
            ]
        )

    def template_app_inputs_class_tc_action(self, class_model_map: dict) -> list:
        """Return app_inputs.py AppInput class for App with tc_action."""
        cmm = ''
        for action, class_name in class_model_map.items():
            cmm += f'\'{action}\': {class_name},'
        cmm = f'{{{cmm}}}'

        return [
            '''class AppInputs:''',
            f'''{self.i1}"""App Inputs"""''',
            '',
            f'''{self.i1}def __init__(self, inputs: 'BaseModel'):''',
            f'''{self.i2}"""Initialize class properties."""''',
            f'''{self.i2}self.inputs = inputs''',
            '',
            f'''{self.i1}def get_model(self, tc_action: Optional[str] = None) -> 'BaseModel':''',
            f'''{self.i2}"""Return the model based on the current action."""''',
            f'''{self.i2}tc_action = tc_action or self.inputs.model_unresolved.tc_action''',
            f'''{self.i2}action_model_map = {cmm}''',
            f'''{self.i2}return action_model_map.get(tc_action)''',
            '',
            f'''{self.i1}def update_inputs(self):''',
            f'''{self.i2}"""Add custom App models to inputs.''',
            '',
            f'''{self.i2}Input will be validate when the model is added an any exceptions will''',
            f'''{self.i2}cause the App to exit with a status code of 1.''',
            f'''{self.i2}"""''',
            f'''{self.i2}self.inputs.add_model(self.get_model())''',
            '',
            '',
        ]

    def template_app_inputs_prefix(
        self,
        field_type_modules: List[str],
        pydantic_modules: List[str],
        typing_modules: List[str],
    ) -> list:
        """Return app_inputs.py prefix data."""
        field_types_modules = ', '.join(sorted(list(field_type_modules)))
        pydantic_modules = ', '.join(sorted(list(pydantic_modules)))
        typing_modules = ', '.join(sorted(list(typing_modules)))
        _imports = [
            '"""App Inputs"""',
            '# pylint: disable=no-self-argument, no-self-use',
            '# standard library',
            f'from typing import {typing_modules}',
            '',
            '# third-party',
            f'from pydantic import {pydantic_modules}',
            f'from tcex.input.field_types import {field_types_modules}',
        ]

        # add import for service trigger Apps
        if self.ij.model.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']:
            _imports.append('from tcex.input.models import CreateConfigModel')

        # add new lines
        _imports.extend(
            [
                '',
                '',
            ]
        )
        return _imports

    @property
    def type_map(self):
        """Return input map."""
        return {
            'Any': {
                'optional': {'type': 'Any', 'field_type': None},
                'required': {'type': 'Any', 'field_type': None},
            },
            'Binary': {
                'optional': {'type': 'Binary', 'field_type': 'Binary'},
                'required': {'type': 'binary(allow_empty=False)', 'field_type': 'binary'},
            },
            'BinaryArray': {
                'optional': {'type': 'List[Binary]', 'field_type': 'Binary'},
                'required': {'type': 'List[binary(allow_empty=False)]', 'field_type': 'binary'},
            },
            'Choice': {
                'optional': {'type': 'Choice', 'field_type': 'Choice'},
                'required': {'type': 'Choice', 'field_type': 'Choice'},
            },
            'EditChoice': {
                'optional': {'type': 'EditChoice', 'field_type': 'EditChoice'},
                'required': {'type': 'EditChoice', 'field_type': 'EditChoice'},
            },
            'Encrypt': {
                'optional': {'type': 'Sensitive', 'field_type': 'Sensitive'},
                'required': {'type': 'sensitive(allow_empty=False)', 'field_type': 'sensitive'},
            },
            'KeyValue': {
                'optional': {'type': 'KeyValue', 'field_type': 'KeyValue'},
                'required': {'type': 'KeyValue', 'field_type': 'KeyValue'},
            },
            'KeyValueArray': {
                'optional': {'type': 'List[KeyValue]', 'field_type': 'KeyValue'},
                'required': {'type': 'List[KeyValue]', 'field_type': 'KeyValue'},
            },
            'KeyValueList': {
                'optional': {'type': 'List[KeyValue]', 'field_type': 'KeyValue'},
                'required': {'type': 'List[KeyValue]', 'field_type': 'KeyValue'},
            },
            'MultiChoice': {
                'optional': {'type': 'List[Choice]', 'field_type': 'Choice'},
                'required': {'type': 'List[Choice]', 'field_type': 'Choice'},
            },
            'String': {
                'optional': {'type': 'String', 'field_type': 'String'},
                'required': {'type': 'string(allow_empty=False)', 'field_type': 'string'},
            },
            'StringArray': {
                'optional': {'type': 'List[String]', 'field_type': 'String'},
                'required': {'type': 'List[string(allow_empty=False)]', 'field_type': 'string'},
            },
            'TCEntity': {
                'optional': {'type': 'TCEntity', 'field_type': 'TCEntity'},
                'required': {'type': 'TCEntity', 'field_type': 'TCEntity'},
            },
            'TCEntityArray': {
                'optional': {'type': 'List[TCEntity]', 'field_type': 'TCEntity'},
                'required': {'type': 'List[TCEntity]', 'field_type': 'TCEntity'},
            },
        }
