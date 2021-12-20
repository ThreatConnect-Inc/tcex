"""Test the TcEx Batch Module."""
# standard library
from typing import TYPE_CHECKING, Any, Iterable, List, Optional, Union

# third-party
import pytest

if TYPE_CHECKING:
    # first-party
    from tcex.playbook.playbook import Playbook


# pylint: disable=no-self-use
class TestUtils:
    """Test the TcEx Batch Module."""

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:s1!String', 1),
            ('#App:0002:s2!String', '2'),
            ('#App:0002:s3!String', '3'),
            ('#App:0002:s4!String', True),
        ],
    )
    def test_playbook_string_pass(
        self, variable: str, value: Union[bool, int, str], playbook: 'Playbook'
    ):
        """Test playbook variables."""
        playbook.create.string(variable, value, when_requested=False)
        result = playbook.read.string(variable)
        value = str(value).lower()
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:s1!String', []),
            ('#App:0002:s2!String', {}),
            ('#App:0002:s3!String', b'bytes'),
            ('#App:0002:b3!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_string_fail(self, variable: str, value: Any, playbook: 'Playbook'):
        """Test playbook variables."""
        try:
            playbook.create.string(variable, value, when_requested=False)
            assert False, f'{value} is not a valid String value'
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:sa1!StringArray', ['1', '1']),
            ('#App:0003:sa2!StringArray', ['2', '2']),
            ('#App:0003:sa3!StringArray', ['3', '3']),
            ('#App:0003:sa4!StringArray', ['4', '4']),
        ],
    )
    def test_playbook_string_array_pass(
        self, variable: str, value: List[str], playbook: 'Playbook'
    ):
        """Test playbook variables."""
        playbook.create.string_array(variable, value, when_requested=False)
        result = playbook.read.string_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    # @pytest.mark.parametrize(
    #     'variable,value',
    #     [('#App:0003:sa5!StringArray', 'foobar')],
    # )
    # def test_playbook_string_array_string(self, variable: str, value: Str, playbook: 'Playbook'):
    #     """Test playbook variables."""
    #     with pytest.raises(RuntimeError) as exc_info:
    #         playbook.create.string_array(variable, value, when_requested=False)

    #     assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:sa1!StringArray', ['1', []]),
            ('#App:0003:sa2!StringArray', ['2', {}]),
            ('#App:0003:sa3!StringArray', ['3', b'bytes']),
            ('#App:0003:sa5!StringArray', 'foobar'),
            ('#App:0002:b3!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_string_array_fail(self, variable: str, value: Any, playbook: 'Playbook'):
        """Test playbook variables."""
        with pytest.raises(RuntimeError) as ex:
            playbook.create.string_array(variable, value, when_requested=False)

        assert 'Invalid ' in str(ex.value)

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:sa5!StringArray', ('6', '6')),
            ('#App:0003:sa6!StringArray', map(lambda a: a, ['6', '6'])),
            ('#App:0003:sa6!StringArray', filter(lambda a: True, ['6', '6'])),
        ],
    )
    def test_playbook_string_array_iterables(
        self, variable: str, value: Iterable, playbook: 'Playbook'
    ):
        """Test playbook variables."""
        playbook.create.string_array(variable, value, when_requested=False)
        result = playbook.read.string_array(variable)
        assert result == ['6', '6'], f'result of ({result}) does not match ({list(value)})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    #
    # Type Specific
    #

    @pytest.mark.parametrize(
        'variable,value',
        [('#App:0002:s1!String', None)],
    )
    def test_playbook_string_none(self, variable: str, value: Optional[str], playbook: 'Playbook'):
        """Test playbook variables."""
        playbook.create.string(variable, value, when_requested=False)
        playbook.read.string(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [('#App:0003:sa1!StringArray', None)],
    )
    def test_playbook_string_array_none(
        self, variable: str, value: Optional[list], playbook: 'Playbook'
    ):
        """Test playbook variables."""
        playbook.create.string_array(variable, value, when_requested=False)
        playbook.read.string_array(variable)
        assert playbook.read.variable(variable) is None

    def test_playbook_string_read_none(self, playbook: 'Playbook'):
        """Test playbook variables."""
        assert playbook.read.string(None) is None
