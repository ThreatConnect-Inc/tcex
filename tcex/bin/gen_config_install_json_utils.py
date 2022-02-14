"""."""
# standard library
from typing import List

# first-party
from tcex.bin.bin_abc import BinABC


class GenConfigInstallJsonUtils(BinABC):
    """Generate App Config File"""

    # def __init__(self) -> None:
    #     """Initialize class properties."""
    #     super().__init__()

    @property
    def default_inputs(self) -> List[dict]:
        """Return default inputs with disabled=True."""
        return [
            # add to advanced
            {
                'label': 'Fail on No Results',
                'default': True,
                'type': 'Boolean',
                'note': 'If an action would return an empty result, exit with a failure.',
                'section': 'Advanced',
                'actions': [],
                'disabled': True,
            },
            {
                'label': 'Fail on False',
                'default': True,
                'type': 'Boolean',
                'note': 'Fail if any output value would be False or Null',
                'section': 'Advanced',
                'actions': [],
                'disabled': True,
            },
            {
                'label': 'Exit on Failed Operation',
                'name': 'fail_on_error',
                'default': True,
                'type': 'Boolean',
                'note': (
                    'For actions with more than one operation, the App will exit via '
                    'the fail path if any one of the operations fails.'
                ),
                'section': 'Advanced',
                'actions': [],
                'disabled': True,
            },
            # add to connection
            {
                'label': 'Verify SSL Cert',
                'default': True,
                'type': 'Boolean',
                'note': 'Verify the SSL Certificate of the API host during connection.',
                'section': 'Connection',
                'actions': [],
                'disabled': True,
            },
        ]

    @property
    def advanced_request_inputs(self) -> List[dict]:
        """Return advanced request inputs."""
        return [
            {
                'label': 'API Endpoint/Path',
                'name': 'tc_adv_req_path',
                'note': 'The API Path request.',
                'required': True,
                'section': 'Configure',
                'actions': ['Advanced Request'],
            },
            {
                'default': 'GET',
                'label': 'HTTP Method',
                'name': 'tc_adv_req_http_method',
                'note': 'HTTP method to use.',
                'required': True,
                'section': 'Configure',
                'type': 'Choice',
                'validValues': [
                    'GET',
                    'POST',
                    'DELETE',
                    'PUT',
                    'HEAD',
                    'PATCH',
                    'OPTIONS',
                ],
                'actions': ['Advanced Request'],
            },
            {
                'label': 'Query Parameters',
                'name': 'tc_adv_req_params',
                'section': 'Configure',
                'note': (
                    'Query parameters to append to the URL. For sensitive information like API '
                    'keys, using variables is recommended to ensure that the Playbook '
                    'will not export sensitive data.'
                ),
                'playbookDataType': ['String', 'StringArray'],
                'required': False,
                'type': 'KeyValueList',
                'validValues': ['${KEYCHAIN}', '${TEXT}'],
                'actions': ['Advanced Request'],
            },
            {
                'label': 'Exclude Empty/Null Parameters',
                'name': 'tc_adv_req_exclude_null_params',
                'note': (
                    '''Some API endpoint don't handle null/empty query parameters '''
                    '''properly (e.g., ?'name': &'type': String). If selected this options '''
                    '''will exclude any query parameters that has a null/empty value.'''
                ),
                'type': 'Boolean',
                'section': 'Configure',
                'actions': ['Advanced Request'],
            },
            {
                'label': 'Headers',
                'name': 'tc_adv_req_headers',
                'note': (
                    'Headers to include in the request. When using Multi-part Form/File data, '
                    'do **not** add a **Content-Type** header. For sensitive '
                    'information like API '
                    'keys, using variables is recommended to ensure that the '
                    'Playbook will not export sensitive data.'
                ),
                'required': False,
                'type': 'KeyValueList',
                'section': 'Configure',
                'validValues': ['${KEYCHAIN}', '${TEXT}'],
                'actions': ['Advanced Request'],
            },
            {
                'display': (
                    "tc_action in ('Advanced Request') AND "
                    "tc_adv_req_http_method in ('POST', 'PUT', 'DELETE', 'PATCH')"
                ),
                'label': 'Body',
                'name': 'tc_adv_req_body',
                'note': 'Content of the HTTP request.',
                'playbookDataType': ['String', 'Binary'],
                'section': 'Configure',
                'required': False,
                'validValues': ['${KEYCHAIN}', '${TEXT}'],
                'viewRows': 4,
                'actions': ['Advanced Request'],
            },
            {
                'display': (
                    "tc_action in ('Advanced Request') AND "
                    "tc_adv_req_http_method in ('POST', 'PUT', 'DELETE', 'PATCH')"
                ),
                'label': 'URL Encode JSON Body',
                'name': 'tc_adv_req_urlencode_body',
                'section': 'Configure',
                'note': (
                    'URL encode a JSON-formatted body. Typically used for '
                    "'x-www-form-urlencoded' "
                    'data, where the data can be configured in the body as a JSON string.'
                ),
                'type': 'Boolean',
                'actions': ['Advanced Request'],
            },
            {
                'default': True,
                'label': 'Fail for Status',
                'name': 'tc_adv_req_fail_on_error',
                'section': 'Configure',
                'note': 'Fail if the response status code is 4XX - 5XX.',
                'type': 'Boolean',
                'actions': ['Advanced Request'],
            },
        ]

        # AR_OUTPUTS = [
        #     {'name': 'request.content', 'type': 'String'},
        #     {'name': 'request.content.binary', 'type': 'Binary'},
        #     {'name': 'request.headers', 'type': 'String'},
        #     {'name': 'request.ok', 'type': 'String'},
        #     {'name': 'request.reason', 'type': 'String'},
        #     {'name': 'request.status_code', 'type': 'String'},
        #     {'name': 'request.url', 'type': 'String'},
        #     # {'name': 'result.json.raw', 'type': 'String'},
        # ]
