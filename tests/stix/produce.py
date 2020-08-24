"""Test producing STIX data."""
# standard library
import json

# third-party
import deepdiff
import pytest

# first-party
from tcex.stix.model import StixModel


class TestStixProducer:
    """Test producing STIX data."""

    model = StixModel()
    file_root = 'tests/stix/tc_files'

    @pytest.mark.parametrize(
        'in_file_path, out_file_path',
        [
            (
                './tests/stix/tc_files/addresses.json',
                './tests/stix/tc_files/addresses_produced.json',
            ),
            ('./tests/stix/tc_files/files.json', './tests/stix/tc_files/files_produced.json',),
            (
                './tests/stix/tc_files/indicators.json',
                './tests/stix/tc_files/indicators_produced.json',
            ),
            (
                './tests/stix/tc_files/registry_key.json',
                './tests/stix/tc_files/registry_key_produced.json',
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

        stix_data = sorted(
            list(json.loads(str(s)) for s in self.model.produce(data)), key=lambda x: x.get('name')
        )

        with open(out_file_path, 'w') as f:
            expected_data = sorted(json.load(f), key=lambda x: x.get('name'))
        ddiff = deepdiff.DeepDiff(
            stix_data,
            expected_data,
            ignore_order=True,
            exclude_paths=['id', 'valid_from', 'created', 'modified'],
            exclude_regex_paths='.*',
        )

        assert not ddiff, str(ddiff)
