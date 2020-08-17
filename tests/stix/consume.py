from tcex.stix.model import StixModel
import json
import inspect


class TestStixConsumer:
    model = StixModel()
    file_root = 'tests/stix/stix_files'

    def test_domain_objects_bundle(self):
        file_name = f'{self.file_root}/{inspect.currentframe().f_code.co_name.replace("test_", "")}.json'
        
        with open(file_name) as f:
            data = json.load(f)

        for tc_data in self.model.consume(data):
            print(tc_data)

    def test_indicator_bundle(self):
        file_name = f'{self.file_root}/{inspect.currentframe().f_code.co_name.replace("test_", "")}.json'

        with open(file_name) as f:
            data = json.load(f)

        for tc_data in self.model.consume(data):
            print(tc_data)

    def test_ipv4_bundle(self):
        file_name = f'{self.file_root}/{inspect.currentframe().f_code.co_name.replace("test_", "")}.json'

        with open(file_name) as f:
            data = json.load(f)

        for tc_data in self.model.consume(data):
            print(tc_data)

