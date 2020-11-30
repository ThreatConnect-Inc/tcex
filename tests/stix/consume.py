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

        tc_data = list(model.consume(data, 'collection_id', 'collection_name', 'collection_path'))

        with open(out_file_path) as f:
            expected_data = json.load(f)
        ddiff = deepdiff.DeepDiff(tc_data, expected_data, ignore_order=True)
        assert not ddiff, str(ddiff)
