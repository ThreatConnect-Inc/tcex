"""Test the TcEx API Snippets."""
# third-party
# import pytest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestIndicatorSnippets(TestV3):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self, method: callable):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('indicators')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

        # remove an previous indicators with the next test case name as a tag
        indicators = self.v3.indicators()
        indicators.filter.tag(TqlOperator.EQ, method.__name__)
        for indicator in indicators:
            indicator.delete()

    #
    # Create Indicators
    #

    def test_address_create(self):
        """Test snippet"""
        # Begin Snippet
        indicator = self.tcex.v3.indicator(
            confidence=74,
            ip='111.111.111.100',
            rating=4,
            type='Address',
        )

        indicator.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        indicator.delete()

    def test_address_stage_group_associations(self):
        """Test snippet"""
        # Begin Snippet
        indicator = self.tcex.v3.indicator(
            confidence=74,
            ip='111.111.111.102',
            rating=4,
            type='Address',
        )

        # Add association
        association = self.tcex.v3.group(name='MyGroup', type='Adversary')
        indicator.stage_associated_group(association)

        indicator.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        indicator.delete()

    def test_address_stage_attribute(self):
        """Test snippet"""
        # Begin Snippet
        indicator = self.tcex.v3.indicator(
            confidence=74,
            ip='111.111.111.104',
            rating=4,
            type='Address',
        )

        # Add attribute
        attribute = self.tcex.v3.indicator_attribute(
            value='An example description attribute.',
            type='Description',
        )
        indicator.stage_attribute(attribute)

        indicator.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        indicator.delete()

    def test_address_stage_security_label(self):
        """Test snippet"""
        # Begin Snippet
        indicator = self.tcex.v3.indicator(
            confidence=74,
            ip='111.111.111.106',
            rating=4,
            type='Address',
        )

        # Add attribute
        security_label = self.tcex.v3.security_label(name='TLP:WHITE')
        indicator.stage_security_label(security_label)

        indicator.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        indicator.delete()

    def test_address_stage_tag(self):
        """Test snippet"""
        # Begin Snippet
        indicator = self.tcex.v3.indicator(
            confidence=74,
            ip='111.111.111.108',
            rating=4,
            type='Address',
        )

        # Add attribute
        tag = self.tcex.v3.tag(name='Example-Tag')
        indicator.stage_tag(tag)

        indicator.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        indicator.delete()

    #
    # Delete Indicators
    #

    def test_address_delete_by_id(self):
        """Test snippet"""
        indicator = self.tcex.v3.indicator(
            confidence=74,
            ip='111.111.111.110',
            rating=4,
            type='Address',
        )
        indicator.create(params={'owner': 'TCI'})

        # Begin Snippet
        indicator = self.tcex.v3.indicator(id=indicator.model.id)
        indicator.delete(params={'owner': 'TCI'})
        # End Snippet

    def test_address_delete_by_summary(self):
        """Test snippet"""
        indicator = self.tcex.v3.indicator(
            confidence=74,
            ip='111.111.111.112',
            rating=4,
            type='Address',
        )
        indicator.create(params={'owner': 'TCI'})

        # Begin Snippet
        indicator = self.tcex.v3.indicator(summary='111.111.111.112')
        indicator.delete(params={'owner': 'TCI'})
        # End Snippet

    def test_address_delete_attribute(self):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(
            confidence=74,
            value1='111.111.111.114',
            rating=4,
            type='Address',
            attributes=[
                {
                    'type': 'Description',
                    'value': 'An example description attribute',
                },
                {
                    'type': 'Description',
                    'value': 'Another example description attribute',
                },
            ],
        )

        # Begin Snippet
        indicator = self.tcex.v3.indicator(summary='111.111.111.114')
        for attribute in indicator.attributes:
            if attribute.model.value == 'An example description attribute':
                attribute.delete()
        # End Snippet

    def test_address_remove_associations(self):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(
            value1='111.111.111.116',
            type='Address',
            associated_groups=[
                {'name': 'MyGroup0', 'type': 'Adversary'},
                {'name': 'MyGroup', 'type': 'Adversary'},
            ],
        )

        # Begin Snippet
        indicator = self.tcex.v3.indicator(summary='111.111.111.116')

        for association in indicator.associated_groups:
            if association.model.name == 'MyGroup':
                # IMPORTANT the "remove()" method will remove the association from the indicator and
                #    the "delete()" method will remove the association from the system.
                association.remove()
        # End Snippet

    def test_address_remove_security_label(self):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(
            value1='111.111.111.118',
            type='Address',
            security_labels=[
                {'name': 'TLP:WHITE'},
                {'name': 'TLP:GREEN'},
            ],
        )

        # Begin Snippet
        indicator = self.tcex.v3.indicator(summary='111.111.111.118')

        for security_label in indicator.security_labels:
            if security_label.model.name == 'TLP:WHITE':
                # IMPORTANT the "remove()" method will remove the security label from the indicator
                #    and the "delete()" method will remove the security label from the system.
                security_label.remove()
        # End Snippet

    def test_address_remove_tag(self):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(
            value1='111.111.111.120',
            type='Address',
            tags={'name': 'Example-Tag'},
        )

        # Begin Snippet
        indicator = self.tcex.v3.indicator(summary='111.111.111.120')

        for tag in indicator.tags:
            if tag.model.name == 'Example-Tag':
                # IMPORTANT the "remove()" method will remove the tag from the indicator and
                #    the "delete()" method will remove the tag from the system.
                tag.remove()
        # End Snippet

    #
    # Get Indicators
    #

    def test_indicator_get_by_id(self):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(type_='Host', value1='example-00.com')

        # Begin Snippet
        indicator = self.tcex.v3.indicator(id=indicator.model.id)
        indicator.get()
        # End Snippet

        # Add cleanup
        indicator.delete()

    def test_get_indicator_file_actions(self):
        """Test snippet"""
        md5 = '491426B9C10D17708FFAC9ACBE761B26'
        host_name = 'example-00.com'
        indicator = self.v3_helper.create_indicator(type_='File', value1=md5)
        host = self.v3_helper.create_indicator(type_='Host', value1=host_name)
        relationship_type = 'File DNS Query'
        indicator.stage_file_action({'relationship': relationship_type, 'indicator': host.model})
        indicator.update()

        # Begin Snippet
        indicator = self.tcex.v3.indicator(id=indicator.model.id)
        indicator.get(params={'fields': ['fileActions']})
        # End Snippet
        assert len(indicator.model.file_actions.data) == 1
        file_action = indicator.model.file_actions.data[0]
        assert file_action.relationship == relationship_type
        assert file_action.indicator.id == host.model.id

        # Add cleanup
        # indicator.delete()

    def test_add_indicator_file_actions(self):
        """Test snippet"""
        md5 = '491426B9C10D17708FFAC9ACBE761C26'
        host_name = 'example-00.com'
        indicator = self.v3_helper.create_indicator(type_='File', value1=md5)
        host = self.v3_helper.create_indicator(type_='Host', value1=host_name)

        # Begin Snippet
        relationship_type = 'File DNS Query'
        indicator.stage_file_action({'relationship': relationship_type, 'indicator': host.model})
        indicator.update()
        # End Snippet

        assert len(indicator.model.file_actions.data) == 1
        file_action = indicator.model.file_actions.data[0]
        assert file_action.relationship == relationship_type
        assert file_action.indicator.id == host.model.id

    def test_remove_indicator_file_actions(self):
        """Test snippet"""
        md5 = '491426B9C10D17708FFAC9BCBE761D26'
        host_name = 'example-00.com'
        host_name_1 = 'example-01.com'
        indicator = self.v3_helper.create_indicator(type_='File', value1=md5)
        host = self.v3_helper.create_indicator(type_='Host', value1=host_name)
        host_2 = self.v3_helper.create_indicator(type_='Host', value1=host_name_1)
        relationship_type = 'File DNS Query'
        indicator.stage_file_action({'relationship': relationship_type, 'indicator': host.model})
        indicator.stage_file_action({'relationship': relationship_type, 'indicator': host_2.model})
        indicator.update()

        # Begin Snippet
        # Get a fresh instance of the indicator object you wish to remove a file action from.
        indicator = self.v3.indicator(id=indicator.model.id)
        # [Stage Testing] - Stage an the file action to be removed
        indicator.stage_file_action({'relationship': relationship_type, 'indicator': host.model})
        # [Delete Testing] - Delete the newly staged file action
        indicator.update(mode='delete')
        # End Snippet

        assert len(indicator.model.file_actions.data) == 1
        file_action = indicator.model.file_actions.data[0]
        assert file_action.relationship == relationship_type
        assert file_action.indicator.id == host_2.model.id

    def test_replace_indicator_file_actions(self):
        """Test snippet"""
        md5 = '491426B9C20D17708FFAC9ACBE761D26'
        host_name = 'example-00.com'
        host_name_1 = 'example-01.com'
        indicator = self.v3_helper.create_indicator(type_='File', value1=md5)
        host = self.v3_helper.create_indicator(type_='Host', value1=host_name)
        host_2 = self.v3_helper.create_indicator(type_='Host', value1=host_name_1)
        relationship_type = 'File DNS Query'
        indicator.stage_file_action({'relationship': relationship_type, 'indicator': host.model})
        indicator.update()

        # Begin Snippet
        # Get a fresh instance of the indicator object you wish to remove a file action from.
        indicator = self.v3.indicator(id=indicator.model.id)
        # [Stage Testing] - Stage an the file action. This will replace the existing file actions.
        indicator.stage_file_action({'relationship': relationship_type, 'indicator': host_2.model})
        # [Replace Testing] - Replace all the current file actions with the new file actions.
        indicator.update(mode='replace')
        # End Snippet

        assert len(indicator.model.file_actions.data) == 1
        file_action = indicator.model.file_actions.data[0]
        assert file_action.relationship == relationship_type
        assert file_action.indicator.id == host_2.model.id

    def test_get_indicator_file_occurrence(self):
        """Test snippet"""
        md5 = '491426B9C10D17708FFAC9ACBE761D38'
        indicator = self.v3_helper.create_indicator(type_='File', value1=md5)
        indicator.stage_file_occurrence(
            {
                'file_name': 'Example.csv',
                'path': '/temp/path/to/file.csv',
                'date': '2022-08-25T17:52:39Z',
            }
        )
        indicator.update()

        # Begin Snippet
        indicator = self.tcex.v3.indicator(id=indicator.model.id)
        indicator.get(params={'fields': ['fileOccurrences']})
        # End Snippet

        assert len(indicator.model.file_occurrences.data) == 1
        file_occurrences = indicator.model.file_occurrences.data[0]
        assert file_occurrences.path == '/temp/path/to/file.csv'
        assert file_occurrences.file_name == 'Example.csv'

    def test_add_indicator_file_occurrence(self):
        """Test snippet"""
        md5 = '441426B9C10D17708FFAC9ACBE761D27'
        indicator = self.v3_helper.create_indicator(type_='File', value1=md5)

        # Begin Snippet
        indicator.stage_file_occurrence(
            {
                'file_name': 'Example.csv',
                'path': '/temp/path/to/file.csv',
                'date': '2022-08-25T17:52:39Z',
            }
        )
        indicator.update()

        # NOTE:

        # Submitting the Update does not automatically populate the file_occurrences field like it
        # does for other fields so an additional call is made to get the field populated
        # if that data is needed.

        # End Snippet

    def test_remove_indicator_file_occurrence(self):
        """Test snippet"""
        md5 = '291426B9C10D17708FFAC9ACBE761D38'
        indicator = self.v3_helper.create_indicator(type_='File', value1=md5)
        indicator.stage_file_occurrence(
            {
                'file_name': 'Example.csv',
                'path': '/temp/path/to/file.csv',
                'date': '2022-08-25T17:52:39Z',
            }
        )
        indicator.stage_file_occurrence(
            {
                'file_name': 'Example_2.csv',
                'path': '/temp/path/to/file.csv',
                'date': '2022-08-25T17:52:39Z',
            }
        )
        indicator.update()
        indicator = self.tcex.v3.indicator(id=indicator.model.id)
        indicator.get(params={'fields': ['fileOccurrences']})
        for file_occurrence in indicator.model.file_occurrences.data:
            if file_occurrence.file_name == 'Example.csv':
                file_occurrence_id = file_occurrence.id
                break
        else:
            assert False, 'Example.csv not found in file_occurrences'

        # Begin Snippet
        # Get a fresh instance of the indicator object you wish to remove a file action from.
        indicator = self.v3.indicator(id=indicator.model.id)
        # [Stage Testing] - Stage an the file occurrence to be removed
        indicator.stage_file_occurrence({'id': file_occurrence_id})
        # [Delete Testing] - Delete the newly staged file occurrence
        indicator.update(mode='delete')

        # Submitting the Update does not automatically populate the file_occurrences field like it
        # does for other fields so an additional call is made to get the field populated
        # if that data is needed.

        # End Snippet

        indicator = self.tcex.v3.indicator(id=indicator.model.id)
        indicator.get(params={'fields': ['fileOccurrences']})

        assert len(indicator.model.file_occurrences.data) == 1
        file_occurrences = indicator.model.file_occurrences.data[0]
        assert file_occurrences.path == '/temp/path/to/file.csv'
        assert file_occurrences.file_name == 'Example_2.csv'

    def test_replace_indicator_file_occurrence(self):
        """Test snippet"""
        md5 = '391426B9C10D17708FFAC9ACBE761D38'
        indicator = self.v3_helper.create_indicator(type_='File', value1=md5)
        indicator.stage_file_occurrence(
            {
                'file_name': 'Example_2.csv',
                'path': '/temp/path/to/file.csv',
                'date': '2022-08-25T17:52:39Z',
            }
        )
        indicator.update()

        # Begin Snippet
        # Get a fresh instance of the indicator object you wish to remove a file action from.
        indicator = self.v3.indicator(id=indicator.model.id)
        # [Stage Testing] - Stage an the file occurrence to replace the existing file occurrences.
        indicator.stage_file_occurrence(
            {
                'file_name': 'Example.csv',
                'path': '/temp/path/to/file.csv',
                'date': '2022-08-25T17:52:39Z',
            }
        )
        # [Replace Testing] - Replace all the current file occurrences with
        # the new file occurrences.
        indicator.update(mode='replace')

        # Submitting the Update does not automatically populate the file_occurrences field like it
        # does for other fields so an additional call is made to get the field populated
        # if that data is needed.

        # End Snippet

        indicator = self.tcex.v3.indicator(id=indicator.model.id)
        indicator.get(params={'fields': ['fileOccurrences']})

        assert len(indicator.model.file_occurrences.data) == 1
        file_occurrences = indicator.model.file_occurrences.data[0]
        assert file_occurrences.path == '/temp/path/to/file.csv'
        assert file_occurrences.file_name == 'Example.csv'

    def test_indicator_get_by_summary(self):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(type_='Host', value1='example-02.com')

        # Begin Snippet
        indicator = self.tcex.v3.indicator(summary=indicator.model.summary)
        indicator.get()
        # End Snippet

        # Add cleanup
        indicator.delete()

    def test_indicator_get_by_raw_tql(self):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(type_='Host', value1='example-04.com')

        # Begin Snippet
        indicators = self.tcex.v3.indicators()
        indicators.filter.tql = (
            'typeName in ("Host", "Address", "EmailAddress", "File", "URL") and '
            '(summary like "%example%" or tag like "%example%")'
        )

        for indicator in indicators:
            print(indicator)
        # End Snippet

        # Add cleanup
        indicator.delete()

    #
    # Update Indicators
    #

    def test_address_update(self):
        """Test snippet"""
        indicator = self.tcex.v3.indicator(
            confidence=74,
            ip='111.111.111.122',
            rating=4,
            type='Address',
        )
        indicator.create(params={'owner': 'TCI'})

        # Begin Snippet
        indicator = self.tcex.v3.indicator(summary='111.111.111.122')
        # This will update the confidence to "50"
        indicator.model.confidence = 50
        indicator.update(params={'owner': 'TCI'})
        # End Snippet

    #
    # Get Deleted Indicators
    #

    def test_indicator_deleted(self):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(
            value1='111.111.111.124',
            type='Address',
        )
        indicator.delete()

        # Begin Snippet
        # The "deleted()" method will not use the params set on the `Indicators` object.
        for indicator in self.tcex.v3.indicators().deleted(
            deleted_since='1 day ago', type_='Address', owner='TCI'
        ):
            print(indicator.model.dict(exclude_none=True))
        # End Snippet
