"""TestStringOperationInflect for string operation inflection functionality.

Test suite for the StringOperation utility class that handles string inflection
operations including pluralization of various threat intelligence entity types.

Classes:
    TestStringOperationInflect: Test suite for string operation inflection methods

TcEx Module Tested: tcex.util.string_operation
"""


import pytest


from tcex.util.string_operation import StringOperation


class TestStringOperationInflect:
    """TestStringOperationInflect for string operation inflection functionality.

    Test suite for the StringOperation utility class that handles string inflection
    operations including pluralization of various threat intelligence entity types.

    Attributes:
        so: Instance of StringOperation class for testing
    """

    so = StringOperation()

    @pytest.mark.parametrize(
        'string,expected',
        [
            pytest.param('adversary', 'adversaries', id='pass-adversary'),
            pytest.param('Campaign', 'Campaigns', id='pass-campaign'),
            pytest.param('Document', 'Documents', id='pass-document'),
            pytest.param('Email', 'Emails', id='pass-email'),
            pytest.param('Event', 'Events', id='pass-event'),
            pytest.param('Incident', 'Incidents', id='pass-incident'),
            pytest.param('Intrusion Set', 'Intrusion Sets', id='pass-intrusion-set'),
            pytest.param('Report', 'Reports', id='pass-report'),
            pytest.param('Signature', 'Signatures', id='pass-signature'),
            pytest.param('Task', 'Tasks', id='pass-task'),
            pytest.param('Threat', 'Threats', id='pass-threat'),
        ],
    )
    def test_utils_inflect(self, string: str, expected: str):
        """Test string inflection pluralization functionality.

        Test case for the inflection.pluralize method that converts singular
        threat intelligence entity names to their plural forms.
        """
        result = self.so.inflection.pluralize(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'
