# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_host_create_0():
#     """Test host creation"""
#     summary = 'createhost0.com'
#     host = ti.write.host(summary)
#     response = host.create('System')
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_host_create_1():
#     """Test host creation"""
#     summary = 'createhost1.com'
#     host = ti.write.host(summary, rating=3, confidence=80)
#     response = host.create('System')
#     assert response.json().get('status') == 'Success'

# def test_host_update_0():
#     """Test host creation"""
#     unique_id = 'createhost1.com'
#     host = ti.write.host(None, unique_id=unique_id, rating=3)
#     response = host.update()
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_host_update_1():
#     unique_id = 'createhost1.com'
#     host = ti.write.host(None, unique_id=unique_id)
#     response = host.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_host_update_2():
#     unique_id = 'createhost1.com'
#     attribute_id = 3232638
#     host = ti.write.host(None, unique_id=unique_id)
#     response = host.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_host_update_3():
#     unique_id = 'createhost1.com'
#     attribute_id = 3232638
#     host = ti.write.host(None, unique_id=unique_id)
#     response = host.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_host_update_4():
#     unique_id = 'createhost1.com'
#     host = ti.write.host(None, unique_id=unique_id)
#     attribute_id = 3232638
#     response = host.delete_attribute(attribute_id)
#     assert response.json().get('status') == 'Success'

# def test_host_update_5():
#     unique_id = 'createhost1.com'
#     host = ti.write.host(None, unique_id=unique_id)
#     response = host.label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_host_update_6():
#     unique_id = 'createhost1.com'
#     host = ti.write.host(None, unique_id=unique_id)
#     response = host.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_host_delete_0():
#     unique_id = 'createhost1.com'
#     host = ti.write.host(None, unique_id=unique_id)
#     response = host.delete()
#     assert response.json().get('status') == 'Success'
