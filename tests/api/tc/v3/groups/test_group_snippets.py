"""Test the TcEx API Snippets."""
# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestCaseManagement, V3Helper


class TestGroupSnippets(TestCaseManagement):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('cases')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

        # remove old cases
        groups = self.tcex.v3.groups()
        groups.filter.summary(TqlOperator.EQ, 'MyAdversary')
        for group in groups:
            group.delete()

    def test_adversary_create(self):
        """Test snippet"""
        # Begin Snippet
        group = self.tcex.v3.group(
            name='MyAdversary',
            type='Adversary',
        )

        group.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        group.delete()

    def test_adversary_stage_group_associations(self):
        """Test snippet"""
        # Begin Snippet
        group = self.tcex.v3.group(
            name='MyAdversary',
            type='Adversary',
        )

        # Add attribute
        association = self.tcex.v3.group(name='MyThreat', type='Threat')
        group.stage_associated_group(association)

        group.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        group.delete()

    def test_adversary_stage_indicator_associations(self):
        """Test snippet"""
        # Begin Snippet
        group = self.tcex.v3.group(
            name='MyAdversary',
            type='Adversary',
        )

        # Add attribute
        association = self.tcex.v3.indicator(ip='111.111.111.111', type='Address')
        group.stage_associated_indicator(association)

        group.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        group.delete()

    def test_adversary_stage_attribute(self):
        """Test snippet"""
        # Begin Snippet
        group = self.tcex.v3.group(
            name='MyAdversary',
            type='Adversary',
        )

        # Add attribute
        attribute = self.tcex.v3.group_attribute(
            value='An example description attribute.',
            type='Description',
        )
        group.stage_attribute(attribute)

        group.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        group.delete()

    def test_adversary_stage_security_label(self):
        """Test snippet"""
        # Begin Snippet
        group = self.tcex.v3.group(
            name='MyAdversary',
            type='Adversary',
        )

        # Add attribute
        security_label = self.tcex.v3.security_label(name='TLP:WHITE')
        group.stage_security_label(security_label)

        group.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        group.delete()

    def test_adversary_stage_tag(self):
        """Test snippet"""
        # Begin Snippet
        group = self.tcex.v3.group(
            name='MyAdversary',
            type='Adversary',
        )

        # Add attribute
        tag = self.tcex.v3.tag(name='Example-Tag')
        group.stage_tag(tag)

        group.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        group.delete()

    def test_adversary_delete_by_id(self):
        """Test snippet"""
        group = self.tcex.v3.group(
            name='MyAdversary',
            type='Adversary',
        )
        group.create(params={'owner': 'TCI'})

        # Begin Snippet
        group = self.tcex.v3.group(id=group.model.id)
        group.delete(params={'owner': 'TCI'})
        # End Snippet

    def test_adversary_delete_by_summary(self):
        """Test snippet"""
        group = self.tcex.v3.group(
            name='MyAdversary',
            type='Adversary',
        )
        group.create(params={'owner': 'TCI'})

        # Begin Snippet
        group = self.tcex.v3.group(id=group.model.id)
        group.delete(params={'owner': 'TCI'})
        # End Snippet

    def test_adversary_delete_attribute(self):
        """Test snippet"""
        group = self.v3_helper.create_group(
            value1='MyAdversary',
            type='Adversary',
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
        group = self.tcex.v3.group(id=group.model.id)
        for attribute in group.attributes:
            if attribute.model.value == 'An example description attribute':
                attribute.delete()
        # End Snippet

    def test_adversary_remove_group_associations(self):
        """Test snippet"""
        group = self.v3_helper.create_group(
            name='MyAdversary',
            type='Adversary',
            associated_groups=[
                {'name': 'MyGroup0', 'type': 'Adversary'},
                {'name': 'MyGroup', 'type': 'Adversary'},
            ],
        )

        # Begin Snippet
        group = self.tcex.v3.group(id=group.model.id)

        for association in group.associated_groups:
            if association.model.name == 'MyGroup':
                # IMPORTANT the "remove()" method will remove the association from the group and
                #    the "delete()" method will remove the association from the system.
                association.remove()
        # End Snippet

    def test_adversary_remove_indicator_associations(self):
        """Test snippet"""
        group = self.v3_helper.create_group(
            name='MyAdversary',
            type='Adversary',
            associated_indicators=[
                {'ip': '111.111.111.111', 'type': 'Address'},
                {'ip': '222.222.222.222', 'type': 'Address'},
            ],
        )

        # Begin Snippet
        group = self.tcex.v3.group(id=group.model.id)

        for association in group.associated_indicators:
            if association.model.summary == '222.222.222.222':
                # IMPORTANT the "remove()" method will remove the association from the group and
                #    the "delete()" method will remove the association from the system.
                association.remove()
        # End Snippet

    def test_adversary_remove_security_label(self):
        """Test snippet"""
        group = self.v3_helper.create_group(
            value1='MyAdversary',
            type='Adversary',
            security_labels=[
                {'name': 'TLP:WHITE'},
                {'name': 'TLP:GREEN'},
            ],
        )

        # Begin Snippet
        group = self.tcex.v3.group(id=group.model.id)

        for security_label in group.security_labels:
            if security_label.model.name == 'TLP:WHITE':
                # IMPORTANT the "remove()" method will remove the security label from the group and
                #    the "delete()" method will remove the security label from the system.
                security_label.remove()
        # End Snippet

    def test_adversary_remove_tag(self):
        """Test snippet"""
        group = self.v3_helper.create_group(
            value1='MyAdversary',
            type='Adversary',
            tags={'name': 'Example-Tag'},
        )

        # Begin Snippet
        group = self.tcex.v3.group(id=group.model.id)

        for tag in group.tags:
            if tag.model.name == 'Example-Tag':
                # IMPORTANT the "remove()" method will remove the tag from the group and
                #    the "delete()" method will remove the tag from the system.
                tag.remove()
        # End Snippet

    def test_adversary_remove_tag_using_mode(self):
        """Test snippet"""
        group = self.v3_helper.create_group(
            value1='MyAdversary',
            type='Adversary',
            tags={'name': 'Example-Tag'},
        )

        # Begin Snippet
        group = self.tcex.v3.group(id=group.model.id)
        updated_group = self.tcex.v3.group(id=group.model.id)
        for tag in group.tags:
            if tag.model.name == 'Example-Tag':
                # IMPORTANT the "remove()" method will remove the tag from the group and
                #    the "delete()" method will remove the tag from the system.
                updated_group.stage_tag(tag)
        updated_group.update()
        # End Snippet

    def test_adversary_update(self):
        """Test snippet"""
        group = self.tcex.v3.group(
            name='MyAdversary',
            type='Adversary',
        )
        group.create(params={'owner': 'TCI'})

        # Begin Snippet
        group = self.tcex.v3.group(id=group.model.id)
        # This will update the confidence to "50"
        group.model.confidence = 50
        group.update(params={'owner': 'TCI'})
        # End Snippet
