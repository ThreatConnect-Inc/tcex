# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_custom_indicator_type_create_0():
#     """Test custom_indicator_type creation"""
#     value1 = 'AAAAAAAAAABAAAAAAAAAAAAAAAAAAA'
#     value2 = 'AAAAAAAAAABAAAAAAAAAAAAAAAAAAABBBBBBBBBB'
#     value3 = 'AAAAAAAAAABAAAAAAAAAAAAAAAAAAABBBBBBBBBBAAAAAAAAAAAAAAAAAAAAAAAA'
#     custom_indicator_type = ti.write.custom_indicator_type(value1, value2, value3)
#     response = custom_indicator_type.create('System')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_create_1():
#     """Test custom_indicator_type creation"""
#     value1 = 'AAAAAAAAAABAAAAAAAAAAAAAAAAAAA'
#     value2 = 'AAAAAAAAAABAABAAAAAAAAAAAAAAAABBBBBBBBBB'
#     value3 = 'AAAAAAAAAABAAAAAAAAAABAAAAAAAABBBBBBBBBBAAAAAAAAAAAAAAAAAAAAAAAA'
#     custom_indicator_type = ti.write.custom_indicator_type(value1, value2, value3, rating=4, confidence=90)
#     response = custom_indicator_type.create('System')
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_0():
#     """Test custom_indicator_type creation"""
#     unique_id = 'AAAAAAAAAABAAAAAAAAAAAAAAAAAAA : AAAAAAAAAABAABAAAAAAAAAAAAAAAABBBBBBBBBB : AAAAAAAAAABAAAAAAAAAABAAAAAAAABBBBBBBBBBAAAAAAAAAAAAAAAAAAAAAAAA'
#     custom_indicator_type = ti.write.custom_indicator_type(None, None, None, id=unique_id, rating=3)
#     response = custom_indicator_type.update()
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_1():
#     """Test adversary creation"""
#     unique_id = '221.123.32.13'
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=unique_id)
#     response = custom_indicator_type.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_2():
#     unique_id = '221.123.32.13'
#     attribute_id = 3232636
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=unique_id)
#     response = custom_indicator_type.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_3():
#     unique_id = '221.123.32.13'
#     attribute_id = 3232636
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=unique_id)
#     response = custom_indicator_type.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_4():
#     unique_id = '221.123.32.13'
#     attribute_id = 3232636
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=unique_id)
#     response = custom_indicator_type.delete_attribute(attribute_id)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_5():
#     unique_id = '221.123.32.13'
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=unique_id)
#     response = custom_indicator_type.label('TLP:AMBER')
#     print(response)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_6():
#     unique_id = '221.123.32.13'
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=unique_id)
#     response = custom_indicator_type.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_delete_0():
#     unique_id = '221.123.32.13'
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=unique_id)
#     response = custom_indicator_type.delete()
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_3():
#     custom_indicator_type_id = 142722
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=custom_indicator_type_id)
#     response = custom_indicator_type.attribute('Description', 'Test_Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_4():
#     custom_indicator_type_id = 142722
#     attribute_id = 933455
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=custom_indicator_type_id)
#     response = custom_indicator_type.delete_attribute(attribute_id)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_5():
#     custom_indicator_type_id = 142722
#     attribute_id = 933456
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=custom_indicator_type_id)
#     response = custom_indicator_type.attribute_labels(attribute_id, 'TLP:AMBER')
#     # Returns a 404 if the security label doesnt exist.
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_custom_indicator_type_update_6():
#     custom_indicator_type_id = 142722
#     attribute_id = 933456
#     custom_indicator_type = ti.write.custom_indicator_type(None, id=custom_indicator_type_id)
#     response = custom_indicator_type.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response)
#     assert response.json().get('status') == 'Success'

