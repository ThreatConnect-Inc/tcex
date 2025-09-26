"""TestAdvancedRequest for TcEx App Playbook Advanced Request Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook Advanced Request Module,
specifically testing the advanced HTTP request functionality including GET, POST, error handling,
parameter management, header configuration, and various request body formats across different
HTTP methods and response scenarios.

Classes:
    TestAdvancedRequest: Test class for TcEx App Playbook Advanced Request Module functionality

TcEx Module Tested: app.playbook.advanced_request
"""


import contextlib
import json
from http import HTTPStatus
from collections.abc import Callable


import pytest


from tcex import TcEx
from tcex.app.playbook.advanced_request import AdvancedRequest
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tests.mock_app import MockApp


class TestAdvancedRequest:
    """TestAdvancedRequest for TcEx App Playbook Advanced Request Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook Advanced Request Module,
    covering various HTTP request scenarios including standard GET requests, error handling
    for 500 status codes, parameter exclusion logic, POST requests with different body formats,
    and URL encoding functionality.
    """

    # properties
    tc_playbook_out_variables: list[str] | None = None

    def setup_method(self) -> None:
        """Configure setup before all tests.

        This method is called before each test method to reset scoped and cached
        properties, ensuring a clean testing environment for each test case.
        """
        scoped_property._reset()  # noqa: SLF001
        cached_property._reset()  # noqa: SLF001

    @staticmethod
    def _load_data(tcex: TcEx, context: str) -> dict:
        """Load data from Redis into a dict.

        This utility method loads data from the Redis key-value store for a given context,
        handling special cases for headers that require double JSON parsing and converting
        binary data to appropriate formats for testing validation.

        Args:
            tcex: TcEx instance with Redis client configured
            context: The context string for the key-value store

        Returns:
            Dictionary containing the loaded data with proper type conversion
        """
        data = {}
        for k, v in tcex.app.key_value_store.redis_client.hgetall(context).items():  # type: ignore
            if k.decode() == '#App:0001:pytest.request.headers!String':
                data[k.decode()] = json.loads(json.loads(v.decode()))
            else:
                data[k.decode()] = json.loads(v.decode())
        return data

    def setup_class(self) -> None:
        """Configure setup before all tests.

        This method is called once before all test methods in the class to initialize
        the playbook output variables list that defines the expected output structure
        for advanced request testing scenarios.
        """
        self.tc_playbook_out_variables = [
            '#App:0001:pytest.request.headers!String',
            '#App:0001:pytest.request.ok!String',
            '#App:0001:pytest.request.reason!String',
            '#App:0001:pytest.request.status_code!String',
            '#App:0001:pytest.request.url!String',
            '#App:0001:pytest.request.content!String',
            '#App:0001:pytest.request.content.binary!Binary',
        ]

    @staticmethod
    def test_advanced_request_get_standard(playbook_app: Callable[..., MockApp]) -> None:
        """Test Advanced Request GET Standard Functionality for TcEx App Playbook Advanced Request Module.

        This test case verifies that the advanced request feature works correctly for standard
        GET requests by testing parameter handling, header configuration, response validation,
        and proper URL construction with query parameters.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            ij_data={
                'params': [
                    {
                        'label': 'HTTP Method',
                        'name': 'tc_adv_req_http_method',
                        'required': True,
                        'sequence': 99,
                        'type': 'Choice',
                        'validValues': ['DELETE', 'GET', 'POST', 'PUT'],
                    },
                ]
            },
            config_data={
                'tc_adv_req_exclude_null_params': False,
                'tc_adv_req_fail_on_error': False,
                'tc_adv_req_urlencode_body': False,
                'tc_adv_req_body': None,
                'tc_adv_req_headers': [{'key': 'pytest', 'value': 'pytest'}],
                'tc_adv_req_http_method': 'GET',
                'tc_adv_req_params': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': ''}],
                'tc_adv_req_path': '/anything',
            },
        ).tcex

        se = tcex.session.external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = AdvancedRequest(
            model=tcex.inputs.model_advanced_request,
            playbook=tcex.app.playbook,
            session=se,
            output_prefix='pytest',
            timeout=60,
        )
        r = ar.request()
        if r is None:
            pytest.fail('Request should not be None.')
        data = r.json()

        assert r.request.url == data.get('url')
        assert r.status_code == HTTPStatus.OK
        # assert headers
        assert data.get('headers', {}).get('Pytest') == 'pytest'
        assert 'TcEx/5' in data.get('headers', {}).get('User-Agent')
        # assert params
        assert data.get('args', {}).get('one') == '1'
        assert data.get('args', {}).get('two') == ''

    def test_advanced_request_get_500(self, playbook_app: Callable[..., MockApp]) -> None:
        """Test Advanced Request GET 500 Error Handling for TcEx App Playbook Advanced Request Module.

        This test case verifies that the advanced request feature correctly handles 500 status
        code responses by testing error handling, output variable creation, and proper
        playbook output data storage for failed requests.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            ij_data={
                'params': [
                    {
                        'label': 'HTTP Method',
                        'name': 'tc_adv_req_http_method',
                        'required': True,
                        'sequence': 99,
                        'type': 'Choice',
                        'validValues': ['DELETE', 'GET', 'POST', 'PUT'],
                    },
                ]
            },
            config_data={
                'tc_playbook_out_variables': self.tc_playbook_out_variables,
                'tc_adv_req_exclude_null_params': False,
                'tc_adv_req_fail_on_error': True,
                'tc_adv_req_urlencode_body': False,
                'tc_adv_req_body': None,
                'tc_adv_req_headers': [{'key': 'pytest', 'value': 'pytest'}],
                'tc_adv_req_http_method': 'GET',
                'tc_adv_req_params': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': ''}],
                'tc_adv_req_path': '/status/500',
            },
        ).tcex

        se = tcex.session.external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = AdvancedRequest(
            model=tcex.inputs.model_advanced_request,
            playbook=tcex.app.playbook,
            session=se,
            output_prefix='pytest',
            timeout=60,
        )
        with contextlib.suppress(RuntimeError):
            ar.request()

        with contextlib.suppress(SystemExit):
            # the write_output method is called in exit method
            tcex.exit.exit(1)

        # load output data from KV store to validate
        context = tcex.inputs.model.tc_playbook_kvstore_context
        if context is not None:
            data = self._load_data(tcex, context)

            assert data.get('#App:0001:pytest.request.reason!String') == 'INTERNAL SERVER ERROR'
            assert data.get('#App:0001:pytest.request.content!String') == ''
            assert data.get('#App:0001:pytest.request.headers!String', {}).get('Server') == 'nginx'
            assert data.get('#App:0001:pytest.request.status_code!String') == '500'
            assert data.get('#App:0001:pytest.request.content.binary!Binary') == ''
            assert data.get('#App:0001:pytest.request.ok!String') == 'false'
            assert (
                data.get('#App:0001:pytest.request.url!String')
                == 'https://httpbin.tci.ninja/status/500?one=1&two='
            )

    @staticmethod
    def test_advanced_request_get_exclude_null_params(playbook_app: Callable[..., MockApp]) -> None:
        """Test Advanced Request GET Exclude Null Parameters for TcEx App Playbook Advanced Request Module.

        This test case verifies that the advanced request feature correctly handles null parameter
        exclusion by testing the exclude_null_params functionality, ensuring that None values
        are properly filtered out from query parameters while preserving valid values.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            ij_data={
                'params': [
                    {
                        'label': 'HTTP Method',
                        'name': 'tc_adv_req_http_method',
                        'required': True,
                        'sequence': 99,
                        'type': 'Choice',
                        'validValues': ['DELETE', 'GET', 'POST', 'PUT'],
                    },
                ]
            },
            config_data={
                'tc_adv_req_exclude_null_params': True,
                'tc_adv_req_fail_on_error': False,
                'tc_adv_req_urlencode_body': False,
                'tc_adv_req_body': None,
                'tc_adv_req_headers': [{'key': 'pytest', 'value': 'pytest'}],
                'tc_adv_req_http_method': 'GET',
                'tc_adv_req_params': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': None}],
                'tc_adv_req_path': '/anything',
            },
        ).tcex

        se = tcex.session.external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = AdvancedRequest(
            model=tcex.inputs.model_advanced_request,
            playbook=tcex.app.playbook,
            session=se,
            output_prefix='pytest',
            timeout=60,
        )
        r = ar.request()
        if r is None:
            pytest.fail('Request should not be None.')
        data = r.json()

        assert r.request.url == data.get('url')
        assert r.status_code == HTTPStatus.OK
        # assert headers
        assert data.get('headers', {}).get('Pytest') == 'pytest'
        assert 'TcEx/5' in data.get('headers', {}).get('User-Agent')
        # assert params
        assert data.get('args', {}).get('one') == '1'
        assert data.get('args', {}).get('two') is None

    @staticmethod
    def test_advanced_request_post_str(playbook_app: Callable[..., MockApp]) -> None:
        """Test Advanced Request POST String Body for TcEx App Playbook Advanced Request Module.

        This test case verifies that the advanced request feature correctly handles POST requests
        with string body content by testing body configuration, header processing, parameter
        handling, and response validation for string-based request bodies.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            ij_data={
                'params': [
                    {
                        'label': 'HTTP Method',
                        'name': 'tc_adv_req_http_method',
                        'required': True,
                        'sequence': 99,
                        'type': 'Choice',
                        'validValues': ['DELETE', 'GET', 'POST', 'PUT'],
                    },
                ]
            },
            config_data={
                'tc_adv_req_exclude_null_params': False,
                'tc_adv_req_fail_on_error': False,
                'tc_adv_req_urlencode_body': False,
                'tc_adv_req_body': 'pytest',
                'tc_adv_req_headers': [{'key': 'pytest', 'value': 'pytest'}],
                'tc_adv_req_http_method': 'POST',
                'tc_adv_req_params': [{'key': 'one', 'value': '1'}],
                'tc_adv_req_path': '/anything',
            },
        ).tcex

        se = tcex.session.external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = AdvancedRequest(
            model=tcex.inputs.model_advanced_request,
            playbook=tcex.app.playbook,
            session=se,
            output_prefix='pytest',
            timeout=60,
        )
        r = ar.request()
        if r is None:
            pytest.fail('Request should not be None.')
        data = r.json()

        assert r.request.url == data.get('url')
        assert r.status_code == HTTPStatus.OK
        # assert data
        assert data.get('data') == tcex.inputs.model.tc_adv_req_body  # type: ignore
        # assert headers
        assert data.get('headers', {}).get('Pytest') == 'pytest'
        assert 'TcEx/5' in data.get('headers', {}).get('User-Agent')
        # assert params
        assert data.get('args', {}).get('one') == '1'

    @staticmethod
    def test_advanced_request_post_bytes(playbook_app: Callable[..., MockApp]) -> None:
        """Test Advanced Request POST Bytes Body for TcEx App Playbook Advanced Request Module.

        This test case verifies that the advanced request feature correctly handles POST requests
        with bytes body content by testing binary body configuration, header processing,
        parameter handling, and response validation for bytes-based request bodies.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            ij_data={
                'params': [
                    {
                        'label': 'HTTP Method',
                        'name': 'tc_adv_req_http_method',
                        'required': True,
                        'sequence': 99,
                        'type': 'Choice',
                        'validValues': ['DELETE', 'GET', 'POST', 'PUT'],
                    },
                ]
            },
            config_data={
                'tc_adv_req_exclude_null_params': False,
                'tc_adv_req_fail_on_error': False,
                'tc_adv_req_urlencode_body': False,
                'tc_adv_req_body': 'pytest',
                'tc_adv_req_headers': [{'key': 'pytest', 'value': 'pytest'}],
                'tc_adv_req_http_method': 'POST',
                'tc_adv_req_params': [{'key': 'one', 'value': '1'}],
                'tc_adv_req_path': '/anything',
            },
        ).tcex

        se = tcex.session.external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = AdvancedRequest(
            model=tcex.inputs.model_advanced_request,
            playbook=tcex.app.playbook,
            session=se,
            output_prefix='pytest',
            timeout=60,
        )
        r = ar.request()
        if r is None:
            pytest.fail('Request should not be None.')
        data = r.json()

        assert r.request.url == data.get('url')
        assert r.status_code == HTTPStatus.OK
        # assert data
        assert data.get('data') == tcex.inputs.model.tc_adv_req_body  # type: ignore
        # assert headers
        assert data.get('headers', {}).get('Pytest') == 'pytest'
        assert 'TcEx/5' in data.get('headers', {}).get('User-Agent')
        # assert params
        assert data.get('args', {}).get('one') == '1'

    @staticmethod
    def test_advanced_request_post_urlencode(playbook_app: Callable[..., MockApp]) -> None:
        """Test Advanced Request POST URL Encoded Body for TcEx App Playbook Advanced Request Module.

        This test case verifies that the advanced request feature correctly handles POST requests
        with URL encoded body content by testing form data processing, header configuration,
        parameter handling, and response validation for URL encoded request bodies.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            ij_data={
                'params': [
                    {
                        'label': 'HTTP Method',
                        'name': 'tc_adv_req_http_method',
                        'required': True,
                        'sequence': 99,
                        'type': 'Choice',
                        'validValues': ['DELETE', 'GET', 'POST', 'PUT'],
                    },
                ]
            },
            config_data={
                'tc_adv_req_exclude_null_params': False,
                'tc_adv_req_fail_on_error': False,
                'tc_adv_req_urlencode_body': True,
                'tc_adv_req_body': json.dumps({'one': '1', 'two': '2'}),
                'tc_adv_req_headers': [{'key': 'pytest', 'value': 'pytest'}],
                'tc_adv_req_http_method': 'POST',
                'tc_adv_req_params': [{'key': 'one', 'value': '1'}],
                'tc_adv_req_path': '/anything',
            },
        ).tcex

        se = tcex.session.external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = AdvancedRequest(
            model=tcex.inputs.model_advanced_request,
            playbook=tcex.app.playbook,
            session=se,
            output_prefix='pytest',
            timeout=60,
        )
        r = ar.request()
        if r is None:
            pytest.fail('Request should not be None.')
        data = r.json()

        assert r.request.url == data.get('url')
        assert r.status_code == HTTPStatus.OK
        # assert form
        assert data.get('form', {}).get('one') == '1'
        assert data.get('form', {}).get('two') == '2'
        # assert headers
        assert data.get('headers', {}).get('Pytest') == 'pytest'
        assert 'TcEx/5' in data.get('headers', {}).get('User-Agent')
        # assert params
        assert data.get('args', {}).get('one') == '1'
