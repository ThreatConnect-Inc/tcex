"""TestAdvancedSettings for testing advanced settings functionality.

This module contains comprehensive test cases for the advanced settings implementation in TcEx,
including validation of optional/required settings, data transformation, and error handling.

Classes:
    TestInputsFieldTypes: Test class for advanced settings validation

TcEx Module Tested: tcex.input.m.modify_advanced_settings
"""


from collections.abc import Callable
from typing import Literal


import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError


from tcex.input.field_type import DateTime, String, modify_advanced_settings
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestInputsFieldTypes(InputTest):
    """TestInputsFieldTypes for comprehensive advanced settings testing.

    This class provides extensive test coverage for the advanced settings functionality,
    including validation of optional/required settings, data transformation, and error handling.

    Fixtures:
        playbook_app: Mock application fixture for testing TcEx functionality
    """

    def setup_method(self) -> None:
        """Configure setup before all tests."""
        scoped_property._reset()
        cached_property._reset()

    def test_advanced_settings_is_optional_input_initialized_with_none(
        self, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test optional advanced_settings input initialized with None.

        This test validates that when an optional advanced_settings input is initialized with None,
        the model correctly reflects this value without raising any validation errors.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        # Model that defines entries expected in pipe-delimited advanced settings input string
        class AdvancedSettingsModel(BaseModel):
            """Model that defines all expected advanced settings entries"""

            my_setting: String

        # the app model
        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # advanced settings input is Optional for this app
            advanced_settings: AdvancedSettingsModel | None = Field(default=None)
            # configure "modify_advanced_settings" validator to act on "advanced_settings" input,
            # which performs the parsing of the pipe-delimited string into a dictionary,
            # which would then be used to initialize AdvancedSettingsModel
            _ = modify_advanced_settings('advanced_settings')

        # advanced settings initialized with None
        config_data = {'advanced_settings': None}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.advanced_settings is None  # type: ignore

    def test_advanced_settings_is_optional_input_and_is_not_initialized(
        self, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test optional advanced_settings input that is not initialized.

        This test validates that when an optional advanced_settings input is not provided in the
        configuration, the model correctly defaults to None without raising validation errors.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        # Model that defines entries expected in pipe-delimited advanced settings input string
        class AdvancedSettingsModel(BaseModel):
            """Model that defines all expected advanced settings entries"""

            my_setting: String

        # the app model
        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # advanced settings input is Optional for this app
            advanced_settings: AdvancedSettingsModel | None = Field(default=None)
            # configure "modify_advanced_settings" validator to act on "advanced_settings" input,
            # which performs the parsing of the pipe-delimited string into a dictionary,
            # which would then be used to initialize AdvancedSettingsModel
            _ = modify_advanced_settings('advanced_settings')

        # advanced_settings is not present in config data of app
        config_data = {}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.advanced_settings is None  # type: ignore

    def test_advanced_settings_is_required_input_initialized_with_none(
        self, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test required advanced_settings input initialized with None.

        This test validates that a ValidationError is raised when a required advanced_settings
        input is initialized with None, as this violates the requirement.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        # Model that defines entries expected in pipe-delimited advanced settings input string
        class AdvancedSettingsModel(BaseModel):
            """Model that defines all expected advanced settings entries"""

            my_setting: String

        # the app model
        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # advanced settings input is required for this app
            advanced_settings: AdvancedSettingsModel
            # configure "modify_advanced_settings" validator to act on "advanced_settings" input,
            # which performs the parsing of the pipe-delimited string into a dictionary,
            # which would then be used to initialize AdvancedSettingsModel
            _ = modify_advanced_settings('advanced_settings')

        # advanced settings initialized with None
        config_data = {'advanced_settings': None}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # error expected, as advanced_settings is required
        with pytest.raises(ValidationError):
            tcex.inputs.add_model(PytestModel)

    def test_advanced_settings_is_required_input_and_is_not_initialized(
        self, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test required advanced_settings input that is not initialized.

        This test validates that a ValidationError is raised when a required advanced_settings
        input is not provided in the configuration, ensuring the requirement is enforced.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        # Model that defines entries expected in pipe-delimited advanced settings input string
        class AdvancedSettingsModel(BaseModel):
            """Model that defines all expected advanced settings entries"""

            my_setting: String

        # the app model
        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # advanced settings input is required for this app
            advanced_settings: AdvancedSettingsModel
            # configure "modify_advanced_settings" validator to act on "advanced_settings" input,
            # which performs the parsing of the pipe-delimited string into a dictionary,
            # which would then be used to initialize AdvancedSettingsModel
            _ = modify_advanced_settings('advanced_settings')

        # advanced_settings is not present in config data of app
        config_data = {}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # error expected, as advanced_settings is required but was not initialized
        with pytest.raises(ValidationError):
            tcex.inputs.add_model(PytestModel)

    def test_advanced_settings_value_is_properly_transformed_per_advanced_settings_model(
        self, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test that AdvancedSettingsModel properly transforms values.

        This test ensures that after the modify_advanced_settings validator parses the
        pipe-delimited string, the resulting dictionary is used to initialize the
        AdvancedSettingsModel, and the values are correctly validated and transformed according
        to the type definitions within the model.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        # Model that defines entries expected in pipe-delimited advanced settings input string
        class AdvancedSettingsModel(BaseModel):
            """Model that defines all expected advanced settings entries"""

            # expect run_until entry in advanced_settings string. Should be converted to DateTime
            # Note: DateTime is not wrapped with Optional. This would mean that run_until is always
            # expected in advanced_settings, if advanced_settings string is provided. Marking this
            # as Optional is also allowed, which would mean it's ok for run_until to be missing.
            run_until: DateTime

        # the app model
        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # advanced settings input is required for this app
            advanced_settings: AdvancedSettingsModel
            # configure "modify_advanced_settings" validator to act on "advanced_settings" input,
            # which performs the parsing of the pipe-delimited string into a dictionary,
            # which would then be used to initialize AdvancedSettingsModel
            _ = modify_advanced_settings('advanced_settings')

        config_data = {
            'advanced_settings': 'run_until=Wednesday, 27-May-2020 10:30:35 UTC'
        }
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)
        run_until_setting = tcex.inputs.model.advanced_settings.run_until  # type: ignore

        # run_until has been parsed into a DateTime as expected, and we can call isoformat on it
        assert run_until_setting.isoformat() == '2020-05-27T10:30:35+00:00'

    def test_validation_performed_on_parsed_advanced_settings_raises_proper_error(
        self, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test that validation errors within AdvancedSettingsModel are raised.

        This test ensures that if a value in the parsed advanced settings string fails validation
        within the AdvancedSettingsModel (e.g., a malformed date), the appropriate
        ValidationError is raised and propagated.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        # Model that defines entries expected in pipe-delimited advanced settings input string
        class AdvancedSettingsModel(BaseModel):
            """Model that defines all expected advanced settings entries"""

            # expect run_until entry in advanced_settings string. Should be converted to DateTime
            # Note: DateTime is not wrapped with Optional. This would mean that run_until is always
            # expected in advanced_settings, if advanced_settings string is provided. Marking this
            # as Optional is also allowed, which would mean it's ok for run_until to be missing.
            run_until: DateTime

        # the app model
        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # advanced settings input is required for this app
            advanced_settings: AdvancedSettingsModel
            # configure "modify_advanced_settings" validator to act on "advanced_settings" input,
            # which performs the parsing of the pipe-delimited string into a dictionary,
            # which would then be used to initialize AdvancedSettingsModel
            _ = modify_advanced_settings('advanced_settings')

        config_data = {'advanced_settings': 'run_until=this is not a date'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValidationError) as ex:
            tcex.inputs.add_model(PytestModel)

        # expect to be told that run_until's value could not be parsed as DateTime
        assert 'run_until' in str(ex.value) and 'this is not a date' in str(ex.value)

    @pytest.mark.parametrize(
        'advanced_settings_string,expected_model,optional,extra_config,fail_expected',
        [
            #
            # Required Testing - AdvancedSettingsModel sets 'my_setting' as required String
            #
            pytest.param(
                'my_setting=value',
                {'my_setting': 'value'},
                False,
                'ignore',
                False,
                id='pass-required-my-setting-value',
            ),
            # keys are not case sensitive
            pytest.param(
                'My_Setting=value',
                {'my_setting': 'value'},
                False,
                'ignore',
                False,
                id='pass-required-my-setting-case-insensitive',
            ),
            # key should be stripped
            pytest.param(
                ' my_setting=value',
                {'my_setting': 'value'},
                False,
                'ignore',
                False,
                id='pass-required-my-setting-leading-space',
            ),
            pytest.param(
                'my_setting =value',
                {'my_setting': 'value'},
                False,
                'ignore',
                False,
                id='pass-required-my-setting-space-after-key',
            ),
            pytest.param(
                ' my_setting =value',
                {'my_setting': 'value'},
                False,
                'ignore',
                False,
                id='pass-required-my-setting-spaces-around-key',
            ),
            # value should be empty
            pytest.param(
                'my_setting=',
                {'my_setting': ''},
                False,
                'ignore',
                False,
                id='pass-required-my-setting-empty-value',
            ),
            # should split on first equal sign only
            pytest.param(
                'my_setting=value=other',
                {'my_setting': 'value=other'},
                False,
                'ignore',
                False,
                id='pass-required-my-setting-multiple-equals',
            ),
            pytest.param(
                'my_setting==',
                {'my_setting': '='},
                False,
                'ignore',
                False,
                id='pass-required-my-setting-double-equals',
            ),
            # value should be string containing single space
            pytest.param(
                'my_setting= ',
                {'my_setting': ' '},
                False,
                'ignore',
                False,
                id='pass-required-my-setting-space-value',
            ),
            #
            # Optional Testing - AdvancedSettingsModel sets 'my_setting' as Optional[String]
            #
            # Note: 'my_setting' will be None within the model, since no value can be parsed
            pytest.param(
                'my_setting',
                {'my_setting': None},
                True,
                'ignore',
                False,
                id='pass-optional-my-setting-no-value',
            ),
            # Note: 'my_setting' will be None in model, since my_setting is not found in string
            pytest.param(
                '',
                {'my_setting': None},
                True,
                'ignore',
                False,
                id='pass-optional-empty-string',
            ),
            # my_setting key not defined in advanced_settings input string
            pytest.param(
                ' =value',
                {'my_setting': None},
                True,
                'ignore',
                False,
                id='pass-optional-space-equals-value',
            ),
            # my_setting key not defined in advanced_settings input string
            pytest.param(
                '=value',
                {'my_setting': None},
                True,
                'ignore',
                False,
                id='pass-optional-equals-value',
            ),
            # my_setting key not defined in advanced_settings input string
            pytest.param(
                '==value',
                {'my_setting': None},
                True,
                'ignore',
                False,
                id='pass-optional-double-equals-value',
            ),
            #
            # Extra fields allowed via 'allow' in AdvancedSettingsModel Config
            #
            pytest.param(
                'my_setting=val|other=val2',
                {'my_setting': 'val', 'other': 'val2'},
                True,
                'allow',
                False,
                id='pass-allow-extra-fields',
            ),
            # trailing pipe
            pytest.param(
                'my_setting=val|other=val2|',
                {'my_setting': 'val', 'other': 'val2'},
                True,
                'allow',
                False,
                id='pass-allow-trailing-pipe',
            ),
            # extra pipe at start
            pytest.param(
                '|my_setting=val|other=val2',
                {'my_setting': 'val', 'other': 'val2'},
                True,
                'allow',
                False,
                id='pass-allow-leading-pipe',
            ),
            # extra pipes at start and end of string
            pytest.param(
                '|my_setting=val|other=val2|',
                {'my_setting': 'val', 'other': 'val2'},
                True,
                'allow',
                False,
                id='pass-allow-leading-and-trailing-pipes',
            ),
            # extra setting has empty key, skipped
            pytest.param(
                'my_setting=val|=val2',
                {'my_setting': 'val'},
                True,
                'allow',
                False,
                id='pass-allow-empty-extra-key',
            ),
            # extra setting has empty key when stripped, skipped
            pytest.param(
                'my_setting=val| =val2',
                {'my_setting': 'val'},
                True,
                'allow',
                False,
                id='pass-allow-space-extra-key',
            ),
            # extra setting has empty value
            pytest.param(
                'my_setting=val|other=',
                {'my_setting': 'val', 'other': ''},
                True,
                'allow',
                False,
                id='pass-allow-empty-extra-value',
            ),
            # setting defined in model has no value
            pytest.param(
                'my_setting=|other=val2',
                {'my_setting': '', 'other': 'val2'},
                True,
                'allow',
                False,
                id='pass-allow-empty-model-value',
            ),
            # no entry for setting defined in model, but extra setting makes it through
            pytest.param(
                'other=val2',
                {'my_setting': None, 'other': 'val2'},
                True,
                'allow',
                False,
                id='pass-allow-missing-model-setting',
            ),
            # extra setting is malformed, skipped
            pytest.param(
                'my_setting=val|other',
                {'my_setting': 'val'},
                True,
                'allow',
                False,
                id='pass-allow-malformed-extra-setting',
            ),
            # extra setting is malformed, skipped
            pytest.param(
                'my_setting=val|=',
                {'my_setting': 'val'},
                True,
                'allow',
                False,
                id='pass-allow-malformed-extra-setting-no-value',
            ),
            # extra setting is malformed, skipped
            pytest.param(
                'my_setting=val|=val2',
                {'my_setting': 'val'},
                True,
                'allow',
                False,
                id='pass-allow-malformed-extra-setting-with-value',
            ),
            #
            # Fail Testing
            #
            # my_setting required, but no valid entry provided for it
            # fails because my_setting is required but was not defined in passed-in setting string
            pytest.param(
                '=value', None, False, 'ignore', True, id='fail-required-missing-key'
            ),
            # fails because my_setting is required but was not defined in passed-in setting string
            pytest.param(
                ' =value',
                None,
                False,
                'ignore',
                True,
                id='fail-required-missing-key-space',
            ),
            # fails because my_setting is required but was not defined in passed-in setting string
            pytest.param(
                'my_setting',
                None,
                False,
                'ignore',
                True,
                id='fail-required-missing-value',
            ),
            # my_setting defined twice in settings string
            pytest.param(
                'my_setting=val|my_setting=val2',
                None,
                False,
                'ignore',
                True,
                id='fail-duplicate-key',
            ),
            # extra field not allowed
            pytest.param(
                'my_setting=val|other=val2',
                None,
                False,
                'forbid',
                True,
                id='fail-forbid-extra-field',
            ),
        ],
    )
    def test_advanced_settings_scenarios(
        self,
        advanced_settings_string: str,
        expected_model: dict | None,
        optional: bool,
        extra_config: Literal['allow', 'ignore', 'forbid'],
        fail_expected: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test various advanced settings scenarios.

        NOTE: the advanced_settings INPUT is required for all scenarios of this test. The 'optional'
        parameter controls whether 'my_setting' is optional or not within the advanced settings
        MODEL.

        PytestModel here would be the Input model that defines all expected inputs for a job app,
        including the advanced_settings input. AdvancedSettingsModel is where we define
        which advanced settings are expected to be found after the advanced_settings input is parsed
        from a pipe-delimited string to a dictionary.

        The act of parsing the pipe-delimited string to a dictionary is handled by the
        modify_advanced_settings validator.

        Args:
            advanced_settings_string: The pipe-delimited string for advanced_settings.
            expected_model: The expected dictionary representation of the parsed model.
            optional: Controls if 'my_setting' is optional in the AdvancedSettingsModel.
            extra_config: Configures behavior for extra fields ('ignore', 'allow', 'forbid').
            fail_expected: If True, the test expects a ValidationError.
            playbook_app: Mock app fixture.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        # "my_setting" advanced_setting entry will be required/optional depending on input
        # my_setting_type = String | None if optional else String
        my_setting_type = String | None if optional else String
        my_setting_type_default = None if optional else ...

        # Model that defines entries expected in pipe-delimited advanced settings input string
        class AdvancedSettingsModel(BaseModel):
            """Model that defines all expected advanced settings entries"""

            # configuration class of AdvancedSettingsModel. This is not required, but allows us
            # to further define model behavior.
            model_config = ConfigDict(extra=extra_config)

            # define "my_setting" advanced setting entry. Will be either required or optional
            # depending on value of "optional" test method input parameter.
            my_setting: my_setting_type = Field(my_setting_type_default)  # type: ignore

        # the app model
        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # advanced settings input is required for this app
            advanced_settings: AdvancedSettingsModel
            # configure "modify_advanced_settings" validator to act on "advanced_settings" input,
            # which performs the parsing of the pipe-delimited string into a dictionary,
            # which would then be used to initialize AdvancedSettingsModel
            _ = modify_advanced_settings('advanced_settings')

        # set up config data. advanced_settings input is given the string contained in
        # advanced_settings_string (what is received from the UI).
        config_data = {'advanced_settings': f'{advanced_settings_string}'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        if not fail_expected:
            tcex.inputs.add_model(PytestModel)
            assert tcex.inputs.model.advanced_settings.model_dump() == expected_model  # type: ignore
        else:
            with pytest.raises(ValidationError):
                tcex.inputs.add_model(PytestModel)
