# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_url_create_0():
#     """Test url creation"""
#     summary = 'https://createurl0.com'
#     url = ti.write.url(summary)
#     response = url.create('System')
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_url_create_1():
#     """Test url creation"""
#     summary = 'https://createurl0.com'
#     url = ti.write.url(summary, rating=3, confidence=80)
#     response = url.create('System')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_url_update_0():
#     """Test url creation"""
#     unique_id = 'https://createurl0.com'
#     url = ti.write.url(None, unique_id=unique_id)
#     response = url.rating(4)
#     assert response.json().get('status') == 'Success'

# def test_url_update_1():
#     unique_id = 'https://createurl0.com'
#     url = ti.write.url(None, unique_id=unique_id)
#     response = url.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_url_update_2():
#     unique_id = 'https://createurl0.com'
#     attribute_id = 3232639
#     url = ti.write.url(None, unique_id=unique_id)
#     response = url.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_url_update_3():
#     unique_id = 'https://createurl0.com'
#     attribute_id = 3232638
#     url = ti.write.url(None, unique_id=unique_id)
#     response = url.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_url_update_4():
#     unique_id = 'createurl1.com'
#     url = ti.write.url(None, unique_id=unique_id)
#     attribute_id = 3232638
#     response = url.delete_attribute(attribute_id)
#     assert response.json().get('status') == 'Success'

# def test_url_update_5():
#     unique_id = 'https://createurl0.com'
#     url = ti.write.url(None, unique_id=unique_id)
#     response = url.label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_url_update_6():
#     unique_id = 'https://createurl0.com'
#     url = ti.write.url(None, unique_id=unique_id)
#     response = url.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_url_delete_0():
#     unique_id = 'https://createurl0.com'
#     url = ti.write.url(None, unique_id=unique_id)
#     response = url.delete()
#     assert response.json().get('status') == 'Success'
