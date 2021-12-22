"""Test the TcEx Batch Module."""
# standard library
from typing import TYPE_CHECKING, Any, List

# third-party
import pytest

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx
    from tcex.playbook.playbook import Playbook
    from tests.mock_app import MockApp


# pylint: disable=no-self-use
class TestUtils:
    """Test the TcEx Batch Module."""

    tc_playbook_out_variables = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.tc_playbook_out_variables = [
            '#App:0001:b1!Binary',
            '#App:0001:b2!Binary',
            '#App:0001:b3!Binary',
            '#App:0001:b4!Binary',
            '#App:0001:ba1!BinaryArray',
            '#App:0001:ba2!BinaryArray',
            '#App:0001:ba3!BinaryArray',
            '#App:0001:ba4!BinaryArray',
            '#App:0001:kv1!KeyValue',
            '#App:0001:kv2!KeyValue',
            '#App:0001:kv3!KeyValue',
            '#App:0001:kv4!KeyValue',
            '#App:0001:kva1!KeyValueArray',
            '#App:0001:kva2!KeyValueArray',
            '#App:0001:kva3!KeyValueArray',
            '#App:0001:kva4!KeyValueArray',
            '#App:0001:s1!String',
            '#App:0001:s2!String',
            '#App:0001:s3!String',
            '#App:0001:s4!String',
            '#App:0001:sa1!StringArray',
            '#App:0001:sa2!StringArray',
            '#App:0001:sa3!StringArray',
            '#App:0001:sa4!StringArray',
            '#App:0001:te1!TCEntity',
            '#App:0001:te2!TCEntity',
            '#App:0001:te3!TCEntity',
            '#App:0001:te4!TCEntity',
            '#App:0001:tea1!TCEntityArray',
            '#App:0001:tea2!TCEntityArray',
            '#App:0001:tea3!TCEntityArray',
            '#App:0001:tea4!TCEntityArray',
            # '#App:0001:tee1!TCEnhanceEntity',
            # '#App:0001:teea1!TCEnhanceEntityArray',
            '#App:0001:r1!Raw',
            '#App:0001:dup.name!String',
            '#App:0001:dup.name!StringArray',
        ]

    def test_playbook_check_key_requested(self, playbook_app: 'MockApp'):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        assert playbook.check_key_requested('b1') is True

    def test_playbook_check_variable_requested(self, playbook_app: 'MockApp'):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook
        assert playbook.check_variable_requested('#App:0001:b1!Binary') is True

    @pytest.mark.parametrize(
        'output_data',
        [
            (
                [
                    {'variable': '#App:0001:b1!Binary', 'value': b'bytes'},
                    {
                        'variable': '#App:0001:ba1!BinaryArray',
                        'value': [b'not', b'really', b'binary'],
                    },
                    {'variable': '#App:0001:kv1!KeyValue', 'value': {'key': 'one', 'value': '1'}},
                    {
                        'variable': '#App:0001:kva1!KeyValueArray',
                        'value': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
                    },
                    {
                        'variable': '#App:0001:kva1!KeyValueArray',
                        'value': {'key': 'three', 'value': '3'},
                    },
                    {'variable': '#App:0001:s1!String', 'value': '1'},
                    {'variable': '#App:0001:sa1!StringArray', 'value': ['a', 'b', 'c']},
                    {'variable': '#App:0001:sa1!StringArray', 'value': ['d', 'e', 'f']},
                    {
                        'variable': '#App:0001:te1!TCEntity',
                        'value': {'id': '123', 'type': 'Address', 'value': '1.1.1.1'},
                    },
                    {
                        'variable': '#App:0001:tea1!TCEntityArray',
                        'value': [
                            {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                            {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                        ],
                    },
                    {'variable': '#App:0001:r1!Raw', 'value': b'raw data'},
                    {'variable': '#App:0001:n1!None', 'value': None},
                ]
            )
        ],
    )
    def test_playbook_output_add_all(self, output_data: List[dict], playbook_app: 'MockApp'):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        # add all output
        expected_data = {}
        for od in output_data:
            variable = od.get('variable')
            value = od.get('value')

            variable_model = tcex.utils.get_playbook_variable_model(variable)
            playbook.output.add(variable_model.key, value, variable_model.type)

            if variable in expected_data:
                if isinstance(value, list):
                    expected_data[variable].extend(value)
                else:
                    expected_data[variable].append(value)
            else:
                expected_data.setdefault(variable, value)

        # write output
        playbook.output.create()

        # validate output
        for variable, value in expected_data.items():
            result = playbook.read.variable(variable)

            assert result == value, f'result of ({result}) does not match ({value})'

            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'output_data',
        [
            (
                [
                    {'variable': '#App:0001:b1!Binary', 'value': b'bytes'},
                    {
                        'variable': '#App:0001:ba1!BinaryArray',
                        'value': [b'not', b'really', b'binary'],
                    },
                    {'variable': '#App:0001:kv1!KeyValue', 'value': {'key': 'one', 'value': '1'}},
                    {
                        'variable': '#App:0001:kva1!KeyValueArray',
                        'value': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
                    },
                    {'variable': '#App:0001:s1!String', 'value': '1'},
                    {'variable': '#App:0001:sa1!StringArray', 'value': ['a', 'b', 'c']},
                    {'variable': '#App:0001:sa1!StringArray', 'value': ['d', 'e', 'f']},
                    {
                        'variable': '#App:0001:te1!TCEntity',
                        'value': {'id': '123', 'type': 'Address', 'value': '1.1.1.1'},
                    },
                    {
                        'variable': '#App:0001:tea1!TCEntityArray',
                        'value': [
                            {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                            {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                        ],
                    },
                    {'variable': '#App:0001:r1!Raw', 'value': b'raw data'},
                    {'variable': '#App:0001:n1!None', 'value': None},
                ]
            )
        ],
    )
    def test_playbook_output_add_no_append(self, output_data: List[dict], playbook_app: 'MockApp'):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        # add all output
        expected_data = {}
        for od in output_data:
            variable = od.get('variable')
            value = od.get('value')

            variable_model = tcex.utils.get_playbook_variable_model(variable)
            playbook.output.add(variable_model.key, value, variable_model.type, append_array=False)

            expected_data[variable] = value

        # write output
        playbook.output.create()

        # validate output
        for variable, value in expected_data.items():
            result = tcex.playbook.read.variable(variable)

            assert result == value, f'result of ({result}) does not match ({value})'

            tcex.playbook.delete.variable(variable)
            assert tcex.playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'output_data',
        [
            (
                [
                    {
                        'variable': '#App:0001:sa1!StringArray',
                        'value': ['a', 'b', None, 'c'],
                        'expected': ['a', 'b', None, 'c'],
                        'append': True,
                    },
                    {
                        'variable': '#App:0001:sa2!StringArray',
                        'value': [['d', 'e'], None],
                        'expected': ['d', 'e'],
                        'append': False,
                    },
                ]
            )
        ],
    )
    def test_playbook_output_add_append_logic(
        self, output_data: List[dict], playbook_app: 'MockApp'
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        # reset previous outputs
        playbook.output.data = {}

        # add all output
        expected_data = {}
        for od in output_data:
            variable = od.get('variable')
            value = od.get('value')

            variable_model = tcex.utils.get_playbook_variable_model(variable)
            for v in value:
                playbook.output.add(
                    variable_model.key, v, variable_model.type, append_array=od.get('append')
                )

            expected_data[variable] = od.get('expected')

        # write output
        playbook.output.create()

        # validate output
        for variable, value in expected_data.items():
            result = tcex.playbook.read.variable(variable)

            assert result == value, f'result of ({result}) does not match ({value})'

            tcex.playbook.delete.variable(variable)
            assert tcex.playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0001:b1!Binary', b'not really binary'),
            ('#App:0001:ba1!BinaryArray', [b'not', b'really', b'binary']),
            ('#App:0001:kv1!KeyValue', {'key': 'one', 'value': '1'}),
            (
                '#App:0001:kva1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
            ),
            ('#App:0001:s1!String', '1'),
            ('#App:0001:s2!String', '2'),
            ('#App:0001:s3!String', '3'),
            ('#App:0001:s4!String', '4'),
            ('#App:0001:sa1!StringArray', ['a', 'b', 'c']),
            ('#App:0001:te1!TCEntity', {'id': '123', 'type': 'Address', 'value': '1.1.1.1'}),
            (
                '#App:0001:tea1!TCEntityArray',
                [
                    {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                    {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                ],
            ),
            ('#App:0001:r1!Raw', b'raw data'),
            ('#App:0001:dup.name!String', 'dup name'),
            ('#App:0001:dup.name!StringArray', ['dup name']),
        ],
    )
    def test_playbook_create_variable(self, variable: str, value: Any, playbook_app: 'MockApp'):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        # parse variable and send to output.variable() method
        variable_model = tcex.utils.get_playbook_variable_model(variable)
        playbook.create.variable(variable_model.key, value, variable_model.type)
        result = playbook.read.variable(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0001:b1!Binary', b'not really binary'),
            ('#App:0001:ba1!BinaryArray', [b'not', b'really', b'binary']),
            ('#App:0001:kv1!KeyValue', {'key': 'one', 'value': '1'}),
            (
                '#App:0001:kva1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
            ),
            ('#App:0001:s1!String', '1'),
            ('#App:0001:s2!String', '2'),
            ('#App:0001:s3!String', '3'),
            ('#App:0001:s4!String', '4'),
            ('#App:0001:sa1!StringArray', ['a', 'b', 'c']),
            ('#App:0001:te1!TCEntity', {'id': '123', 'type': 'Address', 'value': '1.1.1.1'}),
            (
                '#App:0001:tea1!TCEntityArray',
                [
                    {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                    {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                ],
            ),
            ('#App:0001:r1!Raw', b'raw data'),
        ],
    )
    def test_playbook_output_variable_without_type(
        self, variable: str, value: Any, playbook_app: 'MockApp'
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        # parse variable and send to output.variable() method
        variable_model = tcex.utils.get_playbook_variable_model(variable)

        playbook.create.variable(variable_model.key, value)
        result = playbook.read.variable(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0001:not_requested!String', 'not requested'),
            ('#App:0001:none!String', 'None'),
            ('#App:0001:dup.name!String', None),
            ('#App:0001:dup.name!StringArray', None),
        ],
    )
    def test_playbook_output_variable_not_written(
        self, variable: str, value: Any, playbook_app: 'MockApp'
    ):
        """Test playbook variables."""
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        # parse variable and send to output.variable() method
        variable_model = tcex.utils.get_playbook_variable_model(variable)
        playbook.create.variable(variable_model.key, value, variable_model.type)

        result = playbook.read.variable(variable)
        assert result is None, f'result of ({result}) should be None'

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0001:not_requested!String', 'not requested'),
            ('#App:0001:none!String', None),
            (None, None),  # coverage
        ],
    )
    def test_playbook_output_variable_not_written_without_type(self, variable, value, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        # parse variable and send to output.variable() method
        variable_model = tcex.utils.get_playbook_variable_model(variable)
        variable_key = None  # coverage
        if variable is not None:
            variable_key = variable_model.key
        playbook.create.variable(variable_key, value)

        result = playbook.read.variable(variable)
        assert result is None, f'result of ({result}) should be None'

    # @pytest.mark.parametrize(
    #     'variable,value',
    #     [('#App:0001:s1!String', '1')],
    # )
    # def test_playbook_read_array(self, variable, value, playbook_app):
    #     """Test the create output method of Playbook module.

    #     Args:
    #         variable (str): The key/variable to create in Key Value Store.
    #         value (str): The value to store in Key Value Store.
    #         playbook_app (callable, fixture): The playbook_app fixture.
    #     """
    #     tcex: 'TcEx' = playbook_app(
    #         config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
    #     ).tcex
    #     playbook: 'Playbook' = tcex.playbook

    #     # parse variable and send to output.variable() method
    #     variable_model = tcex.utils.get_playbook_variable_model(variable)
    #     playbook.create.variable(variable_model.key, value, variable_model.type)
    #     result = playbook.read_array(variable)
    #     assert result == [value], f'result of ({result}) does not match ({value})'

    #     playbook.delete.variable(variable)
    #     assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [('#App:0001:s1!String', '1')],
    )
    def test_playbook_read(self, variable, value, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        # parse variable and send to output.variable() method
        variable_model = tcex.utils.get_playbook_variable_model(variable)
        playbook.create.variable(variable_model.key, value, variable_model.type)
        result = playbook.read.variable(variable, True)
        assert result == [value], f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    def test_playbook_read_none_array(self, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex: 'TcEx' = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook: 'Playbook' = tcex.playbook

        # parse variable and send to output.variable() method
        result = playbook.read.variable('#App:0001:none!String', True)
        assert result == [], f'result of ({result}) does not match ([])'

    # @pytest.mark.parametrize(
    #     'variable,value,alt_variable,alt_value,expected',
    #     [
    #         ('#App:0001:s1!String', '1', '#App:0001:s2!String', '2', '1'),
    #         ('-- Select --', None, '#App:0001:s2!String', '6', None),
    #         ('-- Variable Input --', None, '#App:0001:s2!String', '7', '7'),
    #         (None, None, '#App:0001:s2!String', '8', None),
    #         ('-- Variable Input --', None, None, None, None),
    #     ],
    # )
    # def test_playbook_read_choice(
    #     self, variable, value, alt_variable, alt_value, expected, playbook_app
    # ):
    #     """Test the create output method of Playbook module.

    #     Args:
    #         variable (str): The key/variable to create in Key Value Store.
    #         value (str): The value to store in Key Value Store.
    #         playbook_app (callable, fixture): The playbook_app fixture.
    #     """
    #     tcex: 'TcEx' = playbook_app(
    #         config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
    #     ).tcex
    #     playbook: 'Playbook' = tcex.playbook

    #     # parse variable and send to output.variable() method
    #     if value is not None:
    #         variable_model = tcex.utils.get_playbook_variable_model(variable)
    #         playbook.create.variable(variable_model.key, value, variable_model.type)

    #     # parse alt variable and send to output.variable() method
    #     if alt_value is not None:
    #         variable_model = tcex.utils.get_playbook_variable_model(variable)
    #         playbook.output.variable(variable_model.key, alt_value, variable_model.type)

    #     # read choice
    #     result = playbook.read_choice(variable, alt_variable)
    #     assert result == expected, f'result of ({result}) does not match ({expected})'

    #     # cleanup
    #     if value is not None:
    #         playbook.delete.variable(variable)
    #         assert playbook.read.variable(variable) is None
    #     if alt_value is not None:
    #         playbook.delete.variable(alt_variable)
    #         assert playbook.read.variable(alt_variable) is None
