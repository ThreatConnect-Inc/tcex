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
    def test_indicator_bundle(self, in_file_path, out_file_path, tcex):
        """Parse stix json files and compare the output to known data.

        Args:
            in_file_path: path to a file with stix json in it.
            out_file_path: path to a file with the expected output from parsing.
            tcex: tcex module.
        """
        model = StixModel(tcex.logger)
        with open(in_file_path) as f:
            data = json.load(f)

        stix_data = list(model.produce(data))

        with open(out_file_path) as f:
            expected_data = json.load(f)

        for produced_data in stix_data:
            self._compare_helper(produced_data, expected_data)

    @staticmethod
    def _compare_helper(produced_data, expected_data):
        for compare_to_data in expected_data:
            if compare_to_data.get('name') == produced_data.get('name'):
                ddiff = deepdiff.DeepDiff(
                    compare_to_data,
                    produced_data,
                    ignore_order=True,
                    exclude_paths=[
                        "root['id']",
                        "root['valid_from']",
                        "root['created']",
                        "root['modified']",
                    ],
                )
                assert not ddiff, str(ddiff)
                return

        ddiff = deepdiff.DeepDiff(None, produced_data)
        assert not ddiff, str(ddiff)
