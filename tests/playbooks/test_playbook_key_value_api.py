"""Test the TcEx Batch Module."""
# third-party
import pytest


class MockApi:
    """Mock tcex session.get() method."""

    def __init__(self, ok=True):
        """Initialize class properties."""
        super().__init__()
        self._content = None
        self._ok = ok

    @property
    def content(self):
        """Mock content property"""
        return self._content

    @content.setter
    def content(self, content):
        """Mock content property"""
        self._content = content

    @property
    def headers(self):
        """Mock headers property"""
        return {'content-type': 'application/json'}

    @property
    def ok(self):
        """Mock ok property"""
        return self._ok

    @property
    def reason(self):
        """Mock text property"""
        return 'reason'

    @property
    def text(self):
        """Mock text property"""
        return self.content


# pylint: disable=no-self-use
class TestPlaybookKeyValueApi:
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
            '#App:0001:r1!Raw',
            '#App:0001:dup.name!String',
            '#App:0001:dup.name!StringArray',
        ]

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
            ('#App:0001:r1!Raw', 'raw data'),
            ('#App:0001:dup.name!String', 'dup name'),
            ('#App:0001:dup.name!StringArray', ['dup name']),
        ],
    )
    def test_playbook_key_value_api(self, variable, value, playbook_app, monkeypatch):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={
                'tc_playbook_out_variables': self.tc_playbook_out_variables,
                'tc_playbook_db_type': 'TCKeyValueAPI',
            }
        ).tcex

        # parse variable and send to create_output() method
        parsed_variable = tcex.playbook.parse_variable(variable)
        variable_name = parsed_variable.get('name')
        variable_type = parsed_variable.get('type')

        # setup mock key value api service
        mock_api = MockApi()

        # monkeypatch put method
        def mp_put(*args, **kwargs):  # pylint: disable=unused-argument
            mock_api.content = kwargs.get('data')
            return mock_api

        # monkeypatch get method
        def mp_get(*args, **kwargs):  # pylint: disable=unused-argument
            return mock_api

        monkeypatch.setattr(tcex.session, 'get', mp_get)
        monkeypatch.setattr(tcex.session, 'put', mp_put)

        tcex.playbook.create_output(variable_name, value, variable_type)
        result = tcex.playbook.read(variable)
        assert result == value, f'result of ({result}) does not match ({value})'
