# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_file_create_0():
#     """Test file creation"""
#     md5 = 'E5B902F68A0EBBD0502C4F9677CB2EDB'
#     file = ti.write.file(md5=md5)
#     response = file.create('System')
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_file_create_1():
#     """Test file creation"""
#     md5 = 'E5B902F68A0EBBD0502C4F9677CB2EDC'
#     sha256 = 'FA2242E1421DA17E02FC7B2B5C9C9ACD0423686380C18CF06628EAE0AA755517'
#     file = ti.write.file(md5=md5, sha256=sha256, rating=4)
#     response = file.create('System')
#     assert response.json().get('status') == 'Success'

# def test_file_update_0():
#     """Test file creation"""
#     sha256 = 'FA2242E1421DA17E02FC7B2B5C9C9ACD0423686380C18CF06628EAE0AA755517'
#     file = ti.write.file(unique_id=sha256, rating=3)
#     response = file.update()
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_file_update_1():
#     sha256 = 'FA2242E1421DA17E02FC7B2B5C9C9ACD0423686380C18CF06628EAE0AA755517'
#     file = ti.write.file(unique_id=sha256)
#     response = file.attribute('Description', 'Test Description')
#     assert response.json().get('status') == 'Success'

# def test_file_update_2():
#     sha256 = 'FA2242E1421DA17E02FC7B2B5C9C9ACD0423686380C18CF06628EAE0AA755517'
#     file = ti.write.file(unique_id=sha256)
#     attribute_id = 3232637
#     response = file.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_file_update_3():
#     sha256 = 'FA2242E1421DA17E02FC7B2B5C9C9ACD0423686380C18CF06628EAE0AA755517'
#     file = ti.write.file(unique_id=sha256)
#     attribute_id = 3232637
#     response = file.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_file_update_4():
#     sha256 = 'FA2242E1421DA17E02FC7B2B5C9C9ACD0423686380C18CF06628EAE0AA755517'
#     file = ti.write.file(unique_id=sha256)
#     attribute_id = 3232637
#     response = file.delete_attribute(attribute_id)
#     assert response.json().get('status') == 'Success'

# def test_file_update_5():
#     sha256 = 'FA2242E1421DA17E02FC7B2B5C9C9ACD0423686380C18CF06628EAE0AA755517'
#     file = ti.write.file(unique_id=sha256)
#     response = file.label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_file_update_6():
#     sha256 = 'FA2242E1421DA17E02FC7B2B5C9C9ACD0423686380C18CF06628EAE0AA755517'
#     file = ti.write.file(unique_id=sha256)
#     response = file.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

def test_file_delete_0():
    sha256 = 'FA2242E1421DA17E02FC7B2B5C9C9ACD0423686380C18CF06628EAE0AA755517'
    file = ti.write.file(unique_id=sha256)
    response = file.delete()
    assert response.json().get('status') == 'Success'
