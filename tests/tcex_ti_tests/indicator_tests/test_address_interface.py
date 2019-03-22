# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_address_create_0():
#     """Test address creation"""
#     summary = '221.123.32.12'
#     address = ti.write.address(summary)
#     response = address.create('System')
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_address_create_1():
#     """Test address creation"""
#     summary = '221.123.32.13'
#     address = ti.write.address(summary, rating=4, confidence=90)
#     response = address.create('System')
#     assert response.json().get('status') == 'Success'

# def test_address_update_0():
#     """Test address creation"""
#     unique_id = '221.123.32.13'
#     address = ti.write.address(None, id=unique_id, rating=3)
#     response = address.update()
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_address_update_1():
#     """Test adversary creation"""
#     unique_id = '221.123.32.13'
#     address = ti.write.address(None, id=unique_id)
#     response = address.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_address_update_2():
#     unique_id = '221.123.32.13'
#     attribute_id = 3232636
#     address = ti.write.address(None, id=unique_id)
#     response = address.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_address_update_3():
#     unique_id = '221.123.32.13'
#     attribute_id = 3232636
#     address = ti.write.address(None, id=unique_id)
#     response = address.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_address_update_4():
#     unique_id = '221.123.32.13'
#     attribute_id = 3232636
#     address = ti.write.address(None, id=unique_id)
#     response = address.delete_attribute(attribute_id)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_address_update_5():
#     unique_id = '221.123.32.13'
#     address = ti.write.address(None, id=unique_id)
#     response = address.label('TLP:AMBER')
#     print(response)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_address_update_6():
#     unique_id = '221.123.32.13'
#     address = ti.write.address(None, id=unique_id)
#     response = address.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_address_delete_0():
#     unique_id = '221.123.32.13'
#     address = ti.write.address(None, id=unique_id)
#     response = address.delete()
#     assert response.json().get('status') == 'Success'

# def test_address_update_3():
#     address_id = 142722
#     address = ti.write.address(None, id=address_id)
#     response = address.attribute('Description', 'Test_Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_address_update_4():
#     address_id = 142722
#     attribute_id = 933455
#     address = ti.write.address(None, id=address_id)
#     response = address.delete_attribute(attribute_id)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_address_update_5():
#     address_id = 142722
#     attribute_id = 933456
#     address = ti.write.address(None, id=address_id)
#     response = address.attribute_labels(attribute_id, 'TLP:AMBER')
#     # Returns a 404 if the security label doesnt exist.
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_address_update_6():
#     address_id = 142722
#     attribute_id = 933456
#     address = ti.write.address(None, id=address_id)
#     response = address.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response)
#     assert response.json().get('status') == 'Success'
