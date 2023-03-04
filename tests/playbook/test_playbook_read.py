"""Test the TcEx Batch Module."""
# standard library
from collections.abc import Callable

# third-party
import pytest

# first-party
from tcex.playbook.playbook import Playbook  # TYPE-CHECKING
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestUtils:
    """Test the TcEx Batch Module."""

    tc_playbook_out_variables = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.tc_playbook_out_variables = [
            '#App:0001:b1!Binary',
            '#App:0001:ba1!BinaryArray',
            '#App:0001:kv1!KeyValue',
            '#App:0001:kva1!KeyValueArray',
            '#App:0001:s1!String',
            '#App:0001:sa1!StringArray',
            '#App:0001:te1!TCEntity',
            '#App:0001:tea1!TCEntityArray',
            # '#App:0001:tee1!TCEnhanceEntity',
            '#App:0001:r1!Raw',
        ]

    @pytest.mark.parametrize(
        'variable,type_,should_fail',
        [
            ('#App:0001:b1!Binary', 'Binary', False),
            ('#App:0001:kv1!KeyValue', 'KeyValue', False),
            ('#App:0001:s1!String', 'String', False),
            ('#App:0001:te1!TCEntity', 'TCEntity', False),
            # fail tests
            ('#App:0001:b1!Binary', 'String', True),
        ],
    )
    def test_playbook_read_check_variable_type(
        self, variable: str, type_: str, should_fail: bool, playbook_app: Callable[..., MockApp]
    ):
        """Test playbook variables."""
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.playbook

        if should_fail is False:
            assert True
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.read._check_variable_type(variable, type_)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'value,expected',
        [
            (True, 'true'),
            (1.1, '1.1'),
            (1, '1'),
            ('string', 'string'),
            (None, None),
        ],
    )
    def test_playbook_read_coerce_string_value(
        self, value: bool | float | int | str, expected: str, playbook: Playbook
    ):
        """Test playbook variables."""
        assert playbook.read._coerce_string_value(value) == expected

    @pytest.mark.parametrize(
        'data,expected',
        [
            (b'123', '123'),
        ],
    )
    def test_playbook_read_decode_binary(self, data: bytes, expected: str, playbook: Playbook):
        """Test playbook variables."""
        assert playbook.read._decode_binary(data) == expected
