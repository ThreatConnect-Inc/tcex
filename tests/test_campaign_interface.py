# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_campaign_many_0():
#     summary = 'campaign1'
#     campaign = ti.campaign(summary)
#     for single in campaign.many():
#         print(single)

# def test_campaign_many_1():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary)
#     for single in campaign.many(owner='System'):
#         print(single)

# def test_campaign_request_0():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary)
#     response = campaign.request(1, 0, owner='System')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_campaign_single_0():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary, unique_id=142740)
#     response = campaign.single(owner='ThreatConnect Intelligence')
#     assert response.json().get('status') == 'Success'

# def test_campaign_indicator_associations_0():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary, unique_id=142740)
#     for association in campaign.indicator_associations():
#         print(association)

# def test_campaign_tags():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary, unique_id=142740)
#     for tag in campaign.tags():
#         print(tag)

# #Doesn't return Tasks for some reason, i blame the api
# def test_campaign_group_associations_0():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary, unique_id=142740)
#     for association in campaign.group_associations():
#         print(association)

# def test_campaign_group_associations_type_0():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary, unique_id=142740)
#     for association in campaign.group_associations_type(ti.document(None, None)):
#         print(association)

# def test_campaign_indicator_associations_type_0():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary, unique_id=142740)
#     for association in campaign.indicator_associations_types(ti.address(None)):
#         print(association)

# def test_campaign_attributes_0():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary, unique_id=142740)
#     for attribute in campaign.attributes():
#         print(attribute)

# def test_campaign_security_labels_0():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary, unique_id=142740)
#     for label in campaign.labels():
#         print(label)

# def test_campaign_attribute_security_labels():
#     summary = 'campaign2'
#     campaign = ti.campaign(summary, unique_id=142740)
#     for label in campaign.attribute_labels(933465):
#         print(label)

# def test_campaign_create_0():
#     """Test campaign creation"""
#     summary = 'campaign1'
#     campaign = ti.campaign(summary)
#     response = campaign.create('System')
#     assert response.json().get('status') == 'Success'

# def test_campaign_create_1():
#     """Test campaign creation"""
#     summary = 'campaign2'
#     campaign = ti.write.campaign(summary, first_seen='5/3/17')
#     response = campaign.create('System')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_campaign_update_0():
#     """Test campaign creation"""
#     unique_id = '142728'
#     campaign = ti.write.campaign(None, unique_id=unique_id, first_seen='5/14/17')
#     response = campaign.update()
#     assert response.json().get('status') == 'Success'

# def test_campaign_update_1():
#     """Test campaign creation"""
#     unique_id = '142728'
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     response = campaign.firstSeen('5/14/16')
#     assert response.json().get('status') == 'Success'

# def test_campaign_update_1_0():
#     """Test campaign creation"""
#     unique_id = '142728'
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     response = campaign.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_campaign_update_2():
#     unique_id = '142728'
#     attribute_id = 933459
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     response = campaign.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_campaign_update_3():
#     unique_id = '142728'
#     attribute_id = 933459
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     response = campaign.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_campaign_update_4():
#     unique_id = '142728'
#     attribute_id = 933459
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     response = campaign.delete_attribute(attribute_id)
#     assert response.json().get('status') == 'Success'

# def test_campaign_update_5():
#     unique_id = '142728'
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     response = campaign.label('TLP:AMBER')
#     print(response)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_campaign_update_6():
#     unique_id = '142728'
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     response = campaign.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_campaign_create_indicator_association():
#     unique_id = '142727'
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     unique_id = '221.123.32.12'
#     address = ti.write.address(None, unique_id=unique_id)
#     response = campaign.create_association(address)
#     assert response.json().get('status') == 'Success'

# def test_campaign_create_group_association():
#     unique_id = '142727'
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     unique_id = '142726'
#     campaign_target = ti.write.campaign(None, unique_id=unique_id)
#     response = campaign.create_association(campaign_target)
#     assert response.json().get('status') == 'Success'

# def test_campaign_create_victim_association():
#     unique_id = '142727'
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     unique_id = '4'
#     victim = ti.write.victim(None, unique_id=unique_id)
#     response = campaign.create_association(victim)
#     assert response.json().get('status') == 'Success'

# def test_campaign_delete_victim_association():
#     unique_id = '142727'
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     unique_id = '4'
#     victim = ti.write.victim(None, unique_id=unique_id)
#     response = campaign.delete_association(victim)
#     assert response.json().get('status') == 'Success'

# def test_campaign_delete_0():
#     unique_id = '142728'
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     response = campaign.delete()
#     assert response.json().get('status') == 'Success'
