"""TcEx Framework Module"""

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestGroupAttributeSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('group_attributes')

    # TODO [PLAT-4144] - next url is invalid
    # def test_group_attributes_get_all(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     for group_attribute in self.tcex.api.tc.v3.group_attributes():
    #         print(group_attribute.model.dict(exclude_none=True))
    #     # End Snippet

    def test_group_attributes_tql_filter(self):
        """Test snippet"""
        group = self.v3_helper.create_group(
            attributes=[
                {
                    'default': True,
                    'type': 'Description',
                    'value': 'An example description attribute',
                }
            ],
        )
        # get attribute id
        assert group.model.attributes.data is not None, 'No attributes found.'
        attribute_id = group.model.attributes.data[0].id
        assert attribute_id is not None, 'No attribute id found.'
        assert group.model.id is not None, 'No group id found.'
        group_id = group.model.id

        # Begin Snippet
        group_attributes = self.tcex.api.tc.v3.group_attributes()
        group_attributes.filter.date_added(TqlOperator.GT, '1 day ago')
        group_attributes.filter.displayed(TqlOperator.EQ, True)
        group_attributes.filter.id(TqlOperator.EQ, attribute_id)
        group_attributes.filter.group_id(TqlOperator.EQ, group_id)
        group_attributes.filter.last_modified(TqlOperator.GT, '1 day ago')
        group_attributes.filter.type_name(TqlOperator.EQ, 'Description')
        for group_attribute in group_attributes:
            print(group_attribute.model.dict(exclude_none=True))
        # End Snippet

    def test_group_attribute_get_by_id(self):
        """Test snippet"""
        group = self.v3_helper.create_group(
            attributes=[
                {
                    'default': True,
                    'type': 'Description',
                    'value': 'An example description attribute',
                }
            ],
        )
        # get attribute id
        assert group.model.attributes.data is not None, 'No attributes found.'
        attribute_id = group.model.attributes.data[0].id

        # Begin Snippet
        group_attribute = self.tcex.api.tc.v3.group_attribute(id=attribute_id)
        group_attribute.get()
        # End Snippet
