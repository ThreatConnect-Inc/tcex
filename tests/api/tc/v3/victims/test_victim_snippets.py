"""Test the TcEx API Snippets."""
# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestVictimSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('victims')

    def test_victim_create(self):
        """Test snippet"""
        # Begin Snippet
        victim = self.tcex.api.tc.v3.victim(
            name='MyVictim-01',
            description='Example Victim Description',
            nationality='American',
            suborg='Sub Organization',
            type='Random Type',
            work_location='Home',
        )

        victim.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        victim.delete()

    def test_victim_stage_attribute(self):
        """Test snippet"""
        # Begin Snippet
        victim = self.tcex.api.tc.v3.victim(
            name='MyVictim-02',
            description='Example Victim Description',
            nationality='American',
            suborg='Sub Organization',
            type='Random Type',
            work_location='Home',
        )

        # stage attribute
        attribute = self.tcex.api.tc.v3.victim_attribute(
            value='An example description attribute.',
            type='Description',
        )
        victim.stage_attribute(attribute)

        victim.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        victim.delete()

    def test_victim_stage_security_label(self):
        """Test snippet"""
        # Begin Snippet
        victim = self.tcex.api.tc.v3.victim(
            name='MyVictim-03',
            description='Example Victim Description',
            nationality='American',
            suborg='Sub Organization',
            type='Random Type',
            work_location='Home',
        )

        # stage security label
        security_label = self.tcex.api.tc.v3.security_label(name='TLP:WHITE')
        victim.stage_security_label(security_label)

        victim.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        victim.delete()

    def test_victim_stage_tag(self):
        """Test snippet"""
        # Begin Snippet
        victim = self.tcex.api.tc.v3.victim(
            name='MyVictim-04',
            description='Example Victim Description',
            nationality='American',
            suborg='Sub Organization',
            type='Random Type',
            work_location='Home',
        )

        # stage tag
        tag = self.tcex.api.tc.v3.tag(name='Example-Tag')
        victim.stage_tag(tag)

        victim.create(params={'owner': 'TCI'})
        # End Snippet

        # Add cleanup
        victim.delete()

    #
    # Delete
    #

    def test_victim_delete_by_id(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim()

        # Begin Snippet
        victim = self.tcex.api.tc.v3.victim(id=victim.model.id)
        victim.delete(params={'owner': 'TCI'})
        # End Snippet

    def test_victim_delete_by_name(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim(name='MyVictim-05')
        # victim = self.tcex.api.tc.v3.victim(
        #     name='MyVictim',
        # )
        # victim.create(params={'owner': 'TCI'})

        # Begin Snippet
        victims = self.tcex.api.tc.v3.victims()
        victims.filter.name(TqlOperator.EQ, 'MyVictim-05')
        for victim in victims:
            # IMPORTANT: this will delete all victims with the name "MyVictim-05"
            victim.delete()
        # End Snippet

    def test_victim_delete_attribute(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim(
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
        victim = self.tcex.api.tc.v3.victim(id=victim.model.id)
        for attribute in victim.attributes:
            if attribute.model.value == 'An example description attribute':
                attribute.delete()
        # End Snippet

    def test_victim_remove_security_label(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim(
            security_labels=[
                {'name': 'TLP:WHITE'},
                {'name': 'TLP:GREEN'},
            ],
        )

        # Begin Snippet
        victim = self.tcex.api.tc.v3.victim(id=victim.model.id)

        for security_label in victim.security_labels:
            if security_label.model.name == 'TLP:WHITE':
                # IMPORTANT the "remove()" method will remove the security label from the group and
                #    the "delete()" method will remove the security label from the system.
                security_label.remove()
        # End Snippet

    def test_victim_remove_tag(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim(
            tags={'name': 'Example-Tag'},
        )

        # Begin Snippet
        victim = self.tcex.api.tc.v3.victim(id=victim.model.id)

        for tag in victim.tags:
            if tag.model.name == 'Example-Tag':
                # IMPORTANT the "remove()" method will remove the tag from the group and
                #    the "delete()" method will remove the tag from the system.
                tag.remove()
        # End Snippet

    def test_victim_remove_multiple_tags_using_mode(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim(
            tags=[
                {'name': 'Example-Tag'},
                {'name': 'Example-Tag-2'},
            ]
        )

        # Begin Snippet
        victim = self.tcex.api.tc.v3.victim(id=victim.model.id)
        # IMPORTANT retrieve the groups tags from the system not using group.model.tags
        for tag in victim.tags:
            if tag.model.name in ['Example-Tag', 'Example-Tag-2']:
                victim.stage_tag(tag)
        victim.update(mode='delete')
        # End Snippet

    #
    # Get Victim
    #

    def test_victim_get_by_id(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim()

        # Begin Snippet
        victim = self.tcex.api.tc.v3.victim(id=victim.model.id, params={'fields': ['_all_']})
        victim.get()
        # End Snippet

    def test_victim_get_by_name(self):
        """Test snippet"""
        self.v3_helper.create_victim(name='MyVictim-06')

        # Begin Snippet
        victims = self.tcex.api.tc.v3.victims()
        victims.filter.name(TqlOperator.EQ, 'MyVictim-06')
        for victim in victims:
            print(victim.model.dict(exclude_none=True))
        # End Snippet

    #
    # Update Victim
    #

    def test_victim_update(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim(name='Name to be Updated')

        # Begin Snippet
        victim = self.tcex.api.tc.v3.victim(id=victim.model.id)
        # This will update the name to "MyVictim"
        victim.model.name = 'MyVictim-07'
        victim.update(params={'owner': 'TCI'})
        # End Snippet
