"""Test Consuming STIX data."""
# standard library
import json

# third-party
import deepdiff
import pytest

# first-party
from tcex.stix.model import StixModel


# pylint: disable=no-self-use
class TestStixConsumer:
    """Test Consuming STIX data."""

    @pytest.mark.parametrize(
        'in_file_path, out_file_path',
        [
            # (
            #     './tests/stix/stix_files/indicator_bundle.json',
            #     './tests/stix/stix_files/indicator_bundle_consumed.json',
            # ),
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
    def test_bundles(self, in_file_path, out_file_path, tcex):
        """Parse stix json files and compare the output to known data.

        Args:
            in_file_path: path to a file with stix json in it.
            out_file_path: path to a file with the expected output from parsing.
            tcex: tcex module.
        """
        model = StixModel(tcex.logger)

        with open(in_file_path) as f:
            data = json.load(f)

        tc_data = list(model.consume(data))

        with open(out_file_path) as f:
            expected_data = json.load(f)
        ddiff = deepdiff.DeepDiff(tc_data, expected_data, ignore_order=True)
        assert not ddiff, str(ddiff)


    def test_custom(self, tcex):
        data = {'objects': [
            {'id': 'indicator--3e6d191d-4189-41e3-865f-7fce4c9b3fcc',
             'pattern': "[domain-name:value = 'scontent-ber1-1.xx.fbcdn.net']", 'lang': 'en',
             'type': 'indicator', 'created': '2020-08-21T12:19:04.751Z', 'modified': '2020-08-21T12:19:04.751Z',
             'revoked': True, 'name': 'FP - scontent-ber1-1.xx.fbcdn.net',
             'description': 'FP from Alert ID: 41785a42.', 'valid_from': '2020-08-21T12:18:20Z',
             'pattern_type': 'stix', 'pattern_version': '2.1', 'indicator_types': ['Domain Watchlist'],
             'spec_version': '2.1', 'confidence': '20'}
        ]}
        model = StixModel(tcex)
        tc_data = list(model.consume(data, 'TCI', 'Collection_ID', 'Collection_Path', custom_type_mapping={'new_type': self.custom_mapping}))
        print(tc_data)

    def custom_mapping(self, stix_data):
        return {
            'key': 'my_custom_value'
        }

