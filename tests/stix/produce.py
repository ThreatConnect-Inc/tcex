# standard library
import inspect
import json

# first-party
from tcex.stix.model import StixModel


class TestStixProducer:
    model = StixModel()
    file_root = 'tests/stix/tc_files'

    def test_indicators(self):
        file_name = (
            f'{self.file_root}/{inspect.currentframe().f_code.co_name.replace("test_", "")}.json'
        )

        with open(file_name) as f:
            data = json.load(f)

        for stix_data in self.model.produce(data):
            print(stix_data)

    def test_addresses(self):
        file_name = (
            f'{self.file_root}/{inspect.currentframe().f_code.co_name.replace("test_", "")}.json'
        )

        with open(file_name) as f:
            data = json.load(f)

        for stix_data in self.model.produce(data):
            print(stix_data)

    def test_files(self):
        file_name = (
            f'{self.file_root}/{inspect.currentframe().f_code.co_name.replace("test_", "")}.json'
        )

        with open(file_name) as f:
            data = json.load(f)

        for stix_data in self.model.produce(data):
            print(stix_data)

    def test_registry_keys(self):
        file_name = (
            f'{self.file_root}/{inspect.currentframe().f_code.co_name.replace("test_", "")}.json'
        )

        with open(file_name) as f:
            data = json.load(f)

        stix_data = self.model.produce(data)
        assert len(stix_data) == 1
