"""Test the TcEx API Snippets."""
# standard-library
# standard library
import base64

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestVictimSnippets(TestV3):
    """Test TcEx API Interface."""

    example_pdf = None
    v3 = None

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('victims')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

        # remove old victims
        victims = self.tcex.v3.victims()
        victims.filter.summary(TqlOperator.EQ, 'MyVictim')
        for victim in victims:
            victim.delete()

    def test_victim_create(self):
        """Test snippet"""
        # Begin Snippet
        victim = self.tcex.v3.victim(
            name='MyVictim',
            description='Example Victim Description',
            nationality='American',
            suborg='Sub Organization',
            type='Random Type',
            work_location='Home'
        )

        victim.create(params={'owner': 'TCI'})
        # End Snippet

    # def test_victim_stage_group_associations(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     victim = self.v3_helper.create_victim()
    #
    #     # Add attribute
    #     association = self.tcex.v3.group(name='MyThreat', type='Threat')
    #     victim.stage_associated_group(association)
    #
    #     victim.create(params={'owner': 'TCI'})
    #     # End Snippet
    #
    # def test_victim_stage_attribute(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     victim = self.v3_helper.create_victim()
    #
    #     # Add attribute
    #     attribute = self.tcex.v3.victim_attribute(
    #         value='An example description attribute.',
    #         type='Description',
    #     )
    #     victim.stage_attribute(attribute)
    #
    #     victim.create(params={'owner': 'TCI'})
    #     # End Snippet
    #
    # def test_adversary_stage_security_label(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     victim = self.v3_helper.create_victim()
    #
    #     # Add attribute
    #     security_label = self.tcex.v3.security_label(name='TLP:WHITE')
    #     victim.stage_security_label(security_label)
    #
    #     victim.create(params={'owner': 'TCI'})
    #     # End Snippet
    #
    # def test_adversary_stage_tag(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     victim = self.v3_helper.create_victim()
    #
    #     # Add attribute
    #     tag = self.tcex.v3.tag(name='Example-Tag')
    #     victim.stage_tag(tag)
    #
    #     victim.create(params={'owner': 'TCI'})
    #     # End Snippet
    #
    # def test_adversary_delete_by_id(self):
    #     """Test snippet"""
    #     victim = self.v3_helper.create_victim()
    #
    #     # Begin Snippet
    #     victim = self.tcex.v3.victim(id=victim.model.id)
    #     victim.delete(params={'owner': 'TCI'})
    #     # End Snippet
    #
    # def test_adversary_delete_by_name(self):
    #     """Test snippet"""
    #     victim = self.tcex.v3.victim(
    #         name='MyVictim',
    #         type='Why is this a thing???',
    #     )
    #     victim.create(params={'owner': 'TCI'})
    #
    #     # Begin Snippet
    #     victims = self.tcex.v3.victims()
    #     victims.filter.name(TqlOperator.EQ, 'MyVictim')
    #     for victim in victims:
    #         # IMPORTANT: this will delete all victims with the name "MyVictim"
    #         victim.delete()
    #     # End Snippet
    #
    # def test_adversary_delete_attribute(self):
    #     """Test snippet"""
    #     victim = self.v3_helper.create_victim(
    #         attributes=[
    #             {
    #                 'type': 'Description',
    #                 'value': 'An example description attribute',
    #             },
    #             {
    #                 'type': 'Description',
    #                 'value': 'Another example description attribute',
    #             },
    #         ],
    #     )
    #     # Begin Snippet
    #     victim = self.tcex.v3.victim(id=victim.model.id)
    #     for attribute in victim.attributes:
    #         if attribute.model.value == 'An example description attribute':
    #             attribute.delete()
    #     # End Snippet
    #
    # def test_victim_get_by_id(self):
    #     """Test snippet"""
    #     victim = self.v3_helper.create_victim()
    #
    #     # Begin Snippet
    #     victim = self.tcex.v3.victim(id=victim.model.id, params={'fields': ['_all_']})
    #     victim.get()
    #     # End Snippet
    #
    # def test_adversary_get_tql(self):
    #     """Test snippet"""
    #     group = self.tcex.v3.group(
    #         name='MyAdversary',
    #         type='Adversary',
    #     )
    #     group.create(params={'owner': 'TCI'})
    #
    #     # Begin Snippet
    #     groups = self.tcex.v3.groups()
    #     groups.filter.date_added(TqlOperator.GT, '1 day ago')
    #     groups.filter.id(TqlOperator.EQ, group.model.id)
    #     groups.filter.owner_name(TqlOperator.EQ, 'TCI')
    #     groups.filter.type_name(TqlOperator.EQ, 'Adversary')
    #     for group in groups:
    #         print(group.model.dict(exclude_none=True))
    #     # End Snippet
    #
    # def test_adversary_remove_group_associations(self):
    #     """Test snippet"""
    #     group = self.v3_helper.create_group(
    #         name='MyAdversary',
    #         type='Adversary',
    #         associated_groups=[
    #             {'name': 'MyGroup0', 'type': 'Adversary'},
    #             {'name': 'MyGroup', 'type': 'Adversary'},
    #         ],
    #     )
    #
    #     # Begin Snippet
    #     group = self.tcex.v3.group(id=group.model.id)
    #
    #     for association in group.associated_groups:
    #         if association.model.name == 'MyGroup':
    #             # IMPORTANT the "remove()" method will remove the association from the group and
    #             #    the "delete()" method will remove the association from the system.
    #             association.remove()
    #     # End Snippet
    #
    # def test_adversary_remove_indicator_associations(self):
    #     """Test snippet"""
    #     group = self.v3_helper.create_group(
    #         name='MyAdversary',
    #         type='Adversary',
    #         associated_indicators=[
    #             {'ip': '111.111.111.111', 'type': 'Address'},
    #             {'ip': '222.222.222.222', 'type': 'Address'},
    #         ],
    #     )
    #
    #     # Begin Snippet
    #     group = self.tcex.v3.group(id=group.model.id)
    #
    #     for association in group.associated_indicators:
    #         if association.model.summary == '222.222.222.222':
    #             # IMPORTANT the "remove()" method will remove the association from the group and
    #             #    the "delete()" method will remove the association from the system.
    #             association.remove()
    #     # End Snippet
    #
    # def test_adversary_remove_security_label(self):
    #     """Test snippet"""
    #     group = self.v3_helper.create_group(
    #         name='MyAdversary',
    #         type='Adversary',
    #         security_labels=[
    #             {'name': 'TLP:WHITE'},
    #             {'name': 'TLP:GREEN'},
    #         ],
    #     )
    #
    #     # Begin Snippet
    #     group = self.tcex.v3.group(id=group.model.id)
    #
    #     for security_label in group.security_labels:
    #         if security_label.model.name == 'TLP:WHITE':
    #             # IMPORTANT the "remove()" method will remove the security label from the group and
    #             #    the "delete()" method will remove the security label from the system.
    #             security_label.remove()
    #     # End Snippet
    #
    # def test_adversary_remove_tag(self):
    #     """Test snippet"""
    #     group = self.v3_helper.create_group(
    #         name='MyAdversary',
    #         type='Adversary',
    #         tags={'name': 'Example-Tag'},
    #     )
    #
    #     # Begin Snippet
    #     group = self.tcex.v3.group(id=group.model.id)
    #
    #     for tag in group.tags:
    #         if tag.model.name == 'Example-Tag':
    #             # IMPORTANT the "remove()" method will remove the tag from the group and
    #             #    the "delete()" method will remove the tag from the system.
    #             tag.remove()
    #     # End Snippet
    #
    # def test_adversary_remove_tag_using_mode(self):
    #     """Test snippet"""
    #     group = self.v3_helper.create_group(
    #         name='MyAdversary',
    #         type='Adversary',
    #         tags={'name': 'Example-Tag'},
    #     )
    #
    #     # Begin Snippet
    #     group = self.tcex.v3.group(id=group.model.id)
    #     updated_group = self.tcex.v3.group(id=group.model.id)
    #     for tag in group.tags:
    #         if tag.model.name == 'Example-Tag':
    #             # IMPORTANT the "remove()" method will remove the tag from the group and
    #             #    the "delete()" method will remove the tag from the system.
    #             updated_group.stage_tag(tag)
    #     updated_group.update()
    #     # End Snippet
    #
    # def test_adversary_update(self):
    #     """Test snippet"""
    #     group = self.v3_helper.create_group(
    #         name='MyAdversary',
    #         type='Adversary',
    #     )
    #
    #     # Begin Snippet
    #     group = self.tcex.v3.group(id=group.model.id)
    #     # This will update the confidence to "50"
    #     group.model.name = 50
    #     group.update(params={'owner': 'TCI'})
    #     # End Snippet
    #
    # def test_document_download_pdf(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     group = self.tcex.v3.group(
    #         name='MyAdversary',
    #         type='Adversary',
    #     )
    #     group.create(params={'owner': 'TCI'})
    #
    #     # Begin Snippet
    #     group = self.tcex.v3.group(id=group.model.id)
    #     _ = group.pdf()  # pdf is returned as bytes
    #     # End Snippet
    #
    # def test_document_upload(self):
    #     """Test snippet"""
    #     file_content = base64.b64decode(self.example_pdf)
    #     # Begin Snippet
    #     group = self.tcex.v3.group(
    #         file_name='example.pdf',
    #         name='MyDocument',
    #         type='Document',
    #     )
    #     group.create(params={'owner': 'TCI'})
    #     response = group.upload(file_content)
    #     if not response.ok:
    #         print(f'The upload failed: {response.reason}')
    #     # End Snippet
    #
    #     group.delete()
    #
    # def test_document_download(self):
    #     """Test snippet"""
    #     group = self.v3_helper.create_group(
    #         file_name='example.pdf',
    #         name='MyDocument',
    #         type_='Document',
    #     )
    #     file_content = base64.b64decode(self.example_pdf)
    #     _ = group.upload(file_content)
    #
    #     # Begin Snippet
    #     group = self.tcex.v3.group(id=group.model.id)
    #     _ = group.download()  # content is returned as bytes
    #     if not group.request.ok:
    #         print(f'The download failed: {group.request.reason}')
    #     # End Snippet
