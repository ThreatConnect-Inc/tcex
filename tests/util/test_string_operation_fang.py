"""TestStringOperationFang for string operation defang/refang functionality.

Test suite for the StringOperation utility class that handles defanging and refanging
of URLs, IPs, email addresses, and other indicators to make them inert or active.

Classes:
    TestStringOperationFang: Test suite for string operation defang/refang methods

TcEx Module Tested: tcex.util.string_operation
"""

import pytest

from tcex.util.string_operation import StringOperation


class TestStringOperationFang:
    """TestStringOperationFang for string operation defang/refang functionality.

    Test suite for the StringOperation utility class that handles defanging and refanging
    of URLs, IPs, email addresses, and other indicators to make them inert or active.

    Attributes:
        so: Instance of StringOperation class for testing
    """

    so = StringOperation()

    @pytest.mark.parametrize(
        'input_string,expected',
        [
            pytest.param(
                'http://example.com',
                'hxxp[:]//example[.]com',
                id='defang-http-url',
            ),
            pytest.param(
                'https://example.com',
                'hxxps[:]//example[.]com',
                id='defang-https-url',
            ),
            pytest.param(
                'ftp://files.example.com',
                'fxp[:]//files[.]example[.]com',
                id='defang-ftp-url',
            ),
            pytest.param(
                'http://user@example.com',
                'hxxp[:]//user[@]example[.]com',
                id='defang-url-with-user',
            ),
            pytest.param(
                'https://example.com:8443/path',
                'hxxps[:]//example[.]com[:]8443/path',
                id='defang-url-with-port',
            ),
            pytest.param(
                '192.168.1.1',
                '192[.]168[.]1[.]1',
                id='defang-ipv4',
            ),
            pytest.param(
                '10.0.0.1:8080',
                '10[.]0[.]0[.]1[:]8080',
                id='defang-ipv4-with-port',
            ),
            pytest.param(
                'example.com',
                'example[.]com',
                id='defang-domain',
            ),
            pytest.param(
                'subdomain.example.com',
                'subdomain[.]example[.]com',
                id='defang-subdomain',
            ),
            pytest.param(
                'user@example.com',
                'user[@]example[.]com',
                id='defang-email',
            ),
            pytest.param(
                'http://192.168.1.1/path',
                'hxxp[:]//192[.]168[.]1[.]1/path',
                id='defang-url-with-ip',
            ),
            pytest.param(
                'https://user:pass@example.com:443',
                'hxxps[:]//user[:]pass[@]example[.]com[:]443',
                id='defang-url-full',
            ),
            pytest.param(
                'Visit http://example.com for more info',
                'Visit hxxp[:]//example[.]com for more info',
                id='defang-url-in-text',
            ),
            pytest.param(
                'Contact admin@example.com or http://support.example.com',
                'Contact admin[@]example[.]com or hxxp[:]//support[.]example[.]com',
                id='defang-multiple-indicators',
            ),
            pytest.param(
                'no special chars here',
                'no special chars here',
                id='defang-plain-text',
            ),
            pytest.param(
                '',
                '',
                id='defang-empty-string',
            ),
        ],
    )
    def test_string_operation_defang(self, input_string: str, expected: str):
        """Test defang operation on various IOCs.

        Test case for the defang method that converts active indicators (URLs, IPs,
        emails, domains) to defanged versions to make them inert and safe to handle.

        Parameters:
            input_string: Active indicator string to defang
            expected: Expected defanged result
        """
        result = self.so.defang(input_string)
        assert result == expected, f'Input {input_string} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'input_string,expected',
        [
            pytest.param(
                'hxxp[:]//example[.]com',
                'http://example.com',
                id='refang-http-url',
            ),
            pytest.param(
                'hxxps[:]//example[.]com',
                'https://example.com',
                id='refang-https-url',
            ),
            pytest.param(
                'fxp[:]//files[.]example[.]com',
                'ftp://files.example.com',
                id='refang-ftp-url',
            ),
            pytest.param(
                'hxxp[:]//user[@]example[.]com',
                'http://user@example.com',
                id='refang-url-with-user',
            ),
            pytest.param(
                'hxxps[:]//example[.]com[:]8443/path',
                'https://example.com:8443/path',
                id='refang-url-with-port',
            ),
            pytest.param(
                '192[.]168[.]1[.]1',
                '192.168.1.1',
                id='refang-ipv4',
            ),
            pytest.param(
                '10[.]0[.]0[.]1[:]8080',
                '10.0.0.1:8080',
                id='refang-ipv4-with-port',
            ),
            pytest.param(
                'example[.]com',
                'example.com',
                id='refang-domain',
            ),
            pytest.param(
                'subdomain[.]example[.]com',
                'subdomain.example.com',
                id='refang-subdomain',
            ),
            pytest.param(
                'user[@]example[.]com',
                'user@example.com',
                id='refang-email',
            ),
            pytest.param(
                'hxxp[:]//192[.]168[.]1[.]1/path',
                'http://192.168.1.1/path',
                id='refang-url-with-ip',
            ),
            pytest.param(
                'hxxps[:]//user[:]pass[@]example[.]com[:]443',
                'https://user:pass@example.com:443',
                id='refang-url-full',
            ),
            pytest.param(
                'Visit hxxp[:]//example[.]com for more info',
                'Visit http://example.com for more info',
                id='refang-url-in-text',
            ),
            pytest.param(
                'Contact admin[@]example[.]com or hxxp[:]//support[.]example[.]com',
                'Contact admin@example.com or http://support.example.com',
                id='refang-multiple-indicators',
            ),
            pytest.param(
                'no special chars here',
                'no special chars here',
                id='refang-plain-text',
            ),
            pytest.param(
                '',
                '',
                id='refang-empty-string',
            ),
        ],
    )
    def test_string_operation_refang(self, input_string: str, expected: str):
        """Test refang operation on various defanged IOCs.

        Test case for the refang method that converts defanged indicators back to
        active versions.

        Parameters:
            input_string: Defanged indicator string to refang
            expected: Expected refanged result
        """
        result = self.so.refang(input_string)
        assert result == expected, f'Input {input_string} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'original',
        [
            pytest.param('http://example.com', id='roundtrip-http-url'),
            pytest.param('https://example.com:8443/path', id='roundtrip-https-url-port'),
            pytest.param('ftp://files.example.com', id='roundtrip-ftp-url'),
            pytest.param('192.168.1.1', id='roundtrip-ipv4'),
            pytest.param('user@example.com', id='roundtrip-email'),
            pytest.param('http://user:pass@example.com:443', id='roundtrip-url-full'),
            pytest.param(
                'Contact admin@example.com or http://support.example.com',
                id='roundtrip-multiple',
            ),
        ],
    )
    def test_string_operation_roundtrip(self, original: str):
        """Test roundtrip defang/refang operation.

        Test case that verifies defanging and then refanging a string returns the
        original value.

        Parameters:
            original: Original indicator string
        """
        defanged = self.so.defang(original)
        refanged = self.so.refang(defanged)
        assert refanged == original, f'Roundtrip failed: {original} -> {defanged} -> {refanged}'

    @pytest.mark.parametrize(
        'input_string,expected_after_double_defang',
        [
            pytest.param(
                'http://example.com',
                'hxxp[[:]]//example[[.]]com',
                id='double-defang-http',
            ),
            pytest.param(
                'user@example.com',
                'user[[@]]example[[.]]com',
                id='double-defang-email',
            ),
            pytest.param(
                '192.168.1.1',
                '192[[.]]168[[.]]1[[.]]1',
                id='double-defang-ip',
            ),
        ],
    )
    def test_string_operation_double_defang(
        self, input_string: str, expected_after_double_defang: str
    ):
        """Test that defanging twice produces nested brackets.

        Test case that verifies defanging is NOT idempotent - defanging an already
        defanged string produces nested brackets (e.g., [.] becomes [[.]]). This
        demonstrates the simple string replacement behavior.

        Parameters:
            input_string: Original indicator string
            expected_after_double_defang: Expected result after defanging twice
        """
        first_defang = self.so.defang(input_string)
        second_defang = self.so.defang(first_defang)
        assert second_defang == expected_after_double_defang, (
            f'Double defang unexpected: {input_string} -> {first_defang} '
            f'-> {second_defang} != {expected_after_double_defang}'
        )
