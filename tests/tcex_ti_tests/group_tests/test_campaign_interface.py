# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_campaign_create_0():
#     """Test campaign creation"""
#     summary = 'campaign1'
#     campaign = ti.write.campaign(summary)
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

# def test_campaign_delete_0():
#     unique_id = '142728'
#     campaign = ti.write.campaign(None, unique_id=unique_id)
#     response = campaign.delete()
#     assert response.json().get('status') == 'Success'
