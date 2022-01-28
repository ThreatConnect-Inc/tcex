"""Class that contains shared logic that may be used by Input test suites"""
# standard library
from typing import TYPE_CHECKING

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types.sensitive import Sensitive
from tcex.pleb.registry import registry

if TYPE_CHECKING:
    # first-party
    from tests.mock_app import MockApp


class InputTest:
    """Class that contains shared logic used by Input test suites"""

    @staticmethod
    def _stage_key_value(config_key, variable_name, value, tcex):
        """Write values to key value store. Expects dictionary of variable_name: value"""
        registry.Playbook.create.any(variable_name, value, validate=False, when_requested=False)

        # force inputs to resolve newly inserted key-values from key value store
        if 'contents_resolved' in tcex.inputs.__dict__:
            del tcex.inputs.__dict__['contents_resolved']

        # inputs get resolved during instantiation of tcex. This means that variables like
        # '#App:1234:my_binary!Binary' were resolved to None before having the chance to be
        # stage update inputs contents cached property from None to correct variable name so
        # that inputs contents_resolved logic may resolve variable
        #
        # UPDATE: tcex code now relies on inputs.model_unresolved, so the tcex should not resolve
        # the variable to None, but leaving this code here just in case tcex is changed to use
        # inputs.model at some point.
        tcex.inputs.__dict__['contents'][config_key] = variable_name

        # since tcex code is not using inputs.model, call it here to ensure variables are resolved
        _ = tcex.inputs.model

    def _type_validation(
        self,
        model: 'BaseModel',
        input_name: str,
        input_value: str,
        input_type: str,
        expected: str,
        fail_test: bool,
        playbook_app: 'MockApp',
    ):
        """Test type validation."""
        config_data = {input_name: f'#App:1234:{input_name}!{input_type}'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value(input_name, f'#App:1234:{input_name}!{input_type}', input_value, tcex)

        validation_ran = False
        if fail_test is True:
            with pytest.raises(ValidationError) as exc_info:
                tcex.inputs.add_model(model)

            err_msg = str(exc_info.value)
            validation_ran = True
            assert 'validation error' in err_msg
        else:
            tcex.inputs.add_model(model)
            model_input_value = getattr(tcex.inputs.model, input_name)
            if isinstance(model_input_value, list):
                # validate empty array
                if not model_input_value:
                    validation_ran = True
                    assert model_input_value == expected, f'{model_input_value } != {expected}'

                # validate all array types
                for index, item in enumerate(model_input_value):
                    if isinstance(item, BaseModel):
                        # validate all array model types, assuming the models
                        # convert to dicts that match the expected value.
                        item = model_input_value[index].dict(exclude_unset=True)
                        expected = expected[index]

                        validation_ran = True
                        assert item == expected, f'{item} != {expected}'
                    else:
                        # validate all array non-model types
                        expected = expected[index]
                        validation_ran = True
                        assert item == expected, f'{item} != {expected}'
            elif isinstance(model_input_value, BaseModel):
                # validate all non-array model types, assuming the models
                # convert to dicts that match the expected value.
                validation_ran = True
                assert (
                    model_input_value.dict(exclude_unset=True) == expected
                ), f'{model_input_value} != {expected}'
            elif isinstance(model_input_value, Sensitive):
                # validate all non-array, non-model types
                validation_ran = True
                assert model_input_value.value == expected, f'{model_input_value} != {expected}'
                # manual testing of sensitive_filter
                tcex.log.error(model_input_value.value)
            else:
                # validate all non-array, non-model types
                validation_ran = True
                assert model_input_value == expected, f'{model_input_value} != {expected}'

        assert validation_ran is True
