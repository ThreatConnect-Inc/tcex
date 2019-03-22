# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_document_create_0():
#     """Test document creation"""
#     summary = 'document1'
#     file_name = 'document_file_name.pdf'
#     document = ti.write.document(summary, file_name)
#     response = document.create('System')
#     assert response.json().get('status') == 'Success'

# def test_document_create_1():
#     """Test document creation"""
#     summary = 'document3'
#     file_name = 'document_file_name.txt'
#     document = ti.write.document(summary, file_name)
#     response = document.create('System')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_document_update_0():
#     """Test document creation"""
#     unique_id = '142736'
#     document = ti.write.document(None, None, unique_id=unique_id)
#     file_content =  'IyEvYmluL2Jhc2gKCmNkIFVzZXJzL2JwdXJkeS1hZC9wcm9qZWN0cy90aHJlYXR' \
#                     'jb25uZWN0LWluc3RhbGxlci90aHJlYXRjb25uZWN0L2FwcApteXNxbCAtdSByb2' \
#                     '90IC1wIHBhc3N3b3JkIHRocmVhdGNvbm5lY3QgPCAnREVMRVRFIEZST00gYHRoc' \
#                     'mVhdGNvbm5lY3RgLmBsaWNlbnNlYDsnCi4vc2V0dXAuc2ggPCB+L0RvY3VtZW50' \
#                     'cy9mdWxsX3NlcnZlcl9pbnB1dC50eHQgIApjcCAuLi90aHJlYXRjb25uZWN0Lnh' \
#                     'tbCB+L0Rvd25sb2Fkcy9lYXAvc3RhbmRhbG9uZS9jb25maWd1cmF0aW9uLwpzdG' \
#                     'FydF9qYm9zcwpzbGVlcCAzMAppZiBbIC1lIH4vRG93bmxvYWRzL2VhcC9zdGFuZ' \
#                     'GFsb25lL2RlcGxveW1lbnRzL3RocmVhdGNvbm5lY3QuZWFyIF07IHRoZW4KICAg' \
#                     'IGVjaG8gIkZ1bGwgZGVwbG95bWVudCBzdWNjZXNzZnVsIgplbHNlCiAgZWNobyA' \
#                     'iRnVsbCBkZXBsb3ltZW50IHVuc3VjY2Vzc2Z1bCIKICBleGl0IDEKZmkKCg=='
#     response = document.file_content(file_content)
#     assert response.json().get('status') == 'Success'

# def test_document_update_1():
#     """Test document creation"""
#     unique_id = '142736'
#     document = ti.write.document(None, unique_id=unique_id)
#     response = document.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_document_update_2():
#     unique_id = '142736'
#     attribute_id = 933459
#     document = ti.write.document(None, unique_id=unique_id)
#     response = document.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_document_update_3():
#     unique_id = '142736'
#     attribute_id = 933459
#     document = ti.write.document(None, unique_id=unique_id)
#     response = document.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_document_update_4():
#     unique_id = '142736'
#     attribute_id = 933459
#     document = ti.write.document(None, unique_id=unique_id)
#     response = document.delete_attribute(attribute_id)
#     assert response.json().get('status') == 'Success'

# def test_document_update_5():
#     unique_id = '142736'
#     document = ti.write.document(None, unique_id=unique_id)
#     response = document.label('TLP:AMBER')
#     print(response)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_document_update_6():
#     unique_id = '142736'
#     document = ti.write.document(None, unique_id=unique_id)
#     response = document.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_document_delete_0():
#     unique_id = '142736'
#     document = ti.write.document(None, unique_id=unique_id)
#     response = document.delete()
#     assert response.json().get('status') == 'Success'
