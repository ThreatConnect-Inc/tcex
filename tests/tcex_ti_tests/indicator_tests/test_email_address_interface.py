# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_email_address_create_0():
#     """Test email_address creation"""
#     summary = 'test_email@gmail.com'
#     email_address = ti.write.email_address(summary)
#     response = email_address.create('System')
#     assert response.json().get('status') == 'Success'

# def test_email_address_create_1():
#     """Test email_address creation"""
#     summary = 'test_email_1@gmail.com'
#     email_address = ti.write.email_address(summary, rating=4, confidence=90)
#     response = email_address.create('System')
#     assert response.json().get('status') == 'Success'

# def test_email_address_update_0():
#     """Test email_address creation"""
#     unique_id = 'test_email_1@gmail.com'
#     email_address = ti.write.email_address(None, id=unique_id, rating=3)
#     response = email_address.update()
#     assert response.json().get('status') == 'Success'

# def test_email_address_update_1():
#     """Test adversary creation"""
#     unique_id = 'test_email_1@gmail.com'
#     email_address = ti.write.email_address(None, id=unique_id)
#     response = email_address.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_email_address_update_2():
#     unique_id = 'test_email_1@gmail.com'
#     attribute_id = 3232636
#     email_address = ti.write.email_address(None, id=unique_id)
#     response = email_address.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_email_address_update_3():
#     unique_id = 'test_email_1@gmail.com'
#     attribute_id = 3232636
#     email_address = ti.write.email_address(None, id=unique_id)
#     response = email_address.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_email_address_update_4():
#     unique_id = 'test_email_1@gmail.com'
#     attribute_id = 3232636
#     email_address = ti.write.email_address(None, id=unique_id)
#     response = email_address.delete_attribute(attribute_id)
#     assert response.json().get('status') == 'Success'

# def test_email_address_update_5():
#     unique_id = 'test_email_1@gmail.com'
#     email_address = ti.write.email_address(None, id=unique_id)
#     response = email_address.label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_email_address_update_6():
#     unique_id = 'test_email_1@gmail.com'
#     email_address = ti.write.email_address(None, id=unique_id)
#     response = email_address.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_email_address_delete_0():
#     unique_id = 'test_email_1@gmail.com'
#     email_address = ti.write.email_address(None, id=unique_id)
#     response = email_address.delete()
#     assert response.json().get('status') == 'Success'
