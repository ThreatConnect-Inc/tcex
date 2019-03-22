# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_adversary_create_0():
#     """Test adversary creation"""
#     summary = '221.123.32.12'
#     adversary = ti.write.adversary(summary)
#     response = adversary.create('System')
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_adversary_create_1():
#     """Test adversary creation"""
#     summary = '221.123.32.13'
#     adversary = ti.write.adversary(summary, rating=4, confidence=90)
#     response = adversary.create('System')
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_0():
#     """Test adversary creation"""
#     unique_id = '221.123.32.13'
#     adversary = ti.write.adversary(None, id=unique_id, rating=3)
#     response = adversary.update()
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_1():
#     """Test adversary creation"""
#     unique_id = '221.123.32.13'
#     adversary = ti.write.adversary(None, id=unique_id)
#     response = adversary.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_2():
#     unique_id = '221.123.32.13'
#     attribute_id = 3232636
#     adversary = ti.write.adversary(None, id=unique_id)
#     response = adversary.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_3():
#     unique_id = '221.123.32.13'
#     attribute_id = 3232636
#     adversary = ti.write.adversary(None, id=unique_id)
#     response = adversary.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_4():
#     unique_id = '221.123.32.13'
#     attribute_id = 3232636
#     adversary = ti.write.adversary(None, id=unique_id)
#     response = adversary.delete_attribute(attribute_id)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_5():
#     unique_id = '221.123.32.13'
#     adversary = ti.write.adversary(None, id=unique_id)
#     response = adversary.label('TLP:AMBER')
#     print(response)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_6():
#     unique_id = '221.123.32.13'
#     adversary = ti.write.adversary(None, id=unique_id)
#     response = adversary.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_adversary_delete_0():
#     unique_id = '221.123.32.13'
#     adversary = ti.write.adversary(None, id=unique_id)
#     response = adversary.delete()
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_3():
#     adversary_id = 142722
#     adversary = ti.write.adversary(None, id=adversary_id)
#     response = adversary.attribute('Description', 'Test_Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_4():
#     adversary_id = 142722
#     attribute_id = 933455
#     adversary = ti.write.adversary(None, id=adversary_id)
#     response = adversary.delete_attribute(attribute_id)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_5():
#     adversary_id = 142722
#     attribute_id = 933456
#     adversary = ti.write.adversary(None, id=adversary_id)
#     response = adversary.attribute_labels(attribute_id, 'TLP:AMBER')
#     # Returns a 404 if the security label doesnt exist.
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_adversary_update_6():
#     adversary_id = 142722
#     attribute_id = 933456
#     adversary = ti.write.adversary(None, id=adversary_id)
#     response = adversary.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response)
#     assert response.json().get('status') == 'Success'
