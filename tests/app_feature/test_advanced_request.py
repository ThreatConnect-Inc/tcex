# -*- coding: utf-8 -*-
"""Test the TcEx App Feature Advance Request Module."""


# standard library
import json


class TestAdvancedRequest:
    """Test the TcEx App Feature Advance Request Module."""

    # properties
    tc_playbook_out_variables = None

    @staticmethod
    def _load_data(tcex: object, context: str):
        """Load data from Redis into a dict.

        Args:
            tcex (object): The TcEx object.
            context (str): The KV store context.
        """
        data = {}
        for k, v in tcex.redis_client.hgetall(context).items():
            if k.decode() == '#App:0001:pytest.request.headers!String':
                data[k.decode()] = json.loads(json.loads(v.decode()))
            else:
                data[k.decode()] = json.loads(v.decode())
        return data

    def setup_class(self):
        """Configure setup before all tests."""
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
    def test_advanced_request_get_standard(playbook_app: callable):
        """Test advanced request feature

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={
                'tc_adv_req_exclude_null_params': False,
                'tc_adv_req_fail_on_error': False,
                'tc_adv_req_urlencode_body': False,
                'tc_adv_req_body': None,
                'tc_adv_req_headers': {'key': 'pytest', 'value': 'pytest'},
                'tc_adv_req_http_method': 'GET',
                'tc_adv_req_params': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': ''}],
                'tc_adv_req_path': '/anything',
            }
        ).tcex

        se = tcex.session_external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = tcex.advanced_request(session=se, timeout=60)

        r = ar.request()
        data = r.json()

        assert r.request.url == data.get('url')
        assert r.status_code == 200
        # assert headers
        assert data.get('headers', {}).get('Pytest') == 'pytest'
        assert data.get('headers', {}).get('User-Agent') == 'TcEx App: Pytest - 1.0.0'
        # assert params
        assert data.get('args', {}).get('one') == '1'
        assert data.get('args', {}).get('two') == ''

    def test_advanced_request_get_500(self, playbook_app: callable):
        """Test advanced request feature

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={
                'tc_playbook_out_variables': self.tc_playbook_out_variables,
                'tc_adv_req_exclude_null_params': False,
                'tc_adv_req_fail_on_error': True,
                'tc_adv_req_urlencode_body': False,
                'tc_adv_req_body': None,
                'tc_adv_req_headers': {'key': 'pytest', 'value': 'pytest'},
                'tc_adv_req_http_method': 'GET',
                'tc_adv_req_params': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': ''}],
                'tc_adv_req_path': '/status/500',
            }
        ).tcex

        se = tcex.session_external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = tcex.advanced_request(session=se, timeout=60)

        try:
            ar.request()
        except RuntimeError:
            pass

        try:
            # the write_output method is called in exit method
            tcex.playbook.exit(1)
        except SystemExit:
            pass

        # load output data from KV store to validate
        data = self._load_data(tcex, tcex.args.tc_playbook_db_context)

        assert data.get('#App:0001:pytest.request.reason!String') == 'INTERNAL SERVER ERROR'
        assert data.get('#App:0001:pytest.request.content!String') == ''
        assert data.get('#App:0001:pytest.request.headers!String').get('Server') == 'nginx'
        assert data.get('#App:0001:pytest.request.status_code!String') == '500'
        assert data.get('#App:0001:pytest.request.content.binary!Binary') == ''
        assert data.get('#App:0001:pytest.request.ok!String') == 'false'
        assert (
            data.get('#App:0001:pytest.request.url!String')
            == 'https://httpbin.tci.ninja/status/500?one=1&two='
        )

    @staticmethod
    def test_advanced_request_get_exclude_null_params(playbook_app: callable):
        """Test advanced request feature

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={
                'tc_adv_req_exclude_null_params': True,
                'tc_adv_req_fail_on_error': False,
                'tc_adv_req_urlencode_body': False,
                'tc_adv_req_body': None,
                'tc_adv_req_headers': {'key': 'pytest', 'value': 'pytest'},
                'tc_adv_req_http_method': 'GET',
                'tc_adv_req_params': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': None}],
                'tc_adv_req_path': '/anything',
            }
        ).tcex

        se = tcex.session_external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = tcex.advanced_request(session=se, timeout=60)

        r = ar.request()
        data = r.json()

        assert r.request.url == data.get('url')
        assert r.status_code == 200
        # assert headers
        assert data.get('headers', {}).get('Pytest') == 'pytest'
        assert data.get('headers', {}).get('User-Agent') == 'TcEx App: Pytest - 1.0.0'
        # assert params
        assert data.get('args', {}).get('one') == '1'
        assert data.get('args', {}).get('two') is None

    @staticmethod
    def test_advanced_request_post_str(playbook_app: callable):
        """Test advanced request feature

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={
                'tc_adv_req_exclude_null_params': False,
                'tc_adv_req_fail_on_error': False,
                'tc_adv_req_urlencode_body': False,
                'tc_adv_req_body': 'pytest',
                'tc_adv_req_headers': {'key': 'pytest', 'value': 'pytest'},
                'tc_adv_req_http_method': 'POST',
                'tc_adv_req_params': {'key': 'one', 'value': '1'},
                'tc_adv_req_path': '/anything',
            }
        ).tcex

        se = tcex.session_external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = tcex.advanced_request(session=se, timeout=60)

        r = ar.request()
        data = r.json()

        assert r.request.url == data.get('url')
        assert r.status_code == 200
        # assert data
        assert data.get('data') == tcex.args.tc_adv_req_body
        # assert headers
        assert data.get('headers', {}).get('Pytest') == 'pytest'
        assert data.get('headers', {}).get('User-Agent') == 'TcEx App: Pytest - 1.0.0'
        # assert params
        assert data.get('args', {}).get('one') == '1'

    @staticmethod
    def test_advanced_request_post_bytes(playbook_app: callable):
        """Test advanced request feature

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={
                'tc_adv_req_exclude_null_params': False,
                'tc_adv_req_fail_on_error': False,
                'tc_adv_req_urlencode_body': False,
                'tc_adv_req_body': b'pytest',
                'tc_adv_req_headers': {'key': 'pytest', 'value': 'pytest'},
                'tc_adv_req_http_method': 'POST',
                'tc_adv_req_params': {'key': 'one', 'value': '1'},
                'tc_adv_req_path': '/anything',
            }
        ).tcex

        se = tcex.session_external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = tcex.advanced_request(session=se, timeout=60)

        r = ar.request()
        data = r.json()

        assert r.request.url == data.get('url')
        assert r.status_code == 200
        # assert data
        assert data.get('data') == tcex.args.tc_adv_req_body.decode()
        # assert headers
        assert data.get('headers', {}).get('Pytest') == 'pytest'
        assert data.get('headers', {}).get('User-Agent') == 'TcEx App: Pytest - 1.0.0'
        # assert params
        assert data.get('args', {}).get('one') == '1'

    @staticmethod
    def test_advanced_request_post_urlencode(playbook_app: callable):
        """Test advanced request feature

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={
                'tc_adv_req_exclude_null_params': False,
                'tc_adv_req_fail_on_error': False,
                'tc_adv_req_urlencode_body': True,
                'tc_adv_req_body': json.dumps({'one': '1', 'two': '2'}),
                'tc_adv_req_headers': {'key': 'pytest', 'value': 'pytest'},
                'tc_adv_req_http_method': 'POST',
                'tc_adv_req_params': {'key': 'one', 'value': '1'},
                'tc_adv_req_path': '/anything',
            }
        ).tcex

        se = tcex.session_external
        se.base_url = 'https://httpbin.tci.ninja'
        se.verify = False

        ar = tcex.advanced_request(session=se, timeout=60)

        r = ar.request()
        data = r.json()

        assert r.request.url == data.get('url')
        assert r.status_code == 200
        # assert form
        assert data.get('form', {}).get('one') == '1'
        assert data.get('form', {}).get('two') == '2'
        # assert headers
        assert data.get('headers', {}).get('Pytest') == 'pytest'
        assert data.get('headers', {}).get('User-Agent') == 'TcEx App: Pytest - 1.0.0'
        # assert params
        assert data.get('args', {}).get('one') == '1'
