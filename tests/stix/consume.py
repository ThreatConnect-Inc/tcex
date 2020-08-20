"""Test Consuming STIX data."""
# standard library
import json

# third-party
import deepdiff
import pytest

# first-party
from tcex.stix.model import StixModel


class TestStixConsumer:
    """Test Consuming STIX data."""
    model = StixModel()

    @pytest.mark.parametrize(
        'in_file_path, out_file_path',
        [
            (
                './tests/stix/stix_files/indicator_bundle.json',
                './tests/stix/stix_files/indicator_bundle_consumed.json',
            ),
            (
                './tests/stix/stix_files/domain_objects_bundle.json',
                './tests/stix/stix_files/domain_objects_bundle_consumed.json',
            ),
            (
                './tests/stix/stix_files/ipv4_bundle.json',
                './tests/stix/stix_files/ipv4_bundle_consumed.json',
            ),
        ],
    )
    def test_indicator_bundle(self, in_file_path, out_file_path):
        """Parse stix json files and compare the output to known data.

        Args:
            in_file_path: path to a file with stix json in it.
            out_file_path: path to a file with the expected output from parsing.
        """
        with open(in_file_path) as f:
            data = json.load(f)

        tc_data = list(self.model.consume(data))

        with open(out_file_path) as f:
            expected_data = json.load(f)
        ddiff = deepdiff.DeepDiff(tc_data, expected_data, ignore_order=True)
        assert not ddiff, str(ddiff)

    def test_indicator(self):
        indicator = {
            'pattern': "[ipv4-addr:value IN ('1.2.3.4/15', '1.23.4.5', '192.168.1.2/12')]",
            'name': 'foobar',
            'id': 'foobar-id'
        }

        from tcex.stix.indicator.indicator import StixIndicator
        si = StixIndicator()
        indicators = list(si.consume(indicator))
        print(indicators)


