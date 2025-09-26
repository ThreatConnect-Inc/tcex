"""TestPlaybookKeyValueApi for TcEx App Playbook Key Value API Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook Key Value API Module,
specifically testing TCKeyValueAPI functionality including variable creation, reading,
and validation across various data types including binary, string, key-value, and
TC entity variables using the ThreatConnect Key Value API backend.

Classes:
    MockApi: Mock class for simulating TC API responses
    TestPlaybookKeyValueApi: Test class for TcEx App Playbook Key Value API Module functionality

TcEx Module Tested: app.key_value_store.key_value_api
"""


from collections.abc import Callable
from typing import Any


import pytest


from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tests.mock_app import MockApp


class MockApi:
    """Mock tcex session.get() method.

    This mock class simulates the behavior of TC API responses for testing
    purposes, providing mock properties for content, headers, ok status,
    reason, and text that match the expected API response interface.
    """

    def __init__(self, ok: bool = True) -> None:
        """Initialize instance properties.

        Args:
            ok: Whether the mock API response should indicate success
        """
        super().__init__()
        self._content = None
        self._ok = ok

    @property
    def content(self) -> Any:
        """Mock content property.

        Returns:
            The mock content value stored in the instance
        """
        return self._content

    @content.setter
    def content(self, content: Any) -> None:
        """Mock content property setter.

        Args:
            content: The content value to store in the mock response
        """
        self._content = content

    @property
    def headers(self) -> dict[str, str]:
        """Mock headers property.

        Returns:
            Mock headers with content-type application/json
        """
        return {'content-type': 'application/json'}

    @property
    def ok(self) -> bool:
        """Mock ok property.

        Returns:
            Whether the mock API response indicates success
        """
        return self._ok

    @property
    def reason(self) -> str:
        """Mock reason property.

        Returns:
            Mock reason text for the API response
        """
        return 'reason'

    @property
    def text(self) -> Any:
        """Mock text property.

        Returns:
            The mock content value (alias for content property)
        """
        return self.content


class TestPlaybookKeyValueApi:
    """TestPlaybookKeyValueApi for TcEx App Playbook Key Value API Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook Key Value API Module,
    covering various data type scenarios including binary, string, key-value, and TC entity
    variables using the TCKeyValueAPI backend with proper mocking and validation.
    """

    tc_playbook_out_variables: list[str] | None = None

    def setup_class(self) -> None:
        """Configure setup before all tests.

        This method is called once before all test methods in the class to initialize
        the playbook output variables list that defines the expected output structure
        for playbook key value API testing scenarios.
        """
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

    def setup_method(self) -> None:
        """Configure setup before all tests.

        This method is called before each test method to reset scoped and cached
        properties, ensuring a clean testing environment for each test case.
        """
        scoped_property._reset()  # noqa: SLF001
        cached_property._reset()  # noqa: SLF001

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0001:b1!Binary', b'not really binary', id='pass-binary-data'),
            pytest.param(
                '#App:0001:ba1!BinaryArray',
                [b'not', b'really', b'binary'],
                id='pass-binary-array-data',
            ),
            pytest.param(
                '#App:0001:kv1!KeyValue', {'key': 'one', 'value': '1'}, id='pass-keyvalue-data'
            ),
            pytest.param(
                '#App:0001:kva1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
                id='pass-keyvalue-array-data',
            ),
            pytest.param('#App:0001:s1!String', '1', id='pass-string-data-1'),
            pytest.param('#App:0001:s2!String', '2', id='pass-string-data-2'),
            pytest.param('#App:0001:s3!String', '3', id='pass-string-data-3'),
            pytest.param('#App:0001:s4!String', '4', id='pass-string-data-4'),
            pytest.param('#App:0001:sa1!StringArray', ['a', 'b', 'c'], id='pass-string-array-data'),
            pytest.param(
                '#App:0001:te1!TCEntity',
                {'id': '123', 'type': 'Address', 'value': '1.1.1.1'},
                id='pass-tcentity-data',
            ),
            pytest.param(
                '#App:0001:tea1!TCEntityArray',
                [
                    {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                    {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                ],
                id='pass-tcentity-array-data',
            ),
            # is it possible to send bytes to API?
            # ('#App:0001:r1!Raw', b'raw data'),
            pytest.param('#App:0001:dup.name!String', 'dup name', id='pass-duplicate-name-string'),
            pytest.param(
                '#App:0001:dup.name!StringArray',
                ['dup name'],
                id='pass-duplicate-name-string-array',
            ),
        ],
    )
    def test_playbook_key_value_api(
        self,
        variable: str,
        value: Any,
        playbook_app: Callable[..., MockApp],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test Playbook Key Value API for TcEx App Playbook Key Value API Module.

        This test case verifies that the TCKeyValueAPI functionality works correctly
        by testing various data types including binary, string, key-value, and TC entity
        variables through the ThreatConnect Key Value API backend with proper mocking
        and validation of create and read operations.

        Parameters:
            variable: The playbook variable to test with TCKeyValueAPI backend
            value: The data value to store and retrieve through the API

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
            monkeypatch: Pytest fixture for patching object attributes during testing
        """
        tcex = playbook_app(
            config_data={
                'tc_playbook_out_variables': self.tc_playbook_out_variables,
                'tc_playbook_db_type': 'TCKeyValueAPI',
            }
        ).tcex

        # parse variable and send to create_output() method
        variable_model = tcex.util.get_playbook_variable_model(variable)
        if variable_model is None:
            error_msg = f'Invalid variable ({variable})'
            raise RuntimeError(error_msg)

        # setup mock key value api service
        mock_api = MockApi()

        # monkeypatch put method
        def mp_put(*_args, **kwargs):
            mock_api.content = kwargs.get('data')
            return mock_api

        # monkeypatch get method
        def mp_get(*_args, **_kwargs):
            return mock_api

        monkeypatch.setattr(tcex.session.tc, 'get', mp_get)
        monkeypatch.setattr(tcex.session.tc, 'put', mp_put)

        tcex.app.playbook.create.variable(variable_model.key, value, variable_model.type)
        result = tcex.app.playbook.read.variable(variable)
        assert result == value, f'result of ({result}) does not match ({value})'
