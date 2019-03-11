# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_victim_create_0():
#     """Test victim creation"""
#     summary = 'Dummy victim 005'
#     victim = ti.write.victim(summary)
#     response = victim.create('System')
#     assert response.json().get('status') == 'Success'

# def test_victim_create_1():
#     """Test victim creation"""
#     summary = 'Dummy victim 001'
#     victim = ti.write.victim(summary, org='System')
#     response = victim.create('System')
#     assert response.json().get('status') == 'Success'

# def test_victim_update_0():
#     """Test victim creation"""
#     unique_id = '9'
#     summary = 'Dummy victim 001'
#     # A valid name MUST be present to perform the update
#     victim = ti.write.victim(summary, id=unique_id, org='TCI')
#     response = victim.update()
#     assert response.json().get('status') == 'Success'

# def test_victim_update_1():
#     """Test adversary creation"""
#     unique_id = '9'
#     victim = ti.write.victim(None, id=unique_id)
#     response = victim.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_victim_update_2():
#     unique_id = '9'
#     attribute_id = 1
#     victim = ti.write.victim(None, id=unique_id)
#     response = victim.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_victim_update_3():
#     unique_id = '9'
#     attribute_id = 1
#     victim = ti.write.victim(None, id=unique_id)
#     response = victim.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_victim_update_4():
#     unique_id = '9'
#     attribute_id = 1
#     victim = ti.write.victim(None, id=unique_id)
#     response = victim.delete_attribute(attribute_id)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_victim_update_5():
#     unique_id = '9'
#     victim = ti.write.victim(None, id=unique_id)
#     response = victim.label('TLP:AMBER')
#     print(response)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_victim_update_6():
#     unique_id = '9'
#     victim = ti.write.victim(None, id=unique_id)
#     response = victim.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_victim_delete_0():
#     unique_id = '9'
#     victim = ti.write.victim(None, id=unique_id)
#     response = victim.delete()
#     assert response.json().get('status') == 'Success'

# def test_victim_update_3():
#     victim_id = 142722
#     victim = ti.write.victim(None, id=victim_id)
#     response = victim.attribute('Description', 'Test_Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_victim_update_4():
#     victim_id = 142722
#     attribute_id = 933455
#     victim = ti.write.victim(None, id=victim_id)
#     response = victim.delete_attribute(attribute_id)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_victim_update_5():
#     victim_id = 142722
#     attribute_id = 933456
#     victim = ti.write.victim(None, id=victim_id)
#     response = victim.attribute_labels(attribute_id, 'TLP:AMBER')
#     # Returns a 404 if the security label doesnt exist.
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_victim_update_6():
#     victim_id = 142722
#     attribute_id = 933456
#     victim = ti.write.victim(None, id=victim_id)
#     response = victim.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response)
#     assert response.json().get('status') == 'Success'

