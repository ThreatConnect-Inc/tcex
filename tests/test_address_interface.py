# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_address_get_0():
#     """Test address creation"""
#     unique_id = '221.123.32.12'
#     address = ti.read.address('System', unique_id=unique_id)
#     response = address.single()
#     print(response)
#     assert response.json().get('status') == 'Success'


def test_address_create_1():
    """Test address creation"""
    # group_name = 'document_1'
    # group_type = 'Document'
    unique_id = 761
    kwargs = {'file_name': 'document_filename_1.txt', 'malware': False, 'unique_id': unique_id}
    group = ti.group(name=None, group_type='Adversary', **kwargs)
    for association in group.group_associations_types('Adversary'):
        print(association)
    # print(group.add_attribute('Description', 'Dummy_text'))


# def test_address_update_0():
#     """Test address creation"""
#     unique_id = '221.123.32.14'
#     address = ti.write.address(None, unique_id=unique_id, rating=3)
#     response = address.update()
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_address_update_1():
#     """Test adversary creation"""
#     unique_id = '221.123.32.14'
#     address = ti.write.address(None, unique_id=unique_id)
#     response = address.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_address_update_2():
#     unique_id = '221.123.32.14'
#     attribute_id = 3232641
#     address = ti.write.address(None, unique_id=unique_id)
#     response = address.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_address_update_3():
#     unique_id = '221.123.32.13'
#     attribute_id = 3232641
#     address = ti.write.address(None, id=unique_id)
#     response = address.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_address_update_4():
#     unique_id = '221.123.32.14'
#     attribute_id = 3232641
#     address = ti.write.address(None, unique_id=unique_id)
#     response = address.delete_attribute(attribute_id)
#     assert response.json().get('status') == 'Success'

# def test_address_update_5():
#     unique_id = '221.123.32.14'
#     address = ti.write.address(None, unique_id=unique_id)
#     response = address.label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_address_update_6():
#     unique_id = '221.123.32.14'
#     address = ti.write.address(None, unique_id=unique_id)
#     response = address.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'


# def test_address_update_6():
#     unique_id = '221.123.32.14'
#     address = ti.write.address(None, unique_id=unique_id)
#     response = address.create_tag('new_tag_1')
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_address_update_6():
#     unique_id = '221.123.32.14'
#     address = ti.write.address(None, unique_id=unique_id)
#     response = address.delete_tag('new_tag_1')
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_address_delete_0():
#     unique_id = '221.123.32.14'
#     address = ti.write.address(None, unique_id=unique_id)
#     response = address.delete()
#     assert response.json().get('status') == 'Success'
