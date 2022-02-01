"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Dict, Optional

# third-party
import pytest
from pydantic import BaseModel, Extra, ValidationError

# first-party
from tcex.backports import cached_property
from tcex.input.field_types import DateTime, String, modify_advanced_settings
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_types.utils import InputTest

if TYPE_CHECKING:
    # first-party
    from tests.mock_app import MockApp


# pylint: disable=no-self-argument, no-self-use
class TestInputsFieldTypes(InputTest):
    """Test TcEx String Field Model Tests."""

    def setup_method(self):
        """Configure setup before all tests."""
        scoped_property._reset()
        cached_property._reset()

    def test_advanced_settings_is_optional_input_initialized_with_none(
        self, playbook_app: 'MockApp'
    ):
        """Test scenario where advanced_settings input is optional and initialized with None"""

        # Model that defines entries expected in pipe-delimited advanced settings input string
        class AdvancedSettingsModel(BaseModel):
            """Model that defines all expected advanced settings entries"""

            my_setting: String

        # the app model
        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # advanced settings input is Optional for this app
            advanced_settings: Optional[AdvancedSettingsModel]
            # configure "modify_advanced_settings" validator to act on "advanced_settings" input,
            # which performs the parsing of the pipe-delimited string into a dictionary,
            # which would then be used to initialize AdvancedSettingsModel
            _ = modify_advanced_settings('advanced_settings')

        # advanced settings initialized with None
        config_data = {'advanced_settings': None}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.advanced_settings is None

    def test_advanced_settings_is_optional_input_and_is_not_initialized(
        self, playbook_app: 'MockApp'
    ):
        """Test scenario where advanced_settings input is optional and is not initialized

        App config data contains nothing for advanced_settings input
        """

        # Model that defines entries expected in pipe-delimited advanced settings input string
        class AdvancedSettingsModel(BaseModel):
            """Model that defines all expected advanced settings entries"""

            my_setting: String

        # the app model
        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # advanced settings input is Optional for this app
            advanced_settings: Optional[AdvancedSettingsModel]
            # configure "modify_advanced_settings" validator to act on "advanced_settings" input,
            # which performs the parsing of the pipe-delimited string into a dictionary,
            # which would then be used to initialize AdvancedSettingsModel
            _ = modify_advanced_settings('advanced_settings')

        # advanced_settings is not present in config data of app
        config_data = {}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.advanced_settings is None

    def test_advanced_settings_is_required_input_initialized_with_none(
        self, playbook_app: 'MockApp'
    ):
        """Test scenario where advanced_settings input is required and initialized with None"""

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
        self, playbook_app: 'MockApp'
    ):
        """Test scenario where advanced_settings input is required and is not initialized

        App config data contains nothing for advanced_settings input
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
        self, playbook_app: 'MockApp'
    ):
        """Test that AdvancedSettingsModel properly transforms entry.

        After modify_advanced_settings validator parses the pipe-delimited string,
        the resulting dictionary should be used to initialize AdvancedSettingsModel, and the values
        should be validated/transformed by each entry's corresponding type definition within
        AdvancedSettingsModel
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

        config_data = {'advanced_settings': 'run_until=Wednesday, 27-May-2020 10:30:35 UTC'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)
        run_until_setting = tcex.inputs.model.advanced_settings.run_until

        # run_until has been parsed into a DateTime as expected, and we can call isoformat on it
        assert run_until_setting.isoformat() == '2020-05-27T10:30:35+00:00'

    def test_validation_performed_on_parsed_advanced_settings_raises_proper_error(
        self, playbook_app: 'MockApp'
    ):
        """Test that AdvancedSettingsModel errors found within AdvancedSettingsModel are raised

        After modify_advanced_settings validator parses the pipe-delimited string,
        the resulting dictionary should be used to initialize AdvancedSettingsModel, and the values
        should be validated/transformed by each entry's corresponding type definition within
        AdvancedSettingsModel.

        In this case, run_until's value will not be properly converted to a DateTime. Error expected
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

        with pytest.raises(ValidationError) as error:
            tcex.inputs.add_model(PytestModel)

        error = str(error)
        # expect to be told that run_until's value could not be parsed as DateTime
        assert 'run_until' in error and 'could not be parsed as a date time object' in error

    @pytest.mark.parametrize(
        'advanced_settings_string,expected_model,optional,extra_config,fail_expected',
        [
            #
            # Required Testing - AdvancedSettingsModel sets 'my_setting' as required String
            #
            ('my_setting=value', {'my_setting': 'value'}, False, Extra.ignore, False),
            # keys are not case sensitive
            ('My_Setting=value', {'my_setting': 'value'}, False, Extra.ignore, False),
            # key should be stripped
            (' my_setting=value', {'my_setting': 'value'}, False, Extra.ignore, False),
            ('my_setting =value', {'my_setting': 'value'}, False, Extra.ignore, False),
            (' my_setting =value', {'my_setting': 'value'}, False, Extra.ignore, False),
            # value should be empty
            ('my_setting=', {'my_setting': ''}, False, Extra.ignore, False),
            # should split on first equal sign only
            ('my_setting=value=other', {'my_setting': 'value=other'}, False, Extra.ignore, False),
            ('my_setting==', {'my_setting': '='}, False, Extra.ignore, False),
            # value should be string containing single space
            ('my_setting= ', {'my_setting': ' '}, False, Extra.ignore, False),
            #
            # Optional Testing - AdvancedSettingsModel sets 'my_setting' as Optional[String]
            #
            # Note: 'my_setting' will be None within the model, since no value can be parsed
            ('my_setting', {'my_setting': None}, True, Extra.ignore, False),
            # Note: 'my_setting' will be None in model, since my_setting is not found in string
            ('', {'my_setting': None}, True, Extra.ignore, False),
            # my_setting key not defined in advanced_settings input string
            (' =value', {'my_setting': None}, True, Extra.ignore, False),
            # my_setting key not defined in advanced_settings input string
            ('=value', {'my_setting': None}, True, Extra.ignore, False),
            # my_setting key not defined in advanced_settings input string
            ('==value', {'my_setting': None}, True, Extra.ignore, False),
            #
            # Extra fields allowed via Extra.allow in AdvancedSettingsModel Config
            #
            (
                'my_setting=val|other=val2',
                {'my_setting': 'val', 'other': 'val2'},
                True,
                Extra.allow,
                False,
            ),
            # trailing pipe
            (
                'my_setting=val|other=val2|',
                {'my_setting': 'val', 'other': 'val2'},
                True,
                Extra.allow,
                False,
            ),
            # extra pipe at start
            (
                '|my_setting=val|other=val2',
                {'my_setting': 'val', 'other': 'val2'},
                True,
                Extra.allow,
                False,
            ),
            # extra pipes at start and end of string
            (
                '|my_setting=val|other=val2|',
                {'my_setting': 'val', 'other': 'val2'},
                True,
                Extra.allow,
                False,
            ),
            # extra setting has empty key, skipped
            ('my_setting=val|=val2', {'my_setting': 'val'}, True, Extra.allow, False),
            # extra setting has empty key when stripped, skipped
            ('my_setting=val| =val2', {'my_setting': 'val'}, True, Extra.allow, False),
            # extra setting has empty value
            ('my_setting=val|other=', {'my_setting': 'val', 'other': ''}, True, Extra.allow, False),
            # setting defined in model has no value
            (
                'my_setting=|other=val2',
                {'my_setting': '', 'other': 'val2'},
                True,
                Extra.allow,
                False,
            ),
            # no entry for setting defined in model, but extra setting makes it through
            ('other=val2', {'my_setting': None, 'other': 'val2'}, True, Extra.allow, False),
            # extra setting is malformed, skipped
            ('my_setting=val|other', {'my_setting': 'val'}, True, Extra.allow, False),
            # extra setting is malformed, skipped
            ('my_setting=val|=', {'my_setting': 'val'}, True, Extra.allow, False),
            # extra setting is malformed, skipped
            ('my_setting=val|=val2', {'my_setting': 'val'}, True, Extra.allow, False),
            #
            # Fail Testing
            #
            # my_setting required, but no valid entry provided for it
            # fails because my_setting is required but was not defined in passed-in setting string
            ('=value', None, False, Extra.ignore, True),
            # fails because my_setting is required but was not defined in passed-in setting string
            (' =value', None, False, Extra.ignore, True),
            # fails because my_setting is required but was not defined in passed-in setting string
            ('my_setting', None, False, Extra.ignore, True),
            # my_setting defined twice in settings string
            ('my_setting=val|my_setting=val2', None, False, Extra.ignore, True),
            # extra field not allowed
            ('my_setting=val|other=val2', None, False, Extra.forbid, True),
        ],
    )
    def test_advanced_settings_scenarios(
        self,
        advanced_settings_string: str,
        expected_model: Dict,
        optional: bool,
        extra_config: str,
        fail_expected: bool,
        playbook_app: 'MockApp',
    ):
        """Test Advanced Settings logic relying on modify_advanced_settings validator for parsing

        NOTE: the advanced_settings INPUT is required for all scenarios of this test. The 'optional'
        parameter controls whether 'my_setting' is optional or not within the advanced settings
        MODEL.

        PytestModel here would be the Input model that defines all expected inputs for a job app,
        including the advanced_settings input. AdvancedSettingsModel is where we define
        which advanced settings are expected to be found after the advanced_settings input is parsed
        from a pipe-delimited string to a dictionary.

        The act of parsing the pipe-delimited string to a dictionary is handled by the
        modify_advanced_settings validator.

        :param advanced_settings_string: the string as passed via advaced_settings input
        :param expected_model: Dictionary that is expected to be the equivalent of calling
        tcex.inputs.model.advanced_settings.__dict__
        :param optional: whether or not 'my_setting' is optional as described above.
        :param extra_config: one of Extra.ignore, Extra.allow, Extra.forbid. Controls whether
        extra entries within the advanced settings string will make it to the final model or not
        :param fail_expected: Whether test is expected to fail or not
        """

        # "my_setting" advanced_setting entry will be required/optional depending on input
        my_setting_type = Optional[String] if optional else String

        # Model that defines entries expected in pipe-delimited advanced settings input string
        class AdvancedSettingsModel(BaseModel):
            """Model that defines all expected advanced settings entries"""

            # define "my_setting" advanced setting entry. Will be either required or optional
            # depending on value of "optional" test method input parameter.
            my_setting: my_setting_type

            # configuration class of AdvancedSettingsModel. This is not required, but allows us
            # to further define model behavior.
            class Config:
                """Datamodel config"""

                # "extra" config setting allows us to control whether we want to keep any passed-in
                # advanced settings that are not explicitly defined in our AdvancedSettingsModel.
                # Any extra settings not defined in model should be ignored by default (if this
                # config class is not included).
                extra = extra_config

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
            assert tcex.inputs.model.advanced_settings.__dict__ == expected_model
        else:
            with pytest.raises(ValidationError):
                tcex.inputs.add_model(PytestModel)
