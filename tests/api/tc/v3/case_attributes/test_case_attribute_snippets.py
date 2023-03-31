"""TcEx Framework Module"""
# third-party
import pytest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestCaseAttributeSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('case_attributes')

    # TODO [PLAT-4144] - next url is invalid
    # def test_case_attributes_get_all(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     for case_attribute in self.tcex.api.tc.v3.case_attributes():
    #         print(case_attribute.model.dict(exclude_none=True))
    #     # End Snippet

    def test_case_attributes_tql_filter(self):
        """Test snippet"""
        case = self.v3_helper.create_case(
            attributes=[
                {
                    'default': True,
                    'type': 'Description',
                    'value': 'An example description attribute',
                }
            ],
            params={'fields': 'attributes'},
        )
        if not case.model.id or not case.model.attributes.data:
            pytest.fail('Case attribute not created.')

        # get attribute id
        attribute_id = case.model.attributes.data[0].id
        if attribute_id is None:
            pytest.fail('Case attribute id not found.')

        # Begin Snippet
        case_attributes = self.tcex.api.tc.v3.case_attributes()
        case_attributes.filter.date_added(TqlOperator.GT, '1 day ago')
        case_attributes.filter.id(TqlOperator.EQ, attribute_id)
        case_attributes.filter.case_id(TqlOperator.EQ, case.model.id)
        case_attributes.filter.last_modified(TqlOperator.GT, '1 day ago')
        case_attributes.filter.type_name(TqlOperator.EQ, 'Description')
        for case_attribute in case_attributes:
            print(case_attribute.model.dict(exclude_none=True))
        # End Snippet

    def test_case_attribute_get_by_id(self):
        """Test snippet"""
        case = self.v3_helper.create_case(
            attributes=[
                {
                    'default': True,
                    'type': 'Description',
                    'value': 'An example description attribute',
                }
            ],
            params={'fields': 'attributes'},
        )
        if not case.model.id or not case.model.attributes.data:
            pytest.fail('Case attribute not created.')

        # get attribute id
        attribute_id = case.model.attributes.data[0].id

        # Begin Snippet
        case_attribute = self.tcex.api.tc.v3.case_attribute(id=attribute_id)
        case_attribute.get()
        print(case_attribute.model.dict(exclude_none=True))
        # End Snippet
